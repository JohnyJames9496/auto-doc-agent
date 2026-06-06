from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager
from backend.app.db.session import create_db_and_tables, get_db
from backend.app.auth.router import router as auth_router
from backend.app.api.docs import router as docs_router
from backend.app.cache.redis_client import cache_set, cache_get
from sqlalchemy import text
import os


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


@app.get("/dashboard", include_in_schema=False)
async def serve_dashboard():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "dashboard.html")
    return FileResponse(template_path)


@app.get("/health", tags=["health"])
async def health_check(db=Depends(get_db)):
    redis_status = "ok"
    db_status = "ok"

    # Test Redis
    try:
        await cache_set("health_check", "ok", ttl=10)
        value = await cache_get("health_check")
        if value != "ok":
            redis_status = "error"
    except Exception:
        redis_status = "error"

    # Bug #4 fix — test PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    overall = "ok" if redis_status == "ok" and db_status == "ok" else "degraded"

    return {
        "status": overall,
        "app": "Auto-Doc Agent",
        "version": "1.0.0",
        "redis": redis_status,
        "database": db_status,
    }
