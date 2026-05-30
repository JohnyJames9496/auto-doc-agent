from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager
from backend.app.db.session import create_db_and_tables
from backend.app.auth.router import router as auth_router
from backend.app.api.docs import router as docs_router


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