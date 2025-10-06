import redis.asyncio as redis
import os
import json
import hashlib
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_client = None
        self.redis_url = self._get_redis_url()
    
    def _get_redis_url(self):
        """Build Redis connection URL from environment variables"""
        host = os.getenv("REDIS_HOST", "redis")
        port = os.getenv("REDIS_PORT", "6379")
        password = os.getenv("REDIS_PASSWORD", "")
        db = os.getenv("REDIS_DB", "0")
        
        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        else:
            return f"redis://{host}:{port}/{db}"
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")
    
    async def health_check(self):
        """Check Redis health"""
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            raise
    
    # Session management
    async def store_session(self, session_id: str, user_id: str, expires_in: int = 86400):
        """Store user session"""
        try:
            session_data = {
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
            }
            await self.redis_client.setex(
                f"session:{session_id}",
                expires_in,
                json.dumps(session_data)
            )
            logger.info(f"Session stored for user {user_id}")
        except Exception as e:
            logger.error(f"Error storing session {session_id}: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user session"""
        try:
            session_data = await self.redis_client.get(f"session:{session_id}")
            if session_data:
                return json.loads(session_data)
            return None
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    async def delete_session(self, session_id: str):
        """Delete user session"""
        try:
            await self.redis_client.delete(f"session:{session_id}")
            logger.info(f"Session {session_id} deleted")
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
    
    # AI response caching
    def hash_prompt(self, prompt: str, model: str = "", max_tokens: int = 0, temperature: float = 0.0) -> str:
        """Create a hash for AI prompt caching"""
        cache_key = f"{prompt}:{model}:{max_tokens}:{temperature}"
        return hashlib.sha256(cache_key.encode()).hexdigest()
    
    async def cache_ai_response(self, prompt_hash: str, response_data: Dict[str, Any], ttl: int = 3600):
        """Cache AI response"""
        try:
            cache_data = {
                "content": response_data.get("content", ""),
                "model": response_data.get("model", ""),
                "usage": response_data.get("usage", {}),
                "cached_at": datetime.utcnow().isoformat()
            }
            await self.redis_client.setex(
                f"ai_cache:{prompt_hash}",
                ttl,
                json.dumps(cache_data)
            )
            logger.debug(f"AI response cached with hash {prompt_hash}")
        except Exception as e:
            logger.error(f"Error caching AI response {prompt_hash}: {e}")
    
    async def get_cached_ai_response(self, prompt_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached AI response"""
        try:
            cached_data = await self.redis_client.get(f"ai_cache:{prompt_hash}")
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Error getting cached AI response {prompt_hash}: {e}")
            return None
    
    # Rate limiting
    async def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Check if rate limit is exceeded"""
        try:
            current = await self.redis_client.get(f"rate_limit:{key}")
            if current is None:
                await self.redis_client.setex(f"rate_limit:{key}", window, 1)
                return True
            elif int(current) < limit:
                await self.redis_client.incr(f"rate_limit:{key}")
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error checking rate limit for {key}: {e}")
            return True  # Allow on error
    
    # General caching
    async def set(self, key: str, value: Any, ttl: int = None):
        """Set a cache value"""
        try:
            serialized_value = json.dumps(value) if not isinstance(value, str) else value
            if ttl:
                await self.redis_client.setex(key, ttl, serialized_value)
            else:
                await self.redis_client.set(key, serialized_value)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a cache value"""
        try:
            value = await self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    async def delete(self, key: str):
        """Delete a cache key"""
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
    
    async def exists(self, key: str) -> bool:
        """Check if a cache key exists"""
        try:
            return bool(await self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Error checking cache key existence {key}: {e}")
            return False
    
    # OAuth PKCE storage
    async def store_pkce_verifier(self, state: str, code_verifier: str, ttl: int = 600):
        """Store PKCE code verifier"""
        try:
            await self.redis_client.setex(f"oauth:pkce:{state}", ttl, code_verifier)
        except Exception as e:
            logger.error(f"Error storing PKCE verifier for state {state}: {e}")
    
    async def get_pkce_verifier(self, state: str) -> Optional[str]:
        """Get PKCE code verifier"""
        try:
            return await self.redis_client.get(f"oauth:pkce:{state}")
        except Exception as e:
            logger.error(f"Error getting PKCE verifier for state {state}: {e}")
            return None
    
    # Cleanup methods
    async def clear_expired_sessions(self):
        """Clear expired sessions (Redis handles this automatically with TTL)"""
        pass
    
    async def clear_cache_pattern(self, pattern: str):
        """Clear cache keys matching a pattern"""
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cache keys matching pattern {pattern}")
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
