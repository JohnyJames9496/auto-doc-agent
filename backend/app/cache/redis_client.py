import redis.asyncio as aioredis
import logging
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
        )
    return _pool


async def cache_get(key: str):
    try:
        client = aioredis.Redis(connection_pool=get_redis_pool())
        value = await client.get(key)
        return value
    except Exception as e:
        logger.warning(f"Redis GET failed: {e}")
        return None


async def cache_set(key: str, value: str, ttl: int = None):
    try:
        client = aioredis.Redis(connection_pool=get_redis_pool())
        ttl = ttl or settings.cache_ttl_seconds
        await client.set(key, value, ex=ttl)
        return True
    except Exception as e:
        logger.warning(f"Redis SET failed: {e}")
        return False


async def cache_invalidate(key: str):
    try:
        client = aioredis.Redis(connection_pool=get_redis_pool())
        await client.delete(key)
    except Exception as e:
        logger.warning(f"Redis DELETE failed: {e}")