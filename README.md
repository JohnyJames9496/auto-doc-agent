# Auto-Doc Agent

AI-powered automatic documentation generator for VS Code — generates hover tooltips as you write code.

![VS Code Extension](https://img.shields.io/badge/VS%20Code-Extension-blue)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Live Links

| Service | URL |
|---|---|
| VS Code Extension | [marketplace.visualstudio.com](https://marketplace.visualstudio.com/items?itemName=JohnyJames.auto-doc-agent) |
| Backend API | [auto-doc-agent.onrender.com](https://auto-doc-agent.onrender.com) |
| Dashboard | [auto-doc-agent.onrender.com/dashboard](https://auto-doc-agent.onrender.com/dashboard) |
| Docs Site | [auto-doc-agent.vercel.app](https://auto-doc-agent.vercel.app) |

---

## What It Does

Auto-Doc Agent watches your code as you write it and automatically generates documentation using Google Gemini AI. Documentation appears as hover tooltips in VS Code — zero effort required.

---

## Features

- Uses Google Gemini 2.5 Flash to generate smart documentation
- Generates hover tooltips as you write code
- Supports Python, TypeScript and JavaScript
- LangGraph pipeline with intelligent retry logic
- Two-layer cache — Redis + PostgreSQL for fast retrieval
- Each user sees only their own projects
- Prometheus metrics exposed at `/metrics`
- Automated testing and deployment via GitHub Actions

---

## Architecture

| Component | Technology | Purpose |
|---|---|---|
| VS Code Extension | TypeScript, Axios | Detects code changes, shows tooltips |
| Backend API | FastAPI, Python | Handles requests, auth, queuing |
| Task Queue | Celery, Redis | Async AI documentation generation |
| AI Agent | LangGraph, Gemini | Generates structured documentation |
| Database | PostgreSQL | Permanent documentation storage |
| Cache | Redis (Upstash) | Fast documentation retrieval |
| Auth | API Keys | Permanent, never-expiring keys |
| Docs Site | Docusaurus, Vercel | Public API documentation |
| Monitoring | Prometheus, Grafana | Metrics and dashboards |
| CI/CD | GitHub Actions | Lint, test, deploy |

---

## Setup

**1. Install the VS Code Extension**

Search **Auto-Doc Agent** in the VS Code Marketplace and click Install.

**2. Get Your API Key**

Go to [auto-doc-agent.onrender.com](https://auto-doc-agent.onrender.com), register or login, and copy your API key — starts with `autodoc_...`

**3. Configure VS Code**

Press `Ctrl+Shift+P` → **Open User Settings (JSON)** and add:

    {
      "autoDocAgent.apiUrl": "https://auto-doc-agent.onrender.com",
      "autoDocAgent.apiKey": "autodoc_your_key_here"
    }

**4. Reload VS Code**

Press `Ctrl+Shift+P` → **Reload Window**

**5. Write Code**

Open any `.py`, `.ts` or `.js` file, write a function, wait 3 seconds, hover over the function name.

---

## Dashboard

Browse all your documented functions at [auto-doc-agent.onrender.com/dashboard](https://auto-doc-agent.onrender.com/dashboard)

- Projects organized by workspace folder name
- Each file and function listed in the sidebar
- Documentation updates automatically as you code
- Private — each user sees only their own projects

---

## Extension Settings

| Setting | Default | Description |
|---|---|---|
| `autoDocAgent.apiUrl` | `https://auto-doc-agent.onrender.com` | Backend API URL |
| `autoDocAgent.apiKey` | `""` | Your API key |
| `autoDocAgent.enabled` | `true` | Enable or disable |
| `autoDocAgent.debounceMs` | `3000` | Wait time after typing stops (ms) |

---

## API Reference

Full docs at [auto-doc-agent.vercel.app](https://auto-doc-agent.vercel.app)

All endpoints require:

    Authorization: Bearer autodoc_your_key_here

Endpoints:

    POST /auth/register                       — Register and get API key
    POST /auth/login                          — Login and get API key
    POST /api/v1/documentation                — Request documentation
    GET  /api/v1/documentation/task/{id}      — Check task status
    GET  /api/v1/projects                     — List your projects
    GET  /api/v1/documentation/{project_id}   — Get project docs
    GET  /health                              — Health check
    GET  /metrics                             — Prometheus metrics

---

## Running Tests

    uv sync
    uv run pytest backend/tests/ -v --cov=backend
    uv run ruff check backend/

---

## Self-Hosting

Environment variables needed:

    DATABASE_URL=postgresql://user:pass@host:5432/db
    DATABASE_URL_DIRECT=postgresql://user:pass@host:5432/db
    REDIS_URL=rediss://default:pass@host:6379
    CELERY_BROKER_URL=rediss://default:pass@host:6379
    GEMINI_API_KEY=your_gemini_key
    JWT_SECRET=your_secret
    JWT_ALGORITHM=HS256
    JWT_EXPIRY_MINUTES=60

Run locally:

    git clone https://github.com/JohnyJames9496/auto-doc-agent
    cd auto-doc-agent
    pip install uv
    uv sync
    bash start.sh

---

## Monitoring

Prometheus metrics at `/metrics`:

| Metric | Description |
|---|---|
| `autodoc_cache_hits_total` | Total Redis cache hits |
| `autodoc_cache_misses_total` | Total Redis cache misses |
| `autodoc_generation_duration_seconds` | AI generation time |
| `autodoc_active_celery_tasks` | Currently active tasks |

---

## CI/CD Pipeline

Every push to `main` triggers lint, tests, backend deploy to Render, and docs deploy to Vercel.

---

## Project Structure

    auto-doc-agent/
    ├── backend/
    │   ├── app/
    │   │   ├── agent/           — LangGraph AI pipeline
    │   │   ├── api/             — FastAPI endpoints
    │   │   ├── auth/            — Authentication
    │   │   ├── cache/           — Redis client
    │   │   ├── db/              — Database models
    │   │   ├── queue/           — Celery tasks
    │   │   ├── templates/       — HTML pages
    │   │   └── main.py          — FastAPI app
    │   └── tests/               — Test suite
    ├── extension/
    │   └── src/
    │       ├── apiClient.ts     — Backend communication
    │       ├── codeDetector.ts  — Function detection
    │       ├── hoverProvider.ts — Tooltip display
    │       └── extension.ts     — Entry point
    ├── docs-site/               — Docusaurus documentation
    ├── monitoring/              — Prometheus config
    ├── .github/workflows/       — CI/CD pipelines
    └── start.sh                 — Production startup script

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `uv run pytest`
5. Push and open a Pull Request

---

## Author

**Johny James** — [github.com/JohnyJames9496](https://github.com/JohnyJames9496)