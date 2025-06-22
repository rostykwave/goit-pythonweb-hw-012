import json
import pickle
from typing import Optional, Any
import redis.asyncio as redis
from src.conf.config import config
import hashlib

class CacheService:
    """Service for Redis caching operations."""
    
    def __init__(self):
        self.redis_client = None
    
    async def get_redis_client(self) -> redis.Redis:
        """Get Redis client instance."""
        if not self.redis_client:
            self.redis_client = redis.from_url(
                config.REDIS_URL,
                password=config.REDIS_PASSWORD,
                decode_responses=False
            )
        return self.redis_client
    
    def _sanitize_user_data(self, user_data: dict) -> dict:
        """Remove sensitive data before caching."""
        sanitized = user_data.copy()
        sensitive_fields = ['password', 'hashed_password', 'refresh_token']
        for field in sensitive_fields:
            sanitized.pop(field, None)
        return sanitized
    
    def _generate_cache_key(self, user_key: str) -> str:
        """Generate secure cache key."""
        key_hash = hashlib.sha256(user_key.encode()).hexdigest()[:8]
        return f"user:{user_key}:{key_hash}"
    
    async def get_user(self, user_key: str) -> Optional[dict]:
        """Get user from cache."""
        try:
            client = await self.get_redis_client()
            cache_key = self._generate_cache_key(user_key)
            cached_user = await client.get(cache_key)
            if cached_user:
                return pickle.loads(cached_user)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set_user(self, user_key: str, user_data: dict, expire: int = None) -> bool:
        """Set user in cache with security sanitization."""
        try:
            client = await self.get_redis_client()

            safe_user_data = self._sanitize_user_data(user_data)
            expire_time = expire or config.CACHE_EXPIRE_TIME
            serialized_user = pickle.dumps(safe_user_data)
            cache_key = self._generate_cache_key(user_key)
            await client.setex(cache_key, expire_time, serialized_user)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete_user(self, user_key: str) -> bool:
        """Delete user from cache."""
        try:
            client = await self.get_redis_client()
            cache_key = self._generate_cache_key(user_key)
            await client.delete(cache_key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def invalidate_user_cache(self, user_key: str) -> bool:
        """Invalidate user cache (alias for delete_user)."""
        return await self.delete_user(user_key)
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()

cache_service = CacheService()