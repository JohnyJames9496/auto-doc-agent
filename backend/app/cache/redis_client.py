import redis.asyncio as aioredis
import logging
import ssl
from backend.app.config import settings

logger = logging.getLogger(__name__)

_pool = None


def get_redis_pool():
    global _pool
    if _pool is None:
        _pool = aioredis.ConnectionPool.from_url(
            settings.redis_url,
            max_connections=20,
            decode_responses=True,
            ssl_cert_reqs=ssl.CERT_NONE,  # Bug #4 fix — match tasks.py SSL config
        )
    return _pool


async def cache_get(key: str):
    try:
        client = aioredis.Redis(connection_pool=get_redis_pool())
        value = await client.get(key)
        return value
    except Exception as e:
        logger.warning(f"Redis GET failed for key '{key}': {e}")  # Bug #5 fix
        return None


async def cache_set(key: str, value: str, ttl: int = None):
    try:
        client = aioredis.Redis(connection_pool=get_redis_pool())
        ttl = ttl or settings.cache_ttl_seconds
        await client.set(key, value, ex=ttl)
        return True
    except Exception as e:
        logger.warning(f"Redis SET failed for key '{key}': {e}")  # Bug #5 fix
        return False


async def cache_invalidate(key: str) -> bool:  # Bug #3 fix — return bool
    try:
        client = aioredis.Redis(connection_pool=get_redis_pool())
        deleted = await client.delete(key)
        return deleted > 0
    except Exception as e:
        logger.warning(f"Redis DELETE failed for key '{key}': {e}")  # Bug #5 fix
        return False
