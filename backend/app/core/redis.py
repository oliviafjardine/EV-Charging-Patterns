"""
Redis configuration and connection management.
"""

import json
import pickle
from typing import Any, Optional, Union, Dict
import logging
import asyncio

from app.core.config import settings

logger = logging.getLogger(__name__)

# Simple in-memory cache for demo purposes
_memory_cache: Dict[str, Any] = {}


class MockRedisClient:
    """Mock Redis client for demo purposes."""

    async def ping(self):
        return True

    async def get(self, key: str):
        return _memory_cache.get(key)

    async def set(self, key: str, value: Any):
        _memory_cache[key] = value
        return True

    async def setex(self, key: str, ttl: int, value: Any):
        _memory_cache[key] = value
        # In a real implementation, we'd handle TTL
        return True

    async def delete(self, key: str):
        _memory_cache.pop(key, None)
        return True

    async def exists(self, key: str):
        return key in _memory_cache

    async def incrby(self, key: str, amount: int = 1):
        current = _memory_cache.get(key, 0)
        _memory_cache[key] = current + amount
        return _memory_cache[key]

    async def expire(self, key: str, ttl: int):
        return True

    async def keys(self, pattern: str = "*"):
        return list(_memory_cache.keys())

    async def flushall(self):
        _memory_cache.clear()
        return True

    async def close(self):
        pass


# Create Redis client (or mock for demo)
try:
    import redis.asyncio as redis
    redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=False,
        socket_keepalive=True,
        socket_keepalive_options={},
        health_check_interval=30,
    )
except ImportError:
    logger.warning("Redis not available, using in-memory cache")
    redis_client = MockRedisClient()


class RedisCache:
    """Redis cache utility class."""

    def __init__(self, client: redis.Redis):
        self.client = client

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await self.client.get(key)
            if value is None:
                return None

            # Try to deserialize as JSON first, then pickle
            try:
                return json.loads(value.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return pickle.loads(value)
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache."""
        try:
            # Try to serialize as JSON first, then pickle
            try:
                serialized = json.dumps(value).encode('utf-8')
            except (TypeError, ValueError):
                serialized = pickle.dumps(value)

            if ttl:
                return await self.client.setex(key, ttl, serialized)
            else:
                return await self.client.set(key, serialized)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(await self.client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(await self.client.exists(key))
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache."""
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing cache key {key}: {e}")
            return None

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for key."""
        try:
            return await self.client.expire(key, ttl)
        except Exception as e:
            logger.error(f"Error setting expiration for cache key {key}: {e}")
            return False

    async def keys(self, pattern: str = "*") -> list:
        """Get keys matching pattern."""
        try:
            keys = await self.client.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
            logger.error(f"Error getting keys with pattern {pattern}: {e}")
            return []

    async def flush_all(self) -> bool:
        """Flush all keys from cache."""
        try:
            return await self.client.flushall()
        except Exception as e:
            logger.error(f"Error flushing cache: {e}")
            return False


# Create cache instance
cache = RedisCache(redis_client)


async def get_cache_key(prefix: str, *args) -> str:
    """Generate cache key with prefix and arguments."""
    key_parts = [prefix] + [str(arg) for arg in args]
    return ":".join(key_parts)
