from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from celery.result import AsyncResult
from backend.app.auth.dependencies import get_current_user
from backend.app.cache.redis_client import cache_get, cache_set
from backend.app.queue.celery_app import celery_app
from backend.app.queue.tasks import generate_doc_task
from backend.app.db.session import get_db
from backend.app.db.models import Documentation, Project
from sqlmodel import select
import hashlib
import time
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class DocumentationRequest(BaseModel):
    file_path: str
    function_name: str
    code_snippet: str
    language: str
    project_id: str


class DocumentationResponse(BaseModel):
    function_name: Optional[str] = None
    documentation: Optional[str] = None
    cached: Optional[bool] = None
    generation_time_ms: Optional[float] = None
    task_id: Optional[str] = None
    status: Optional[str] = None


@router.post("/documentation", response_model=DocumentationResponse)
async def request_documentation(
    req: DocumentationRequest,
    current_user: str = Depends(get_current_user),
    db=Depends(get_db),
):
    from backend.app.main import cache_hits, cache_misses

    project_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, req.project_id)
    project_result = await db.execute(select(Project).where(Project.id == project_uuid))
    if not project_result.scalar_one_or_none():
        db.add(
            Project(
                id=project_uuid,
                name=req.project_id,
                owner_id=uuid.UUID(current_user),
            )
        )
        await db.flush()
        logger.info(f"Project created: {project_uuid} owner: {current_user}")
    else:
        logger.info(f"Project exists: {project_uuid}")

    start = time.monotonic()
    code_hash = hashlib.sha256(req.code_snippet.encode()).hexdigest()
    cache_key = f"doc:{code_hash}"

    cached_doc = await cache_get(cache_key)
    if cached_doc:
        cache_hits.inc()
        return DocumentationResponse(
            function_name=req.function_name,
            documentation=cached_doc,
            cached=True,
            generation_time_ms=(time.monotonic() - start) * 1000,
            status="complete",
        )

    cache_misses.inc()

    result = await db.execute(select(Documentation).where(Documentation.code_hash == code_hash))
    existing = result.scalar_one_or_none()
    if existing:
        await cache_set(cache_key, existing.doc_content)
        cache_hits.inc()
        return DocumentationResponse(
            function_name=req.function_name,
            documentation=existing.doc_content,
            cached=True,
            generation_time_ms=(time.monotonic() - start) * 1000,
            status="complete",
        )

    task = generate_doc_task.delay(
        code_snippet=req.code_snippet,
        function_name=req.function_name,
        language=req.language,
        file_path=req.file_path,
        project_id=req.project_id,
        code_hash=code_hash,
    )

    return DocumentationResponse(task_id=task.id, status="queued")


@router.get("/documentation/task/{task_id}", response_model=DocumentationResponse)
async def get_task_result(
    task_id: str,
    current_user: str = Depends(get_current_user),
):
    result = AsyncResult(task_id, app=celery_app)

    if result.ready():
        if result.successful():
            data = result.get()
            return DocumentationResponse(
                function_name=data.get("function_name"),
                documentation=data.get("doc"),
                cached=False,
                status="complete",
            )
        return DocumentationResponse(status="failed")

    return DocumentationResponse(status="pending")


@router.get("/documentation/{project_id}")
async def get_project_documentation(
    project_id: str,
    current_user: str = Depends(get_current_user),
    db=Depends(get_db),
):
    result = await db.execute(select(Documentation).where(Documentation.project_id == project_id))
    docs = result.scalars().all()
    return {
        "documentation": [
            {
                "function_name": d.function_name,
                "file_path": d.file_path,
                "doc_content": d.doc_content,
                "language": d.language,
                "updated_at": str(d.updated_at),
            }
            for d in docs
        ]
    }


@router.get("/projects")
async def get_user_projects(
    current_user: str = Depends(get_current_user),
    db=Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.owner_id == uuid.UUID(current_user)))
    projects = result.scalars().all()
    return {
        "projects": [
            {"id": str(p.id), "name": p.name, "created_at": str(p.created_at)} for p in projects
        ]
    }
