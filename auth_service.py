import os
import jwt
import bcrypt
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, cache_service=None):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
        self.cache_service = cache_service
        
        # Security scheme for FastAPI
        self.security = HTTPBearer()
        
        # Validate Redis is available for production security
        if not self.cache_service or not self.cache_service.redis_client:
            logger.warning("?? Redis not available - token blacklist functionality degraded")
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        try:
            # Generate salt and hash password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        try:
            to_encode = data.copy()
            
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
            to_encode.update({"exp": expire, "iat": datetime.utcnow()})
            
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            # Validate token format before processing
            if not token or not isinstance(token, str):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format"
                )
            
            # Check if token has proper JWT structure (3 parts separated by dots)
            token_parts = token.split('.')
            if len(token_parts) != 3:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format"
                )
            
            # Check if token is blacklisted in Redis
            if self.cache_service and self.cache_service.redis_client:
                try:
                    # Check individual key with last 16 chars
                    token_key = f"blacklist:token:{token[-16:]}"
                    is_blacklisted = self.cache_service.redis_client.exists(token_key)
                    
                    if is_blacklisted:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token has been revoked"
                        )
                except Exception as e:
                    logger.warning(f"Error checking token blacklist in Redis: {e}")
                    # Continue with token validation (fail open for availability)
            
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token has expired
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.PyJWTError as e:
            logger.error(f"JWT verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    def blacklist_token(self, token: str):
        """Add a token to the blacklist with automatic TTL based on JWT expiry"""
        try:
            if not self.cache_service or not self.cache_service.redis_client:
                raise RuntimeError("Redis required for token blacklisting in production")
            
            # Decode token to get expiry (without verification for blacklisting)
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                exp_timestamp = payload.get('exp')
                
                if exp_timestamp:
                    # Calculate TTL: time until token expires
                    ttl = int(exp_timestamp - time.time())
                    
                    if ttl > 0:
                        # Store with individual key and TTL
                        # Use last 16 chars of token as key (unique identifier)
                        token_key = f"blacklist:token:{token[-16:]}"
                        self.cache_service.redis_client.setex(token_key, ttl, "1")
                        logger.info(f"Token blacklisted in Redis with TTL={ttl}s")
                    else:
                        # Token already expired, no need to blacklist
                        logger.info("Token already expired, skipping blacklist")
                else:
                    # No expiry in token, use default 24 hour TTL
                    token_key = f"blacklist:token:{token[-16:]}"
                    self.cache_service.redis_client.setex(token_key, 86400, "1")
                    logger.warning("Token has no expiry, using 24h TTL")
            except jwt.DecodeError as e:
                logger.error(f"Failed to decode token for blacklisting: {e}")
                raise
                
        except Exception as e:
            logger.error(f"Error blacklisting token: {e}")
            raise
    
    def get_current_user_id(self, credentials: HTTPAuthorizationCredentials) -> str:
        """Extract user ID from JWT token"""
        try:
            payload = self.verify_token(credentials.credentials)
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
            return user_id
        except Exception as e:
            logger.error(f"Error getting current user ID: {e}")
            raise
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a refresh token (longer expiry)"""
        try:
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(days=30)  # 30 days for refresh token
            to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
            
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise
    
    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """Verify a refresh token"""
        try:
            payload = self.verify_token(token)
            
            # Check if it's actually a refresh token
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
        except Exception as e:
            logger.error(f"Error verifying refresh token: {e}")
            raise
    
    def generate_api_token(self, user_id: str, expires_days: int = 30) -> str:
        """Generate an API token for external access"""
        try:
            data = {
                "sub": user_id,
                "type": "api",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(days=expires_days)
            }
            
            token = jwt.encode(data, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            logger.error(f"Error generating API token: {e}")
            raise
    
    def verify_api_token(self, token: str) -> Dict[str, Any]:
        """Verify an API token"""
        try:
            payload = self.verify_token(token)
            
            # Check if it's actually an API token
            if payload.get("type") != "api":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
        except Exception as e:
            logger.error(f"Error verifying API token: {e}")
            raise
    
    def extract_token_from_header(self, authorization: str) -> str:
        """Extract token from Authorization header"""
        try:
            if not authorization:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization header missing"
                )
            
            # Handle both "Bearer token" and just "token" formats
            if authorization.startswith("Bearer "):
                return authorization.split(" ", 1)[1]
            else:
                return authorization
        except Exception as e:
            logger.error(f"Error extracting token from header: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
    
    def validate_password_strength(self, password: str) -> bool:
        """Validate password strength"""
        try:
            # Basic password validation
            if len(password) < 8:
                return False
            
            # Check for at least one uppercase, one lowercase, and one digit
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            
            return has_upper and has_lower and has_digit
        except Exception as e:
            logger.error(f"Error validating password strength: {e}")
            return False
    
    def generate_password_reset_token(self, user_id: str) -> str:
        """Generate a password reset token"""
        try:
            data = {
                "sub": user_id,
                "type": "password_reset",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
            }
            
            token = jwt.encode(data, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            logger.error(f"Error generating password reset token: {e}")
            raise
    
    def verify_password_reset_token(self, token: str) -> Dict[str, Any]:
        """Verify a password reset token"""
        try:
            payload = self.verify_token(token)
            
            # Check if it's actually a password reset token
            if payload.get("type") != "password_reset":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
        except Exception as e:
            logger.error(f"Error verifying password reset token: {e}")
            raise
    
    def cleanup_blacklisted_tokens(self):
        """Clean up expired tokens from blacklist (should be called periodically)"""
        try:
            # In a production environment, you'd want to store blacklisted tokens
            # in a database with expiry times and clean them up periodically
            # For now, we'll just clear the in-memory set periodically
            if len(self.blacklisted_tokens) > 10000:  # Arbitrary limit
                self.blacklisted_tokens.clear()
                logger.info("Blacklisted tokens cleared due to size limit")
        except Exception as e:
            logger.error(f"Error cleaning up blacklisted tokens: {e}")
