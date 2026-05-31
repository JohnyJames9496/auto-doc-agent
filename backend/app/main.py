from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge
from contextlib import asynccontextmanager
from backend.app.db.session import create_db_and_tables
from backend.app.auth.router import router as auth_router
from backend.app.api.docs import router as docs_router
import os

cache_hits = Counter(
    "autodoc_cache_hits_total",
    "Total Redis cache hits",
)

cache_misses = Counter(
    "autodoc_cache_misses_total",
    "Total Redis cache misses",
)

doc_generation_duration = Histogram(
    "autodoc_generation_duration_seconds",
    "Documentation generation time in seconds",
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
)

active_tasks = Gauge(
    "autodoc_active_celery_tasks",
    "Number of currently active Celery tasks",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(
    title="Auto-Doc Agent API",
    version="1.0.0",
    docs_url="/api/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(docs_router, prefix="/api/v1", tags=["docs"])


@app.get("/", include_in_schema=False)
async def serve_login_page():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    return FileResponse(template_path)


@app.get("/health", tags=["health"])
async def health_check():
    from backend.app.cache.redis_client import cache_set, cache_get

    redis_status = "ok"
    try:
        await cache_set("health_check", "ok", ttl=10)
        value = await cache_get("health_check")
        if value != "ok":
            redis_status = "error"
    except Exception:
        redis_status = "error"

    return {
        "status": "ok",
        "app": "Auto-Doc Agent",
        "version": "1.0.0",
        "redis": redis_status,
    }
