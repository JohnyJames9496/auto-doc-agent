from backend.app.queue.celery_app import celery_app
from backend.app.agent.graph import generate_documentation
import asyncio
import logging

logger = logging.getLogger(__name__)


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

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def save():
        from backend.app.cache.redis_client import cache_set
        await cache_set(f"doc:{code_hash}", doc_markdown)

    loop.run_until_complete(save())
    loop.close()

    from backend.app.db.session import SyncSessionLocal
    from sqlmodel import Session, select
    from backend.app.db.models import Documentation
    import hashlib
    from datetime import datetime

    with Session(SyncSessionLocal()) as db:
        existing = db.exec(
            select(Documentation).where(Documentation.code_hash == code_hash)
        ).first()

        if existing:
            existing.doc_content = doc_markdown
            existing.updated_at = datetime.utcnow()
            db.add(existing)
        else:
            doc = Documentation(
                project_id=project_id,
                file_path=file_path,
                function_name=function_name,
                code_hash=code_hash,
                doc_content=doc_markdown,
                language=language,
            )
            db.add(doc)
        db.commit()

    return {"status": "success", "function_name": function_name, "doc": doc_markdown}