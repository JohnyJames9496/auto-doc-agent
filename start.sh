#!/bin/bash
celery -A backend.app.queue.celery_app worker -Q docs --loglevel=info --concurrency=2 &
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
