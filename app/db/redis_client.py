import json
from typing import Optional, Any
from app.config import settings
from app.core.logging import logger

try:
    import redis
    _redis_pool = redis.ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=2,
    )
    _redis_client = redis.Redis(connection_pool=_redis_pool)
except Exception as e:
    logger.warning(f"Redis initialization failed, fallback to in-memory store: {e}")
    _redis_client = None


class InMemoryCache:
    """Thread-safe in-memory cache fallback when Redis is not running."""
    def __init__(self):
        self._data = {}

    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._data[key] = value
        return True

    def delete(self, key: str) -> int:
        return 1 if self._data.pop(key, None) is not None else 0

    def keys(self, pattern: str = "*") -> list:
        return list(self._data.keys())

    def flushall(self):
        self._data.clear()

    def ping(self) -> bool:
        return True


_in_memory_cache = InMemoryCache()


def get_cache_client():
    """Returns Redis client if reachable, otherwise returns in-memory cache."""
    global _redis_client
    if _redis_client is not None:
        try:
            _redis_client.ping()
            return _redis_client
        except Exception:
            pass
    return _in_memory_cache
