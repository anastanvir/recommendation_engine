import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from .config import settings
import json
from typing import Optional, Any, Dict, List
from datetime import timedelta

class RedisManager:
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self):
        """Initialize connection pool"""
        if self._pool is None:
            self._pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_POOL_SIZE,
                decode_responses=True
            )
    
    async def get_client(self) -> redis.Redis:
        """Get Redis client from pool"""
        await self.initialize()
        return redis.Redis(connection_pool=self._pool)
    
    async def close(self):
        """Close all connections"""
        if self._pool:
            await self._pool.disconnect()
    
    # Cache operations
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        client = await self.get_client()
        try:
            value = await client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None
    
    async def cache_set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with TTL"""
        client = await self.get_client()
        try:
            if ttl is None:
                ttl = settings.CACHE_TTL
            await client.setex(key, ttl, json.dumps(value))
            return True
        except Exception:
            return False
    
    async def cache_delete(self, key: str) -> bool:
        """Delete value from cache"""
        client = await self.get_client()
        try:
            await client.delete(key)
            return True
        except Exception:
            return False
    
    # User feature caching
    async def get_user_features(self, user_id: int) -> Optional[Dict]:
        """Get precomputed user features from cache"""
        key = f"user:features:{user_id}"
        return await self.cache_get(key)
    
    async def set_user_features(self, user_id: int, features: Dict, ttl: int = 3600) -> bool:
        """Cache user features for 1 hour"""
        key = f"user:features:{user_id}"
        return await self.cache_set(key, features, ttl)
    
    # Recommendation caching
    async def get_recommendations(self, user_id: int, context_hash: str) -> Optional[List]:
        """Get cached recommendations"""
        key = f"recs:{user_id}:{context_hash}"
        return await self.cache_get(key)
    
    async def set_recommendations(self, user_id: int, context_hash: str, recommendations: List, ttl: int = 3600) -> bool:
        """Cache recommendations"""
        key = f"recs:{user_id}:{context_hash}"
        return await self.cache_set(key, recommendations, ttl)

# Global instance
redis_manager = RedisManager()