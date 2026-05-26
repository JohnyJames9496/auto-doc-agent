from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title = "Auto-Doc Agent API",
    description = "AI-powered automatic documentation system",
    version = "1.0.0",
    docs_url = "/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "vscode-webview://*",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

Instrumentator().instrument(app).expose(app)

@app.get("/health")
async def health_check():
    return {
        "status":"ok",
        "app":"Auto-Doc Agent",
        "version":"1.0.0"
    }