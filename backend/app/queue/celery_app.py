from celery import Celery
from backend.app.config import settings

celery_app = Celery(
    "autodoc",
    broker=settings.celery_broker_url,
    backend=settings.redis_url,
    include=["backend.app.queue.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_soft_time_limit=25,
    task_time_limit=30,
)