from prometheus_client import Counter, Histogram, Gauge

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
doc_generation_total = Counter(
    "autodoc_doc_generation_total",
    "Total documentation generation attempts",
    ["language", "status"],  # labels
)
api_key_auth_total = Counter(
    "autodoc_api_key_auth_total",
    "Total API key authentication attempts",
    ["status"],  # success or failure
)
