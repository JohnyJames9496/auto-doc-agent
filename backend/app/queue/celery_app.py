from celery import Celery
from backend.app.config import settings
import ssl

broker_url = settings.celery_broker_url
backend_url = settings.redis_url

celery_app = Celery(
    "autodoc",
    broker=broker_url,
    backend=backend_url,
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
    broker_transport_options={
        "visibility_timeout": 3600,
        "ssl_cert_reqs": ssl.CERT_NONE,
    },
    redis_backend_transport_options={
        "ssl_cert_reqs": ssl.CERT_NONE,
    },
    broker_use_ssl={
        "ssl_cert_reqs": ssl.CERT_NONE,
        "ssl_check_hostname": False,
    },
    redis_backend_use_ssl={
        "ssl_cert_reqs": ssl.CERT_NONE,
        "ssl_check_hostname": False,
    },
)