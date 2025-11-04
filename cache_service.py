import redis.asyncio as redis
import os
import json
import hashlib
import logging
import time
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_client = None
        self.redis_url = self._get_redis_url()
        self.is_connected = False
        self.connection_retries = 0
        self.max_retries = 3
        # In-memory fallback for critical short-lived secrets (e.g., PKCE verifiers)
        self._pkce_fallback: Dict[str, Tuple[str, datetime]] = {}
    
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
        """Initialize Redis connection with retry logic"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            await self.redis_client.ping()
            self.is_connected = True
            self.connection_retries = 0
            logger.info("Redis connection established successfully")
        except Exception as e:
            self.connection_retries += 1
            logger.error(f"Failed to connect to Redis (attempt {self.connection_retries}/{self.max_retries}): {e}")
            
            if self.connection_retries >= self.max_retries:
                logger.warning("Max Redis connection retries reached. Continuing without cache.")
                self.is_connected = False
                self.redis_client = None
            else:
                raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            try:
                await self.redis_client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
            finally:
                self.redis_client = None
                self.is_connected = False
    
    async def health_check(self):
        """Check Redis health"""
        if not self.is_connected or not self.redis_client:
            return False
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            self.is_connected = False
            return False

    async def ping_with_latency(self) -> Tuple[bool, Optional[int]]:
        """Ping Redis and capture latency in milliseconds."""
        if not self.redis_client:
            return False, None
        start = time.perf_counter()
        try:
            await self.redis_client.ping()
            latency_ms = int((time.perf_counter() - start) * 1000)
            self.is_connected = True
            return True, latency_ms
        except Exception as e:
            logger.error(f"Redis latency ping failed: {e}")
            self.is_connected = False
            return False, None
    
    def _is_redis_available(self):
        """Check if Redis is available for operations"""
        return self.is_connected and self.redis_client is not None
    
    # Session management
    async def store_session(self, session_id: str, user_id: str, expires_in: int = 86400):
        """Store user session"""
        if not self._is_redis_available():
            logger.warning("Redis unavailable, skipping session storage")
            return
        
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
            # Don't raise, just log the error
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user session"""
        if not self._is_redis_available():
            logger.warning("Redis unavailable, cannot retrieve session")
            return None
        
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
    def hash_prompt(self, prompt: str, model: str = "", max_tokens: int = 0, temperature: float = 0.0, **extras) -> str:
        """Create a hash for AI prompt caching.

        Accepts optional keyword-only extras (e.g., mode, tone) and folds them
        into the cache key in a deterministic way so callers can extend context
        without breaking compatibility with older call sites.
        """
        parts = [str(prompt), str(model), str(max_tokens), str(temperature)]
        if extras:
            # Include sorted extras to keep key stable regardless of ordering
            for k in sorted(extras.keys()):
                parts.append(f"{k}={extras[k]}")
        cache_key = ":".join(parts)
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
    async def store_pkce_verifier(self, state: str, code_verifier: str, ttl: int = 600) -> bool:
        """Store PKCE code verifier (falls back to in-memory when Redis unavailable)."""
        if not state or not code_verifier:
            return False
        ttl = max(1, ttl)
        if self._is_redis_available():
            try:
                await self.redis_client.setex(f"oauth:pkce:{state}", ttl, code_verifier)
                expires_at = datetime.utcnow() + timedelta(seconds=ttl)
                # Maintain local fallback to guard against transient cache hiccups
                self._pkce_fallback[state] = (code_verifier, expires_at)
                logger.debug(f"PKCE verifier cached in Redis for state {state}")
                return True
            except Exception as e:
                logger.error(f"Error storing PKCE verifier for state {state}: {e}")
        # Cache unavailable: remove any stale fallback so callback knows PKCE was skipped
        self._pkce_fallback.pop(state, None)
        return False
    
    async def get_pkce_verifier(self, state: str, *, delete: bool = True) -> Optional[str]:
        """Get (and optionally delete) PKCE verifier, falling back to in-memory store."""
        if not state:
            return None
        verifier: Optional[str] = None

        if self._is_redis_available():
            try:
                verifier = await self.redis_client.get(f"oauth:pkce:{state}")
                if verifier and delete:
                    try:
                        await self.redis_client.delete(f"oauth:pkce:{state}")
                    except Exception as cleanup_err:
                        logger.debug(f"Failed to delete PKCE verifier for state {state}: {cleanup_err}")
            except Exception as e:
                logger.error(f"Error getting PKCE verifier for state {state}: {e}")
        if verifier:
            # Redis hit
            self._pkce_fallback.pop(state, None)
            return verifier

        # Fallback path
        entry = self._pkce_fallback.get(state)
        if not entry:
            return None
        code_verifier, expires_at = entry
        if expires_at and expires_at < datetime.utcnow():
            # Expired
            self._pkce_fallback.pop(state, None)
            return None
        if delete:
            self._pkce_fallback.pop(state, None)
        return code_verifier
    
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
