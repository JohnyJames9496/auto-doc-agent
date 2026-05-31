from backend.app.queue.celery_app import celery_app
from backend.app.agent.graph import generate_documentation
from backend.app.config import settings
from uuid import UUID
import redis
import ssl
import logging

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

    doc_markdown = generate_documentation(
        code=code_snippet,
        function_name=function_name,
        language=language,
    )

    try:
        sync_redis.set(
            f"doc:{code_hash}",
            doc_markdown,
            ex=settings.cache_ttl_seconds,
        )
    except Exception as e:
        logger.warning(f"Redis cache save failed: {e}")

    try:
        from sqlmodel import Session, select
        from backend.app.db.session import sync_engine
        from backend.app.db.models import Documentation
        from datetime import datetime

        project_uuid = UUID(project_id) if not isinstance(project_id, UUID) else project_id

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
        logger.warning(f"Database save failed: {e}")

    return {
        "status": "success",
        "function_name": function_name,
        "doc": doc_markdown,
    }
