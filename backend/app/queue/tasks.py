from backend.app.queue.celery_app import celery_app
from backend.app.agent.graph import generate_documentation
from backend.app.config import settings
from backend.app.db.session import sync_engine
from backend.app.db.models import Documentation
from backend.app.metrics import doc_generation_duration, active_tasks, doc_generation_total
from sqlmodel import Session, select
from datetime import datetime
import uuid as uuid_module
import redis
import ssl
import logging
import time

logger = logging.getLogger(__name__)

sync_redis = redis.Redis.from_url(
    settings.redis_url,
    decode_responses=True,
    ssl_cert_reqs=ssl.CERT_NONE,
)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=2,
    retry_kwargs={"max_retries": 3},
    name="backend.app.queue.tasks.generate_doc_task",
)
def generate_doc_task(
    self,
    code_snippet: str,
    function_name: str,
    language: str,
    file_path: str,
    project_id: str,
    code_hash: str,
):
    logger.info(f"Generating docs for {function_name} in {file_path}")

    active_tasks.inc()
    doc_generation_total.labels(language=language, status="started").inc()
    start = time.monotonic()

    try:
        doc_markdown = generate_documentation(
            code=code_snippet,
            function_name=function_name,
            language=language,
        )

        duration = time.monotonic() - start
        doc_generation_duration.observe(duration)

        if not doc_markdown or len(doc_markdown.strip()) < 20:
            logger.error(f"Invalid AI output for {function_name}: '{doc_markdown}'")
            raise ValueError(f"Invalid documentation generated for {function_name}")

        doc_generation_total.labels(language=language, status="success").inc()

        try:
            sync_redis.set(
                f"doc:{code_hash}",
                doc_markdown,
                ex=settings.cache_ttl_seconds,
            )
        except Exception as e:
            logger.warning(
                f"Redis cache save failed for {function_name} (hash: {code_hash[:8]}...): {e}"
            )

        try:
            project_uuid = uuid_module.uuid5(uuid_module.NAMESPACE_DNS, project_id)

            with Session(sync_engine) as db:
                existing = db.exec(
                    select(Documentation).where(Documentation.code_hash == code_hash)
                ).first()

                if existing:
                    existing.doc_content = doc_markdown
                    existing.updated_at = datetime.utcnow()
                    db.add(existing)
                else:
                    doc = Documentation(
                        project_id=project_uuid,
                        file_path=file_path,
                        function_name=function_name,
                        code_hash=code_hash,
                        doc_content=doc_markdown,
                        language=language,
                    )
                    db.add(doc)
                db.commit()

        except Exception as e:
            logger.error(f"Database save failed for {function_name}: {e}")
            doc_generation_total.labels(language=language, status="db_failed").inc()
            raise

        return {
            "status": "success",
            "function_name": function_name,
            "doc": doc_markdown,
        }

    except Exception:
        doc_generation_total.labels(language=language, status="failed").inc()
        raise

    finally:
        active_tasks.dec()
