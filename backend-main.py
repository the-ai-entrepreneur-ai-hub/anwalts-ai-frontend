import base64
"""
AnwaltsAI FastAPI Backend Server
Complete backend with PostgreSQL, Redis, and Together AI integration
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request, Response, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import os
from typing import Optional, List, Dict, Any, Tuple, Literal
from collections.abc import Mapping
import logging
from datetime import datetime, timedelta, timezone
from email.utils import parseaddr, parsedate_to_datetime
import uuid
import hashlib
import re
import asyncio
import httpx
import imaplib
import json
from PIL import Image, ImageOps, ImageDraw
import io
import time
import csv
import hmac
from decimal import Decimal

from models import *
from ai_service import AIService
from cache_service import CacheService
from smtp_utils import send_email
from fastapi.responses import Response as FastAPIResponse
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse, StreamingResponse
import httpx
from auth_service import AuthService
from database import Database
import base64
import secrets
import string
from supabase import create_client, Client as SupabaseClient

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # Keep running even if python-dotenv is not available
    pass

# ===== Feedback feature flag =====
import os as _os
FEEDBACK_V1_ENABLED = (_os.getenv("FEEDBACK_V1", "true").lower() == "true")

DASHBOARD_SERVICE_KEY = os.getenv("DASHBOARD_SERVICE_KEY", "").strip()

# Optional uploads subsystem
try:
    import upload_processor  # local module we added
except Exception:
    upload_processor = None

_UUID_SEGMENT = re.compile(r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.IGNORECASE)
_HEX_SEGMENT = re.compile(r"/[0-9a-f]{16,}", re.IGNORECASE)
_DIGIT_SEGMENT = re.compile(r"/\d+")


def _normalize_api_path(path: str) -> str:
    """Collapse variable segments (ids, uuids) for metrics bucketing."""
    normalized = _UUID_SEGMENT.sub("/:uuid", path)
    normalized = _HEX_SEGMENT.sub("/:hash", normalized)
    normalized = _DIGIT_SEGMENT.sub("/:id", normalized)
    return normalized


def _format_metric_value(value: int) -> str:
    """Format integer using German thousands separator."""
    return f"{value:,}".replace(",", ".")


def _percent_change(current: int, previous: int) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 2)


def _assert_admin(user: UserInDB):
    if user.role not in {"admin", "owner", "superadmin"}:
        raise HTTPException(status_code=403, detail="Administratorrechte erforderlich")

async def _verify_domain_imap_credentials(
    host: str,
    port: int,
    username: str,
    password: str,
    use_ssl: bool,
) -> None:
    """Validate IMAP credentials before persisting them."""
    loop = asyncio.get_running_loop()

    def _run_check():
        try:
            client = imaplib.IMAP4_SSL(host, port) if use_ssl else imaplib.IMAP4(host, port)
            client.login(username, password)
            try:
                client.logout()
            except Exception:
                pass
            return None
        except imaplib.IMAP4.error as err:
            return str(err)
        except Exception as err:
            return str(err)

    error_message = await loop.run_in_executor(None, _run_check)
    if error_message:
        raise HTTPException(
            status_code=400,
            detail=f"Anmeldung fehlgeschlagen: {error_message}",
        )


# ===== Pydantic models for feedback/edit =====
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import List as _List, Optional as _Optional, Literal as _Literal

class FeedbackRequest(BaseModel):
    conversation_id: _Optional[str] = None
    message_id: str
    model: _Optional[str] = None
    rating: int = Field(..., description="-1 or +1")
    reasons: _Optional[_List[str]] = None
    note: _Optional[str] = None
    message_hash: _Optional[str] = None
    client_ts: _Optional[str] = None

class EditRequest(BaseModel):
    conversation_id: _Optional[str] = None
    message_id: str
    edited_content: str
    allow_training: bool = False
    message_hash: _Optional[str] = None
    client_ts: _Optional[str] = None


class GmailConsentRequest(BaseModel):
    oauth_consent: bool
    ai_read_consent: bool
    draft_only_mode: _Optional[bool] = None


class ApiTokenCreateRequest(BaseModel):
    expires_in_days: _Optional[int] = Field(default=365, ge=1, le=1095)


class WebhookRequest(BaseModel):
    name: str
    url: HttpUrl
    events: _List[str] = Field(default_factory=list)
    is_active: bool = True
    secret: _Optional[str] = None


class UserRoleUpdateRequest(BaseModel):
    role: str


class UserActivationRequest(BaseModel):
    active: _Optional[bool] = None


class EmailSummarizeRequest(BaseModel):
    email_id: _Optional[str] = None
    account_id: _Optional[uuid.UUID] = None
    subject: _Optional[str] = None
    body: _Optional[str] = None
    refresh: bool = False


class ChatMessageSchema(BaseModel):
    role: _Literal["user", "assistant", "system"] = "user"
    content: str


class ChatSessionRequest(BaseModel):
    session_id: _Optional[str] = None
    title: _Optional[str] = None
    messages: _List[ChatMessageSchema]
    temperature: _Optional[float] = 0.6
    model: _Optional[str] = None
    reset: bool = False


class DomainEmailConnectRequest(BaseModel):
    email: EmailStr
    host: str
    port: int = Field(default=993, ge=1, le=65535)
    username: str
    password: str
    use_ssl: bool = True
    protocol: _Literal["imap", "ews"] = "imap"
    consent_mailbox: bool = Field(..., description="Consent for accessing mailbox contents")
    consent_ai: bool = Field(..., description="Consent for AI processing of emails")


class DomainEmailConnectionResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    host: str
    port: int
    username: str
    use_ssl: bool
    protocol: _Literal["imap", "ews"]
    mailbox_access_consent: bool
    ai_read_consent: bool
    last_verified_at: _Optional[datetime]
    last_status: _Optional[str]
    created_at: datetime
    updated_at: datetime


class DocumentAnalyzeRequest(BaseModel):
    title: _Optional[str] = None
    content: str
    categories: _Optional[_List[str]] = None
    model: _Optional[str] = None

# Email AI action requests
class EmailReplyRequest(BaseModel):
    email_id: _Optional[str] = None
    account_id: _Optional[uuid.UUID] = None
    subject: _Optional[str] = None
    body: _Optional[str] = None
    tone: _Optional[_Literal["legal", "neutral", "plain", "legal+plain"]] = "legal"


class EmailToDocumentRequest(BaseModel):
    email_id: _Optional[str] = None
    account_id: _Optional[uuid.UUID] = None
    subject: _Optional[str] = None
    body: _Optional[str] = None
    document_type: _Optional[str] = "email-briefing"
    title: _Optional[str] = None
    model: _Optional[str] = None

# ===== Rate limit helper using Redis =====
async def _rate_limit(user_id: str, route: str, max_count: int, window_sec: int = 3600) -> bool:
    try:
        key = f"rl:{route}:{user_id}:{datetime.utcnow().strftime('%Y%m%d%H')}"
        async with cache_service.redis_client.pipeline(transaction=True) as pipe:
            await pipe.incr(key)
            await pipe.expire(key, window_sec)
            cnt, _ = await pipe.execute()
        return int(cnt) <= max_count
    except Exception:
        # Fail-open to avoid blocking core flows
        return True

# ===== IP-based rate limiting for authentication endpoints =====
async def check_ip_rate_limit(request: Request, endpoint: str, limit: int, window: int):
    """Check IP-based rate limit for authentication endpoints"""
    try:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Redis key for this IP and endpoint
        key = f"rl:ip:{endpoint}:{client_ip}"
        
        if cache_service and cache_service.redis_client:
            count = cache_service.redis_client.incr(key)
            if count == 1:
                cache_service.redis_client.expire(key, window)
            
            if count > limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many requests. Please try again in {window} seconds.",
                    headers={"Retry-After": str(window)}
                )
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Rate limit check failed: {e}")
        # Fail open for availability
        pass

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _http_error_detail(exc: httpx.HTTPStatusError) -> str:
    try:
        data = exc.response.json()
        if isinstance(data, dict):
            inner = data.get("error")
            if isinstance(inner, dict):
                message = inner.get("message")
                if isinstance(message, str) and message.strip():
                    return message.strip()
            for key in ("message", "detail", "error"):
                value = data.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        text = exc.response.text
        if text:
            return text.strip()
    except Exception:
        pass
    return str(exc)

def _hash_ip(ip: str) -> str:
    salt = _os.getenv("FEEDBACK_SALT", "anwaltsai-feedback-salt")
    return _sha256(salt + (ip or ""))

def _coerce_uuid(value: Any) -> uuid.UUID:
    if isinstance(value, uuid.UUID):
        return value
    if value is None:
        raise ValueError("UUID value is required")
    return uuid.UUID(str(value))

def _try_uuid(value: Any) -> Optional[uuid.UUID]:
    try:
        return _coerce_uuid(value)
    except Exception:
        return None

def _parse_client_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).replace(tzinfo=None) if value.tzinfo else value
    if isinstance(value, str):
        candidate = value.strip()
        if candidate.endswith("Z"):
            candidate = candidate[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(candidate)
            if parsed.tzinfo:
                return parsed.astimezone(timezone.utc).replace(tzinfo=None)
            return parsed
        except Exception:
            return None
    return None

async def _ensure_message_exists(msg_id: str, user_id: str, content: str = None, model: str = None, conversation_id: str = None):
    try:
        async with db.get_connection() as conn:
            row = await conn.fetchrow("SELECT id FROM assistant_messages WHERE id = $1", uuid.UUID(msg_id))
            if row:
                return True
            # Insert skeleton if content provided
            if content is None:
                content = ""
            await conn.execute(
                """
                INSERT INTO assistant_messages (id, conversation_id, user_id, role, content, model, message_hash)
                VALUES ($1, $2, $3, 'assistant', $4, $5, $6)
                """,
                uuid.UUID(msg_id), uuid.UUID(conversation_id) if conversation_id else None,
                uuid.UUID(user_id), content, model, _sha256(content)
            )
            return True
    except Exception as e:
        logger.warning(f"ensure_message_exists failed: {e}")
        return False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
db: Database = None
ai_service: AIService = None
cache_service: CacheService = None
auth_service: AuthService = None


def _set_auth_cookies(response: Response, token: str) -> None:
    """Set primary (HttpOnly) and public session cookies."""
    try:
        cookie_domain = os.getenv("SESSION_DOMAIN", "portal-anwalts.ai")
        cookie_samesite = os.getenv("COOKIE_SAMESITE", "none").lower()
        response.set_cookie(
            key=os.getenv("SESSION_COOKIE_NAME", "sid"),
            value=token,
            httponly=True,
            secure=True,
            samesite=cookie_samesite,
            domain=cookie_domain,
            max_age=86400,
            path="/",
        )
        response.set_cookie(
            key=os.getenv("PUBLIC_SESSION_COOKIE", "sat"),
            value=token,
            httponly=False,
            secure=True,
            samesite=cookie_samesite,
            domain=cookie_domain,
            max_age=86400,
            path="/",
        )
    except Exception as exc:  # pragma: no cover - defensive logging only
        logger.warning(f"Set-Cookie failed: {exc}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources"""
    global db, ai_service, cache_service, auth_service
    
    # Initialize services
    db = Database()
    await db.connect()
    await db.ensure_settings_telemetry_schema()
    try:
        await db._ensure_chat_schema()
        await db._ensure_email_summary_schema()
    except Exception as schema_err:
        logger.error(f"Failed to ensure AI helper schema: {schema_err}")
    
    cache_service = CacheService()
    try:
        await cache_service.connect()
        logger.info("Cache service connected successfully")
    except Exception as e:
        logger.warning(f"Cache service unavailable, continuing without cache: {e}")
        # Keep cache_service instance alive so in-memory fallbacks remain available

    ai_service = AIService()
    auth_service = AuthService(cache_service=cache_service)
    
    cleanup_task = None
    # DISABLED: Token blacklist cleanup (function not implemented, TTL handles cleanup)
    # cleanup_task = asyncio.create_task(periodic_token_cleanup())
    # logger.info("?? Token blacklist cleanup scheduler started (1 hour interval)")
    
    # Test AI service connectivity
    if ai_service:
        try:
            logger.info(f"?? Testing AI service (provider: {ai_service.provider})")
            if ai_service.provider == "together" and ai_service.together_api_key:
                test_response = await ai_service.generate_completion(
                    prompt="Say 'Hello'",
                    model=ai_service.together_model,
                    max_tokens=5,
                    temperature=0.1
                )
                logger.info(f"? Together AI connected successfully: {test_response.content[:50]}")
            else:
                logger.warning(f"?? AI provider is {ai_service.provider}, skipping Together AI test")
        except Exception as e:
            logger.error(f"? AI service test failed: {e}")
            logger.error("?? Document generation may not work!")
    
    logger.info("? AnwaltsAI Backend started successfully")
    
    yield
    
    # Cleanup
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
    await db.disconnect()
    if cache_service:
        await cache_service.disconnect()
    logger.info("AnwaltsAI Backend shutdown complete")

# Initialize FastAPI app
app = FastAPI(
    title="AnwaltsAI Backend API",
    description="Complete backend for AnwaltsAI with PostgreSQL, Redis, and Together AI integration",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
cors_origin = os.getenv("CORS_ORIGIN", "https://portal-anwalts.ai")


def _get_supabase_admin() -> SupabaseClient:
    """Get Supabase admin client for user management"""
    supabase_url = os.getenv("SUPABASE_URL", "https://portal-anwalts.ai/supabase")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not supabase_service_key:
        raise ValueError("SUPABASE_SERVICE_ROLE_KEY not configured")
    return create_client(supabase_url, supabase_service_key)

def _build_google_redirect_uri() -> str:
    """Construct a redirect URI even when GOOGLE_REDIRECT_URI is missing."""
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "").strip()
    if redirect_uri:
        return redirect_uri

    base_origin = (os.getenv("PUBLIC_BASE_URL") or cors_origin or "").strip()
    if not base_origin:
        base_origin = "https://portal-anwalts.ai"
    base_origin = base_origin.rstrip("/")

    default_path = (os.getenv("GOOGLE_REDIRECT_PATH") or "/api/auth/google/callback").strip() or "/api/auth/google/callback"
    if not default_path.startswith("/"):
        default_path = "/" + default_path

    return f"{base_origin}{default_path}"


def _ensure_google_config(require_secret: bool = False) -> Tuple[str, Optional[str], str]:
    """Return Google OAuth configuration, raising helpful errors when missing."""
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    if client_id.lower().startswith(("http://", "https://")):
        client_id = client_id.split("://", 1)[-1]
    client_id = client_id.rstrip("/")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    redirect_uri = _build_google_redirect_uri()

    if not client_id:
        logger.error("Google OAuth missing client ID")
        raise HTTPException(status_code=500, detail="Google OAuth provider is not configured")
    if require_secret and not client_secret:
        logger.error("Google OAuth missing client secret")
        raise HTTPException(status_code=500, detail="Google OAuth provider is not fully configured")

    return client_id, (client_secret or None), redirect_uri

app.add_middleware(
    CORSMiddleware,
    allow_origins=[cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
)
app.add_middleware(GZipMiddleware, minimum_size=5000)

# Request size limit middleware
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Limit request body size to prevent DoS attacks"""
    max_size = 50 * 1024 * 1024  # 50MB limit
    
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"Request body too large. Maximum size: {max_size // 1024 // 1024}MB"
        )
    
    return await call_next(request)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https:; "
        "font-src 'self' data: https://cdn.jsdelivr.net; "
        "connect-src 'self' https://api.together.xyz; "
        "frame-ancestors 'none';"
    )
    
    # HTTP Strict Transport Security
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # XSS Protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Permissions Policy
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response

# Security
security = HTTPBearer()

# Flexible auth: Authorization header takes precedence; fall back to cookies only if no header
async def get_current_user_flexible(request: Request) -> UserInDB:
    try:
        auth_header = request.headers.get("authorization") or ""
        if auth_header.lower().startswith("bearer "):
            header_token = auth_header.split(" ", 1)[1].strip()
            try:
                payload = auth_service.verify_token(header_token)
                user_id = payload.get("sub")
                if not user_id:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
                user = await db.get_user_by_id(user_id)
                if not user:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
                return user
            except HTTPException:
                # Header present but invalid ? do not silently fall back to cookies
                raise
            except Exception as e:
                logger.error(f"flex-auth header verification error: {e}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

        # No Authorization header ? try cookies in a safe order
        cookie_candidates: List[Tuple[str, Optional[str]]] = [
            ("auth_token", request.cookies.get("auth_token")),
            (os.getenv("SESSION_COOKIE_NAME", "sid"), request.cookies.get(os.getenv("SESSION_COOKIE_NAME", "sid"))),
            (os.getenv("PUBLIC_SESSION_COOKIE", "sat"), request.cookies.get(os.getenv("PUBLIC_SESSION_COOKIE", "sat"))),
        ]
        for source, candidate in cookie_candidates:
            if not candidate:
                continue
            try:
                payload = auth_service.verify_token(candidate)
                user_id = payload.get("sub")
                if not user_id:
                    continue
                user = await db.get_user_by_id(user_id)
                if not user:
                    continue
                return user
            except Exception:
                continue

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authentication")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"flex-auth error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
# Admin guard middleware: block /api/admin/* unless role is admin
@app.middleware("http")
async def request_metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        path = request.url.path or ""
        if path.startswith("/api/") and getattr(db, "pool", None):
            try:
                normalized = _normalize_api_path(path)
                status_code = getattr(response, "status_code", 500) if response else 500
                latency_ms = int((time.perf_counter() - start) * 1000)
                await db.record_api_metric(request.method.upper(), normalized, status_code, latency_ms)
            except Exception as metric_error:
                logger.debug(f"metrics capture failed for {request.method} {path}: {metric_error}")

@app.middleware("http")
async def admin_guard(request: Request, call_next):
    path = request.url.path or ""
    if path.startswith("/api/admin"):
        # Require admin
        try:
            auth_header = request.headers.get("authorization") or request.cookies.get(os.getenv("SESSION_COOKIE_NAME", "sid"))
            if not auth_header:
                return FastAPIResponse(content='{"detail":"forbidden"}', media_type="application/json", status_code=403)
            token = auth_header.split(" ")[-1] if " " in auth_header else auth_header
            payload = auth_service.verify_token(token)
            user = await db.get_user_by_id(payload.get("sub"))
            if not user or user.role != "admin":
                return FastAPIResponse(content='{"detail":"forbidden"}', media_type="application/json", status_code=403)
        except Exception:
            return FastAPIResponse(content='{"detail":"forbidden"}', media_type="application/json", status_code=403)
    return await call_next(request)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInDB:
    """Get current authenticated user"""
    try:
        payload = auth_service.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = await db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


# ============ AUTHENTICATION ENDPOINTS ============

# Lightweight authorize endpoints to kick off OAuth in a reliable full-page redirect
def _b64url_no_pad(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _generate_compliant_password(length: int = 48) -> str:
    """Generate a strong password with multiple chars per category and no edge chars.

    - At least 4 uppercase, 4 lowercase, 4 digits, 4 specials
    - Remaining filled from a safe pool
    - Length >= 32
    """
    length = max(length, 32)
    safe_specials = "!@#$%^&*()-_=+[]{}:,./?"  # Avoid quotes, backslashes, spaces

    rng = secrets.SystemRandom()

    uppers = [rng.choice(string.ascii_uppercase) for _ in range(4)]
    lowers = [rng.choice(string.ascii_lowercase) for _ in range(4)]
    digits = [rng.choice(string.digits) for _ in range(4)]
    specials = [rng.choice(safe_specials) for _ in range(4)]

    base = uppers + lowers + digits + specials
    pool = string.ascii_letters + string.digits + safe_specials
    remaining_count = length - len(base)
    base += [rng.choice(pool) for _ in range(max(0, remaining_count))]

    rng.shuffle(base)
    return ''.join(base)


async def _google_entry_redirect(request: Request) -> RedirectResponse:
    """Return a prefix-aware redirect so /api routes stay under /api."""
    path = request.url.path or ""
    prefix = "/api/auth" if path.startswith("/api/") else "/auth"
    query = request.url.query
    target = f"{prefix}/google/authorize"
    if query:
        target = f"{target}?{query}"
    return RedirectResponse(target)


@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint for monitoring and observability"""
    try:
        # Database pool metrics
        pool_size = db.pool.get_size() if db.pool else 0
        pool_free = db.pool.get_idle_size() if db.pool else 0
        pool_used = pool_size - pool_free
        pool_usage_percent = round((pool_used / 20 * 100), 2) if pool_size > 0 else 0
        
        # Count blacklisted tokens
        blacklist_count = 0
        if cache_service and cache_service.redis_client:
            try:
                cursor = 0
                while True:
                    cursor, keys = cache_service.redis_client.scan(cursor, match="blacklist:token:*", count=100)
                    blacklist_count += len(keys)
                    if cursor == 0:
                        break
            except Exception:
                pass
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "pool_size": pool_size,
                "pool_used": pool_used,
                "pool_free": pool_free,
                "pool_usage_percent": pool_usage_percent,
                "pool_max_configured": 20
            },
            "cache": {
                "status": "connected" if (cache_service and cache_service.redis_client) else "disconnected",
                "blacklisted_tokens": blacklist_count
            },
            "security": {
                "jwt_algorithm": auth_service.algorithm if auth_service else "unknown",
                "token_expire_minutes": auth_service.access_token_expire_minutes if auth_service else 0
            },
            "ai_service": {
                "provider": ai_service.provider if ai_service else "unknown",
                "model": (ai_service.local_default_model if ai_service.provider == "sidecar" 
                         else ai_service.together_model) if ai_service else "unknown"
            }
        }
    except Exception as e:
        logger.error(f"Metrics endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Metrics unavailable")

@app.get("/auth/google")
async def google_auth(request: Request):
    """Redirect to Google OAuth authorize endpoint"""
    return await _google_entry_redirect(request)


@app.get("/auth/google/authorize")
async def google_authorize(request: Request):
    try:
        import urllib.parse
        client_id, _, redirect_uri = _ensure_google_config()
        mode = (request.query_params.get("mode") or "").strip().lower()
        include_gmail = mode in {"gmail", "email", "mail", "workspace"}
        link_user_id: Optional[str] = None
        if include_gmail:
            try:
                current_user = await get_current_user_flexible(request)
                link_user_id = str(current_user.id)
            except HTTPException:
                logger.warning("Gmail linking requested without authenticated session")
                raise HTTPException(
                    status_code=401,
                    detail="Bitte melden Sie sich an, bevor Sie ein E-Mail-Konto verkn?pfen.",
                )
        base_scopes = ["openid", "email", "profile"]
        if include_gmail:
            base_scopes.extend([
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.modify",
            ])
        # Preserve caller-provided additional scopes
        extra_scope = request.query_params.get("scope")
        if extra_scope:
            base_scopes.extend(s.strip() for s in extra_scope.split() if s.strip())
        # Deduplicate while preserving order
        seen = set()
        ordered_scopes = []
        for scope_entry in base_scopes:
            if scope_entry not in seen:
                seen.add(scope_entry)
                ordered_scopes.append(scope_entry)
        scope = urllib.parse.quote(" ".join(ordered_scopes))
        state = request.query_params.get("state") or uuid.uuid4().hex
        base = "https://accounts.google.com/o/oauth2/v2/auth"
        access_type = request.query_params.get("access_type")
        if not access_type:
            access_type = "offline" if include_gmail else "online"
        prompt = request.query_params.get("prompt")
        if not prompt:
            prompt = "consent" if include_gmail else "select_account"
        url = (f"{base}?response_type=code&client_id={urllib.parse.quote(client_id)}"
               f"&redirect_uri={urllib.parse.quote(redirect_uri)}&scope={scope}&state={state}"
               f"&access_type={urllib.parse.quote(access_type)}&prompt={urllib.parse.quote(prompt)}")
        if include_gmail:
            url += "&include_granted_scopes=true"

        # Set up PKCE so Google OAuth works even when consent screen forces PKCE
        pkce_supported = False
        code_verifier = _b64url_no_pad(secrets.token_bytes(32))
        code_challenge = _b64url_no_pad(hashlib.sha256(code_verifier.encode()).digest())
        if cache_service:
            try:
                pkce_supported = await cache_service.store_pkce_verifier(state, code_verifier, ttl=600)
                if pkce_supported:
                    logger.debug(f"PKCE verifier stored for state {state}")
                else:
                    logger.warning(f"PKCE verifier not stored (cache unavailable) for state {state}")
            except Exception as store_err:
                logger.warning(f"PKCE verifier store failed, falling back to non-PKCE flow: {store_err}")
        if pkce_supported:
            url += f"&code_challenge={code_challenge}&code_challenge_method=S256"
        else:
            logger.debug("Google OAuth proceeding without PKCE challenge (cache unavailable)")

        from fastapi.responses import RedirectResponse
        response = RedirectResponse(url)
        try:
            response.set_cookie(
                key="oauth_flow_mode",
                value="gmail" if include_gmail else "login",
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=600,
                path="/",
            )
        except Exception as cookie_error:  # pragma: no cover - defensive logging only
            logger.warning(f"Failed to set oauth_flow_mode cookie: {cookie_error}")
        if include_gmail and link_user_id:
            if cache_service:
                try:
                    await cache_service.set(f"oauth:link-user:{state}", link_user_id, ttl=600)
                except Exception as link_store_err:
                    logger.debug(f"Failed to persist link-user state: {link_store_err}")
            try:
                response.set_cookie(
                    key="email_link_uid",
                    value=link_user_id,
                    httponly=True,
                    secure=True,
                    samesite="lax",
                    max_age=600,
                    path="/",
                )
            except Exception as link_cookie_err:
                logger.warning(f"Failed to set email_link_uid cookie: {link_cookie_err}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google authorize error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Authorization init failed")

@app.get("/api/auth/google")
async def google_auth_api_alias(request: Request):
    return await _google_entry_redirect(request)

@app.get("/api/auth/google/authorize")
async def google_authorize_api_alias(request: Request):
    return await google_authorize(request)

@app.get("/auth/twitter/authorize")
async def twitter_authorize():
    try:
        import urllib.parse
        client_id = os.getenv("TWITTER_CLIENT_ID", "")
        redirect_uri = os.getenv("TWITTER_REDIRECT_URI", "")
        raw_scopes = os.getenv("TWITTER_SCOPES", "tweet.read users.read")
        scope = urllib.parse.quote(raw_scopes)
        state = uuid.uuid4().hex
        # PKCE (S256)
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
        code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode().rstrip("=")
        try:
            await cache_service.redis_client.setex(f"oauth:pkce:{state}", 600, code_verifier)
        except Exception as e:
            logger.warning(f"PKCE store failed: {e}")
        base = "https://twitter.com/i/oauth2/authorize"
        url = (f"{base}?response_type=code&client_id={urllib.parse.quote(client_id)}"
               f"&redirect_uri={urllib.parse.quote(redirect_uri)}&scope={scope}&state={state}"
               f"&code_challenge={code_challenge}&code_challenge_method=S256")
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url)
    except Exception as e:
        logger.error(f"Twitter authorize error: {e}")
        raise HTTPException(status_code=500, detail="Authorization init failed")


# ============ OAUTH CALLBACKS ============

async def _redirect(path: str, clear_flow_cookie: bool = True) -> RedirectResponse:
    response = RedirectResponse(url=path, status_code=302)
    if clear_flow_cookie:
        try:
            response.delete_cookie("oauth_flow_mode", path="/")
        except Exception as err:  # pragma: no cover - defensive logging only
            logger.debug(f"Failed to clear oauth_flow_mode cookie on redirect: {err}")
    return response


async def _initial_gmail_sync(user_id: uuid.UUID):
    """Background task to pull initial emails after OAuth."""
    try:
        await asyncio.sleep(2)  # Brief delay to ensure token is persisted
        logger.info(f"Starting initial Gmail sync for user {user_id}")
        
        # Get user"s active email account
        account = await db.get_active_email_account(user_id)
        if not account or not account.get("ai_read_consent"):
            logger.warning(f"Cannot sync: no account or no AI consent for user {user_id}")
            return
        
        result = await _fetch_gmail_message_list(
            user_id=user_id,
            account=account,
            label="INBOX",
            folder="inbox",
            limit=20,
            page_token=None,
        )
        logger.info(
            "Initial Gmail sync completed for user %s: %s emails retrieved",
            user_id,
            len(result.get("emails", [])),
        )
                
    except Exception as e:
        logger.error(f"Initial Gmail sync failed for {user_id}: {e}", exc_info=True)


@app.get("/auth/google/callback")
async def google_callback(request: Request, code: Optional[str] = None, state: Optional[str] = None):
    # Distributed lock to prevent race conditions on duplicate OAuth callbacks
    lock_key = f"oauth:lock:{code}:{state}"
    lock_acquired = False
    
    try:
        # Try to acquire distributed lock
        if cache_service and cache_service.redis_client and code and state:
            lock_acquired = cache_service.redis_client.set(lock_key, "1", nx=True, ex=10)
            
            if not lock_acquired:
                logger.warning(f"OAuth callback already processing (state={state}), checking cache...")
                # Wait briefly for concurrent request to complete
                await asyncio.sleep(1)
                # Check for cached result
                result_key = f"oauth:result:{state}"
                cached_redirect = cache_service.redis_client.get(result_key)
                if cached_redirect:
                    logger.info("Returning cached OAuth redirect from concurrent request")
                    return RedirectResponse(url=cached_redirect, status_code=302)
    except Exception as lock_err:
        logger.warning(f"OAuth lock acquisition failed, continuing anyway: {lock_err}")
    
    flow_mode = "login"
    try:
        cookie_mode = request.cookies.get("oauth_flow_mode")
        if cookie_mode in {"gmail", "login"}:
            flow_mode = cookie_mode
        elif not cookie_mode:
            # Fallback: check for email_link_uid cookie to detect Gmail flow
            email_link_uid = request.cookies.get("email_link_uid")
            if email_link_uid:
                flow_mode = "gmail"
                logger.info("Gmail flow detected via email_link_uid cookie (oauth_flow_mode missing)")
        # Additional fallback: detect Gmail flow using server-side state mapping
        # This covers environments where cookies are suppressed/blocked
        if flow_mode != "gmail" and cache_service and state:
            try:
                cached_user = await cache_service.get(f"oauth:link-user:{state}")
                # Value may be stored as scalar or wrapped object
                if isinstance(cached_user, dict):
                    cached_user = cached_user.get("value")
                if cached_user:
                    flow_mode = "gmail"
                    logger.info("Gmail flow inferred via server state mapping (cookie missing)")
            except Exception as cache_err:  # pragma: no cover - defensive logging only
                logger.debug(f"flow-mode cache lookup failed: {cache_err}")
    except Exception as cookie_read_error:  # pragma: no cover - defensive logging only
        logger.debug(f"oauth_flow_mode cookie read failed: {cookie_read_error}")
    link_state_key = f"oauth:link-user:{state}" if state else None

    async def _resolve_portal_user() -> Optional[UserInDB]:
        try:
            return await get_current_user_flexible(request)
        except HTTPException:
            pass
        link_user_val: Optional[str] = None
        if cache_service and state:
            try:
                cached_user = await cache_service.get(f"oauth:link-user:{state}")
                if isinstance(cached_user, dict):
                    cached_user = cached_user.get("value")
                if cached_user:
                    link_user_val = str(cached_user)
            except Exception as cache_err:
                logger.debug(f"link-user cache lookup failed: {cache_err}")
        if not link_user_val:
            link_user_val = request.cookies.get("email_link_uid")
        if not link_user_val:
            return None
        try:
            return await db.get_user_by_id(link_user_val)
        except Exception as fetch_err:
            logger.debug(f"link-user DB lookup failed: {fetch_err}")
            return None

    # Resolve current portal session up-front to keep identity stable
    portal_user: Optional[UserInDB] = None
    try:
        portal_user = await _resolve_portal_user()
    except Exception:
        portal_user = None

    # CRITICAL FIX: Handle duplicate callback requests gracefully
    if not code:
        # Check if this is a duplicate request and user is already authenticated
        try:
            if flow_mode == "gmail" and portal_user:
                gmail_status = await db.get_gmail_connection_status(portal_user.id)
                if gmail_status.get("connected"):
                    logger.info(
                        "Duplicate Gmail OAuth callback - user %s already connected",
                        portal_user.id,
                    )
                    response = await _redirect("/email")
                    response.delete_cookie("email_link_uid", path="/")
                    return response
            else:
                auth_token = request.cookies.get("auth_token")
                if auth_token:
                    payload = auth_service.verify_token(auth_token)
                    user_id = payload.get("sub")
                    # Check if user already has Gmail connected
                    gmail_status = await db.get_gmail_connection_status(uuid.UUID(user_id))
                    if gmail_status.get("connected"):
                        target = "/email" if flow_mode == "gmail" else "/dashboard"
                        logger.info(
                            "Duplicate OAuth callback - user %s already connected, redirecting to %s",
                            user_id,
                            target,
                        )
                        response = await _redirect(target)
                        response.delete_cookie("email_link_uid", path="/")
                        return response
        except Exception as e:
            logger.debug(f"Could not check existing connection: {e}")

        raise HTTPException(status_code=400, detail="Missing authorization code")
    try:
        token_url = "https://oauth2.googleapis.com/token"
        client_id, client_secret, redirect_uri = _ensure_google_config(require_secret=True)
        code_verifier = None
        if cache_service and state:
            try:
                code_verifier = await cache_service.get_pkce_verifier(state, delete=True)
            except Exception as pkce_err:
                logger.warning(f"Failed to load PKCE verifier for state {state}: {pkce_err}")
            if not code_verifier:
                logger.warning(f"PKCE verifier missing for state {state}; attempting token exchange without verifier")
        async with httpx.AsyncClient(timeout=10) as client:
            token_payload = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret or "",
                "redirect_uri": redirect_uri,
            }
            if code_verifier:
                token_payload["code_verifier"] = code_verifier

            token_res = await client.post(
                token_url,
                data=token_payload,
                headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
            )
            token_res.raise_for_status()
            tokens = token_res.json()
            id_token = tokens.get("id_token")
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")  # Extract refresh token for Gmail
            if flow_mode == "gmail":
                if refresh_token:
                    logger.info("Received Gmail refresh token for Gmail linking flow")
                else:
                    logger.warning("Gmail OAuth callback completed without refresh token for linking flow")
            scope_raw = tokens.get("scope")
            granted_scopes = [s for s in scope_raw.split() if isinstance(scope_raw, str) and s] if scope_raw else []

            # Get profile
            userinfo_res = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            userinfo_res.raise_for_status()
            profile = userinfo_res.json()

        email = (profile.get("email") or "").lower().strip()
        given = (profile.get("given_name") or "").strip()
        family = (profile.get("family_name") or "").strip()
        name = (profile.get("name") or "").strip() or (given + (" " if given and family else "") + family)
        if not email:
            return await _redirect("/onboarding")

        # Independence enforcement: if Gmail scopes are present and we have a portal session,
        # treat this as a mailbox link even if cookies/state were lost.
        has_gmail_scopes = any(
            isinstance(s, str) and "googleapis.com/auth/gmail" in s for s in (granted_scopes or [])
        )
        if has_gmail_scopes and flow_mode != "gmail":
            flow_mode = "gmail"
            logger.info("Gmail flow inferred via token scopes (session independence)")

        if flow_mode == "gmail":
            # Validate Gmail flow has authenticated user; never switch account identity here
            if not portal_user:
                raise HTTPException(status_code=401, detail="Aktive Sitzung erforderlich, um Gmail zu verkn?pfen.")
            if not refresh_token:
                raise HTTPException(status_code=400, detail="Gmail-Refresh-Token wurde nicht bereitgestellt.")
            portal_login_email = (portal_user.email or "").strip().lower()
            normalized_gmail_email = email.lower()
            if portal_login_email and normalized_gmail_email != portal_login_email:
                logger.warning(
                    "Rejected Gmail linking: portal user %s attempted to link mismatched mailbox %s (expected %s)",
                    portal_user.id,
                    normalized_gmail_email,
                    portal_login_email,
                )
                if cache_service and link_state_key:
                    try:
                        await cache_service.delete(link_state_key)
                    except Exception as delete_err:
                        logger.debug(f"Failed to clear link-user state after mismatch: {delete_err}")
                response = await _redirect("/email?gmail_error=account_mismatch")
                response.delete_cookie("email_link_uid", path="/")
                response.delete_cookie("oauth_flow_mode", path="/")
                return response
            try:
                account = await db.set_gmail_refresh_token(
                    portal_user.id,
                    refresh_token,
                    email_address=email,
                    display_name=name or email,
                    scopes=granted_scopes or None,
                    oauth_consent=True,
                    ai_read_consent=True,  # Default to True; will use pending consent if available
                    link_source="oauth",
                )
            except ValueError as link_err:
                logger.warning(
                    "Gmail linking rejected for user %s: %s",
                    portal_user.id,
                    link_err,
                )
                if cache_service and link_state_key:
                    try:
                        await cache_service.delete(link_state_key)
                    except Exception as delete_err:
                        logger.debug(f"Failed to clear link-user state: {delete_err}")
                response = await _redirect("/email?gmail_error=login_email_conflict")
                response.delete_cookie("email_link_uid", path="/")
                return response
            if not account:
                raise HTTPException(
                    status_code=500,
                    detail="Gmail-Integration fehlgeschlagen. Bitte versuchen Sie es erneut."
                )
            await db.set_active_email_account(portal_user.id, account["id"])
            
            # CRITICAL FIX: Return simple HTML redirect without token JavaScript
            # This preserves the current user's session and prevents session hijacking
            simple_html = """<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Gmail Connected</title>
</head>
<body>
<script>
try {
    var redirectWindow = window;
    try {
        if (window.top && window.top !== window) {
            redirectWindow = window.top;
        }
    } catch (frameErr) {
        console.warn('Unable to access top window, falling back to self', frameErr);
    }
    redirectWindow.location.replace('/email');
} catch (e) {
    console.error('Redirect error:', e);
    window.location.replace('/email');
}
</script>
<p>Gmail connected successfully! Redirecting...</p>
</body>
</html>"""
            
            response = HTMLResponse(content=simple_html, status_code=200)
            response.headers["Cache-Control"] = "no-store"
            response.headers["Content-Type"] = "text/html; charset=utf-8"
            
            # Set active_email_account cookie
            try:
                response.set_cookie(
                    key="active_email_account",
                    value=str(account["id"]),
                    httponly=False,
                    secure=True,
                    samesite="lax",
                    max_age=86400,
                    path="/",
                )
            except Exception as cookie_err:
                logger.warning(f"Failed to set active_email_account cookie: {cookie_err}")
            
            # Clean up OAuth flow cookies
            response.delete_cookie("email_link_uid", path="/")
            response.delete_cookie("oauth_flow_mode", path="/")
            
            if cache_service and link_state_key:
                try:
                    await cache_service.delete(link_state_key)
                except Exception as delete_err:
                    logger.debug(f"Failed to clear link-user state: {delete_err}")
            
            # DO NOT set auth_token or user_id cookies - preserve existing session!
            logger.info(f"Gmail account {email} linked to user {portal_user.id} - session preserved")
            return response

        # SAFETY CHECK: Gmail flow should have returned by now
        if flow_mode == "gmail":
            logger.error(
                "Gmail flow reached login code path - this should never happen! "
                "portal_user=%s, email=%s",
                portal_user.id if portal_user else None,
                email
            )
            raise HTTPException(
                status_code=500,
                detail="Internal error: Gmail linking flow corruption. Please try again."
            )

        # Determine role by email allowlist/domain (LOGIN FLOW ONLY)
        # Hardcoded admin emails for initial setup
        AUTHORIZED_ADMINS = {
            "test.reg.e2e+20251026@anwalts.ai",
            "angelageneralao.1997@gmail.com"
        }
        admin_domains = (os.getenv("ADMIN_EMAIL_DOMAINS", "").strip() or "").split(",")
        admin_emails = set((os.getenv("ADMIN_EMAILS", "").strip() or "").lower().split(","))
        admin_emails = admin_emails.union(AUTHORIZED_ADMINS)
        email_domain = email.split("@")[-1] if "@" in email else ""
        is_admin = (email.lower() in admin_emails) or (email_domain in [d.strip().lower() for d in admin_domains if d.strip()])

        # Find or create user
        existing_user = await db.get_user_by_email(email)
        if existing_user:
            user = existing_user
            # Update name/role if changed
            try:
                if (name and user.name != name) or (is_admin and user.role != "admin"):
                    await db.update_user_basic(user.id, name=name or user.name, role=("admin" if is_admin else user.role))
                    user = await db.get_user_by_id(user.id)
            except Exception as _:
                pass
        else:
            compliant_pwd = _generate_compliant_password()
            password_hash = auth_service.hash_password(compliant_pwd)
            user = await db.create_user(email=email, name=name or email, role=("admin" if is_admin else "assistant"), password_hash=password_hash)

        # Store Gmail refresh token if present (for email integration)
        saved_account = None
        if refresh_token:
            try:
                saved_account = await db.set_gmail_refresh_token(
                    user.id,
                    refresh_token,
                    email_address=email,
                    display_name=name or email,
                    scopes=granted_scopes or None,
                    oauth_consent=True,
                    link_source="login",
                )
                if saved_account:
                    await db.set_active_email_account(user.id, saved_account["id"])
                    logger.info(f"Gmail refresh token stored for user {email}")
                    if saved_account.get("oauth_consent") and saved_account.get("ai_read_consent"):
                        try:
                            asyncio.create_task(_initial_gmail_sync(user.id))
                        except RuntimeError as sync_err:
                            logger.warning("Unable to schedule initial Gmail sync: %s", sync_err)
            except ValueError as validation_err:
                logger.info(
                    "Skipping Gmail token storage for %s due to independence rule: %s",
                    email,
                    validation_err,
                )
            except Exception as e:
                logger.error(f"Failed to store Gmail refresh token for {email}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="Gmail-Integration fehlgeschlagen. Bitte versuchen Sie es erneut."
                )
        elif flow_mode == "gmail":
            logger.warning(
                "Gmail OAuth callback completed without refresh token for user %s", email
            )
        
        # Create simple JWT token session
        token = auth_service.create_access_token(data={"sub": str(user.id), "email": email, "name": name, "role": user.role})
        session_id = str(uuid.uuid4())
        if cache_service:
            await cache_service.store_session(session_id, str(user.id), expires_in=86400)
        
        # Simple redirect with token in localStorage - check for return path
        # CRITICAL FIX: Use sessionStorage flag to prevent duplicate processing
        html = (
            "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>Signing in?</title></head><body>"
            "<script>"
            "try {"
            f"  var oauthState = {json.dumps(state or '')};"
            "  var processedStateKey = 'oauth_processed_state';"
            f"  var flowMode = {json.dumps(flow_mode)};"
            "  var returnKey = 'gmail_oauth_return';"
            "  var redirectWindow = window;"
            "  try {"
            "    if (window.top && window.top !== window) {"
            "      redirectWindow = window.top;"
            "    }"
            "  } catch (frameErr) {"
            "    console.warn('Unable to access top window, falling back to self', frameErr);"
            "    redirectWindow = window;"
            "  }"
            "  var computeReturnPath = function() {"
            "    var stored = null;"
            "    try {"
            "      var sessionVal = sessionStorage.getItem(returnKey);"
            "      if (sessionVal && sessionVal.trim()) { stored = sessionVal; }"
            "    } catch (err) {"
            "      console.warn('Session return lookup failed', err);"
            "    }"
            "    if (!stored) {"
            "      try {"
            "        var legacyVal = localStorage.getItem(returnKey);"
            "        if (legacyVal && legacyVal.trim()) { stored = legacyVal; }"
            "      } catch (legacyErr) {"
            "        console.warn('Legacy return lookup failed', legacyErr);"
            "      }"
            "    }"
            "    if (stored && stored.trim && stored.trim()) {"
            "      return stored;"
            "    }"
            "    if (flowMode === 'gmail') {"
            "      return '/email';"
            "    }"
            "    return '/dashboard';"
            "  };"
            "  var clearReturnPath = function() {"
            "    try { sessionStorage.removeItem(returnKey); } catch (err) {}"
            "    try { localStorage.removeItem(returnKey); } catch (err2) {}"
            "  };"
            "  var isDuplicate = false;"
            "  try {"
            "    var lastState = sessionStorage.getItem(processedStateKey);"
            "    if (oauthState && lastState === oauthState) {"
            "      isDuplicate = true;"
            "    } else if (!oauthState && sessionStorage.getItem('oauth_processed') === 'true') {"
            "      isDuplicate = true;"
            "    }"
            "  } catch (stateErr) {"
            "    console.warn('State tracking check failed', stateErr);"
            "  }"
            "  if (isDuplicate) {"
            "    var existingToken = null;"
            "    try {"
            "      existingToken = localStorage.getItem('auth_token') || localStorage.getItem('anwalts_auth_token') || localStorage.getItem('access_token');"
            "    } catch (existingErr) {"
            "      console.warn('Token lookup failed', existingErr);"
            "    }"
            "    if (!existingToken) {"
            "      console.warn('Duplicate detected without stored token, treating as fresh login');"
            "      isDuplicate = false;"
            "    }"
            "  }"
            "  if (isDuplicate) {"
            "    console.log('OAuth already processed for state', oauthState);"
            "    var returnPath = computeReturnPath();"
            "    clearReturnPath();"
            "    redirectWindow.location.replace(returnPath);"
            "  } else {"
            "    try { sessionStorage.setItem(processedStateKey, oauthState || ''); } catch (persistErr) { console.warn('State persist failed', persistErr); }"
            "    try { sessionStorage.removeItem('oauth_processed'); } catch (_) {}"
            "    sessionStorage.setItem('oauth_processed', 'true');"
            "    localStorage.setItem('auth_token', %s);"
            "    localStorage.setItem('anwalts_auth_token', %s);"
            "    var authPayload = { id: %s, email: %s, name: %s, role: %s };"
            "    try {"
            "      localStorage.setItem('auth_user', JSON.stringify(authPayload));"
            "      localStorage.setItem('anwalts_user', JSON.stringify(authPayload));"
            "    } catch (jsonErr) {"
            "      console.warn('Failed to persist structured auth payload', jsonErr);"
            "    }"
            "    try {"
            "      localStorage.setItem('user_id', authPayload.id || '');"
            "      localStorage.setItem('user_email', authPayload.email || '');"
            "      localStorage.setItem('user_name', authPayload.name || '');"
            "      localStorage.setItem('user_role', authPayload.role || '');"
            "    } catch (legacyStoreErr) {"
            "      console.warn('Legacy storage update failed', legacyStoreErr);"
            "    }"
            "    console.log('Auth data stored successfully', authPayload);"
            "    var finalReturn = computeReturnPath();"
            "    clearReturnPath();"
            "    redirectWindow.location.replace(finalReturn);"
            "  }"
            "} catch (e) { console.error('Storage error:', e); try { redirectWindow.location.replace('/dashboard'); } catch (_e) { window.location.replace('/dashboard'); } }"
            "</script>"
            "Signing in?</body></html>"
        ) % (
            repr(token),
            repr(token),
            repr(str(user.id)),
            repr(email),
            repr(name),
            repr(user.role)
        )
        response = HTMLResponse(content=html, status_code=200)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        response.headers["Content-Encoding"] = "identity"
        
        # Set auth cookies
        response.set_cookie(
            key="auth_token",
            value=token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=86400,
            path="/",
        )
        response.set_cookie(
            key="user_id",
            value=str(user.id),
            httponly=False,
            secure=True,
            samesite="lax",
            max_age=86400,
            path="/",
        )
        try:
            response.delete_cookie("oauth_flow_mode", path="/")
        except Exception as clear_err:  # pragma: no cover - defensive logging only
            logger.debug(f"Failed to clear oauth_flow_mode cookie: {clear_err}")
        if cache_service and link_state_key:
            try:
                await cache_service.delete(link_state_key)
            except Exception as delete_err:
                logger.debug(f"Failed to clear link-user state after login: {delete_err}")
        response.delete_cookie("email_link_uid", path="/")
        if saved_account:
            try:
                response.set_cookie(
                    key="active_email_account",
                    value=str(saved_account["id"]),
                    httponly=False,
                    secure=True,
                    samesite="lax",
                    max_age=86400,
                    path="/",
                )
            except Exception:
                pass

        logger.info(f"OAuth login successful for: {email}")
        return response
    except httpx.HTTPError as e:
        try:
            detail = e.response.text
            # CRITICAL FIX: Handle invalid_grant (reused OAuth code) gracefully
            try:
                error_json = e.response.json()
                if error_json.get("error") == "invalid_grant":
                    logger.warning(f"OAuth code already used (invalid_grant) - checking existing connection")
                    # Try to identify user from previous successful auth
                    try:
                        auth_token = request.cookies.get("auth_token")
                        if auth_token:
                            payload = auth_service.verify_token(auth_token)
                            user_id = payload.get("sub")
                            gmail_status = await db.get_gmail_connection_status(uuid.UUID(user_id))
                            if gmail_status.get("connected"):
                                # Already connected, redirect to success page
                                target = "/email" if flow_mode == "gmail" else "/dashboard"
                                logger.info(f"User {user_id} already has Gmail connected, redirecting to {target}")
                                return await _redirect(target)
                    except Exception as check_error:
                        logger.debug(f"Error checking existing connection: {check_error}")
                    
                    # If we can't verify existing connection, show friendly error
                    error_response = HTMLResponse(content="""
                        <!doctype html><html><head><meta charset='utf-8'>
                        <meta name='viewport' content='width=device-width, initial-scale=1'>
                        <title>Authentication Issue</title></head><body style='font-family: sans-serif; max-width: 600px; margin: 100px auto; padding: 20px; text-align: center;'>
                        <h2>Authentication Link Expired</h2>
                        <p>This authorization link has already been used or has expired.</p>
                        <p>If you just connected your Gmail, your emails should already be accessible.</p>
                        <p><a href='/email' style='display: inline-block; margin-top: 20px; padding: 10px 20px; background: #5b7ce6; color: white; text-decoration: none; border-radius: 8px;'>Go to Email</a></p>
                        </body></html>
                    """, status_code=400)
                    try:
                        error_response.delete_cookie("oauth_flow_mode", path="/")
                    except Exception:
                        pass
                    return error_response
            except ValueError:
                # Response is not JSON, continue with original error handling
                pass
        except Exception:
            detail = str(e)
        if "'invalid_client'" in detail or '"invalid_client"' in detail:
            logger.error("Google OAuth rejected client credentials; verify GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET")
            raise HTTPException(
                status_code=500,
                detail="Google OAuth misconfigured. Bitte wenden Sie sich an den Administrator."
            )
        logger.error(f"Google callback HTTP error: {e} | {detail}")
        raise HTTPException(status_code=502, detail="OAuth exchange failed")
    except Exception as e:
        logger.error(f"Google callback error: {e}")
        raise HTTPException(status_code=500, detail="Callback failed")


@app.get("/api/auth/google/callback")
async def google_callback_api_alias(request: Request, code: Optional[str] = None, state: Optional[str] = None):
    return await google_callback(request=request, code=code, state=state)

@app.get("/auth/oauth/google/callback")
async def google_callback_legacy_auth(request: Request, code: Optional[str] = None, state: Optional[str] = None):
    return await google_callback(request=request, code=code, state=state)

@app.get("/api/auth/oauth/google/callback")
async def google_callback_api_legacy_auth(request: Request, code: Optional[str] = None, state: Optional[str] = None):
    return await google_callback(request=request, code=code, state=state)

@app.get("/auth/twitter/callback")
async def twitter_callback(code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None):
    if error:
        logger.warning(f"Twitter callback error param: {error}")
        return await _redirect("/")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    try:
        token_url = "https://api.twitter.com/2/oauth2/token"
        client_id = os.getenv("TWITTER_CLIENT_ID", "")
        client_secret = os.getenv("TWITTER_CLIENT_SECRET", "")
        redirect_uri = os.getenv("TWITTER_REDIRECT_URI", "")
        # Twitter requires Basic auth for token exchange with client_id:client_secret base64
        basic = httpx.BasicAuth(client_id, client_secret)
        async with httpx.AsyncClient(timeout=10, auth=basic) as client:
            token_res = await client.post(token_url, data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "code_verifier": state or "",
                "client_id": client_id,
            }, headers={"Content-Type": "application/x-www-form-urlencoded"})
            token_res.raise_for_status()
            tokens = token_res.json()
            access_token = tokens.get("access_token")
        # Get user info (v2)
        async with httpx.AsyncClient(timeout=10) as client:
            me = await client.get("https://api.twitter.com/2/users/me?user.fields=profile_image_url,name,username", headers={"Authorization": f"Bearer {access_token}"})
            me.raise_for_status()
            data = me.json().get("data", {})
        username = data.get("username") or "twitter_user"
        name = data.get("name") or username
        # Twitter usually does not return email; use username@twitter.local placeholder
        email = f"{username}@twitter.local"

        # Find or create
        existing_user = await db.get_user_by_email(email)
        if existing_user:
            user = existing_user
        else:
            compliant_pwd = _generate_compliant_password()
            password_hash = auth_service.hash_password(compliant_pwd)
            user = await db.create_user(email=email, name=name, role="assistant", password_hash=password_hash)

        token = auth_service.create_access_token(data={"sub": str(user.id)})
        session_id = str(uuid.uuid4())
        if cache_service:
            await cache_service.store_session(session_id, str(user.id), expires_in=86400)

        return await _redirect("/dashboard")
    except httpx.HTTPError as e:
        logger.error(f"Twitter callback HTTP error: {e}")
        raise HTTPException(status_code=502, detail="OAuth exchange failed")
    except Exception as e:
        logger.error(f"Twitter callback error: {e}")
        raise HTTPException(status_code=500, detail="Callback failed")

@app.post("/auth/login-test")
async def login_test(request: dict):
    """Test login endpoint with simple parameters"""
    email = request.get("email")
    password = request.get("password")
    logger.info(f"Login test called with email: {email}")
    
    try:
        user = await db.get_user_by_email(email)
        logger.info(f"User found: {user is not None}")
        
        if not user:
            return {"error": "User not found"}
        
        password_valid = auth_service.verify_password(password, user.password_hash)
        logger.info(f"Password valid: {password_valid}")
        
        if not password_valid:
            return {"error": "Invalid password"}
        
        if not user.is_active:
            return {"error": "User not active"}
        
        # Create JWT token
        token = auth_service.create_access_token(data={"sub": str(user.id)})
        logger.info("Token created successfully")
        
        payload = {
            "success": True,
            "token": token,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
        }
        response = JSONResponse(content=payload)
        _set_auth_cookies(response, token)
        return response
    except Exception as e:
        logger.error(f"Login test error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {"error": f"Exception: {str(e)}"}

@app.post("/auth/login")
async def login(request: dict, response: Response):
    """Authenticate user and return JWT token"""
    try:
        # Extract email and password from request
        email = request.get("email")
        password = request.get("password")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")
        
        logger.info(f"Login attempt for email: {email}")
        
        # Get user from database
        user = await db.get_user_by_email(email)
        if not user:
            logger.warning(f"User not found: {email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not auth_service.verify_password(password, user.password_hash):
            logger.warning(f"Invalid password for user: {email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Inactive user login attempt: {email}")
            raise HTTPException(status_code=401, detail="Account is disabled")
        
        # Create JWT token
        token = auth_service.create_access_token(data={"sub": str(user.id)})
        logger.info(f"JWT token created for user: {user.id}")
        
        # Store session
        session_id = str(uuid.uuid4())
        if cache_service:
            try:
                await cache_service.store_session(session_id, str(user.id), expires_in=86400)
                logger.info(f"Session stored for user: {user.id}")
            except Exception as e:
                logger.warning(f"Failed to store session in cache: {e}")
        
        # Set auth cookies
        _set_auth_cookies(response, token)
        try:
            await _reset_gmail_runtime_state(user.id)
        except Exception as reset_err:
            logger.debug("Failed to reset Gmail runtime state for user %s: %s", user.id, reset_err)
        # Clear any stale Gmail helper cookies carried over from another account
        try:
            response.delete_cookie(key="active_email_account", path="/")
        except Exception:
            pass
        
        # Return successful response
        return {
            "success": True,
            "token": token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register new user"""
    try:
        # Check if user already exists
        existing_user = await db.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        password_hash = auth_service.hash_password(user_data.password)
        user = await db.create_user(
            email=user_data.email,
            name=user_data.name,
            role=user_data.role or "assistant",
            password_hash=password_hash
        )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@app.post("/auth/register-full", response_model=LoginResponse)
async def register_full(payload: dict):
    """Register user with extended profile and return token in one step.
    Backward compatible: only creates profile fields if provided."""
    try:
        email = (payload.get("email") or "").strip().lower()
        name = (payload.get("name") or "").strip()
        password = payload.get("password") or ""
        profile_data = payload.get("profile") or {}

        if not email or not name or not password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields: email, name, password")

        # Enforce key lawyer profile fields
        required_profile_fields = ["firm", "phone", "roleTitle"]
        missing = [f for f in required_profile_fields if not (profile_data.get(f) or "").strip()]
        if missing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing required profile fields: {', '.join(missing)}")

        # Prevent duplicates
        existing_user = await db.get_user_by_email(email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        # Create user
        password_hash = auth_service.hash_password(password)
        user = await db.create_user(
            email=email,
            name=name,
            role="assistant",
            password_hash=password_hash
        )

        # Upsert profile if any fields provided
        from models import UserProfileUpdate
        try:
            profile = UserProfileUpdate(**{
                "first_name": profile_data.get("firstName"),
                "last_name": profile_data.get("lastName"),
                "firm": profile_data.get("firm"),
                "role_title": profile_data.get("roleTitle"),
                "bar_id": profile_data.get("barId"),
                "jurisdictions": profile_data.get("jurisdictions") or [],
                "practice_areas": profile_data.get("practiceAreas") or [],
                "phone": profile_data.get("phone"),
                "website": profile_data.get("website"),
                "marketing_opt_in": profile_data.get("marketingOptIn"),
                "consent_at": profile_data.get("consentAt"),
                "terms_accepted_at": profile_data.get("termsAcceptedAt"),
            })
            # Only persist if at least one value set
            if any(v not in (None, [], "") for v in profile.model_dump().values()):
                await db.upsert_user_profile(user.id, profile)
        except Exception as e:
            logger.warning(f"Profile upsert skipped: {e}")

        # Create token and session
        token = auth_service.create_access_token(data={"sub": str(user.id)})
        session_id = str(uuid.uuid4())
        if cache_service:
            await cache_service.store_session(session_id, str(user.id), expires_in=86400)

        payload = LoginResponse(
            token=token,
            user=UserResponse(id=user.id, email=user.email, name=user.name, role=user.role)
        )
        response = JSONResponse(content=json.loads(payload.model_dump_json()))
        _set_auth_cookies(response, token)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Register full error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")

@app.get("/api/user/profile", response_model=UserProfileResponse)
async def get_user_profile(current_user: UserInDB = Depends(get_current_user_flexible)):
    """Return the authenticated user's core profile details.

    This endpoint intentionally sources identity fields from the portal account
    (users table) to keep login identity independent from any linked email
    accounts. Optional extended profile fields are stored separately and can be
    exposed via dedicated endpoints if needed.
    """
    # Always reflect the portal (login) identity here
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        created_at=current_user.created_at,
        is_active=current_user.is_active,
    )

@app.post("/api/user/profile", response_model=UserProfileResponse)
async def upsert_user_profile(profile_data: UserProfileUpdate, current_user: UserInDB = Depends(get_current_user_flexible)):
    """Update extended profile data while keeping identity independent.

    Persist supplemental fields to `user_profiles.data`, but always return
    the portal account identity (email/name/role) to avoid any confusion with
    linked email accounts.
    """
    try:
        await db.upsert_user_profile(current_user.id, profile_data)
    except Exception:
        # Surface as 400 to indicate invalid payload without leaking internals
        raise HTTPException(status_code=400, detail="Profile update failed")
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        created_at=current_user.created_at,
        is_active=current_user.is_active,
    )

@app.get("/api/user/profile/extended", response_model=UserProfileExtendedResponse)
async def get_user_profile_extended(current_user: UserInDB = Depends(get_current_user_flexible)):
    """Return portal identity plus any extended profile data stored in user_profiles.data.

    Identity fields (email/name/role) always reflect the authenticated portal
    user and are not influenced by linked email accounts.
    """
    raw = None
    try:
        raw = await db.get_user_profile(current_user.id)
    except Exception as e:
        logger.debug(f"extended profile lookup failed: {e}")
    data_field: Optional[Dict[str, Any]] = None
    if raw:
        try:
            data_val = raw.get("data")
            if isinstance(data_val, str):
                data_field = json.loads(data_val)
            elif isinstance(data_val, dict):
                data_field = data_val
        except Exception:
            data_field = None
    return UserProfileExtendedResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        created_at=current_user.created_at,
        is_active=current_user.is_active,
        data=data_field,
    )

# Profile Picture Endpoints
@app.post("/api/user/profile/picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Upload and validate profile picture"""
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Ung?ltiges Format. Nur JPEG, PNG, WebP erlaubt."
            )
        
        # Read file content
        contents = await file.read()
        
        # Validate file size (2MB max)
        if len(contents) > 2 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Datei zu gro?. Maximum 2MB."
            )
        
        # Validate and process image with PIL
        try:
            image = Image.open(io.BytesIO(contents))

            # Verify it's actually an image by checking magic numbers
            image.verify()

            # Reopen for processing (verify closes the file)
            image = Image.open(io.BytesIO(contents))
            image = ImageOps.exif_transpose(image)

            # Ensure consistent mode for masking
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            # Center-crop to square before resizing to avoid letterboxing
            width, height = image.size
            min_edge = min(width, height)
            left = (width - min_edge) // 2
            top = (height - min_edge) // 2
            right = left + min_edge
            bottom = top + min_edge
            image = image.crop((left, top, right, bottom))

            # Resize to final dimensions
            image = image.resize((400, 400), Image.Resampling.LANCZOS)

            # Apply circular mask so uploaded avatars render as true circles
            mask = Image.new('L', (400, 400), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 400, 400), fill=255)
            output_image = Image.new('RGBA', (400, 400))
            output_image.paste(image, (0, 0), mask)

            # Save as PNG (preserves transparency from the circular mask)
            output = io.BytesIO()
            output_image.save(output, format='PNG', optimize=True)
            output.seek(0)
            
            # Convert to base64
            base64_image = base64.b64encode(output.read()).decode('utf-8')
            picture_data = f"data:image/png;base64,{base64_image}"
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise HTTPException(
                status_code=400,
                detail="Ung?ltige Bilddatei. Bitte eine g?ltige Bilddatei hochladen."
            )
        
        # Store in database
        success = await db.set_profile_picture(current_user.id, picture_data)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Fehler beim Speichern des Profilbilds."
            )
        
        return {
            "success": True,
            "message": "Profilbild erfolgreich hochgeladen",
            "profile_picture": picture_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading profile picture: {e}")
        raise HTTPException(
            status_code=500,
            detail="Upload fehlgeschlagen. Bitte erneut versuchen."
        )

@app.get("/api/user/profile/picture")
@app.get("/api/user/profile/picture")
async def get_profile_picture(current_user: UserInDB = Depends(get_current_user_flexible)):
    """Get current user's profile picture"""
    try:
        picture_data = await db.get_profile_picture(current_user.id)
        
        if not picture_data:
            # Return default avatar
            default_avatar_path = "/root/static/default-avatar.svg"
            if os.path.exists(default_avatar_path):
                with open(default_avatar_path, "rb") as f:
                    default_avatar_data = base64.b64encode(f.read()).decode('utf-8')
                return {
                    "success": True,
                    "profile_picture": f"data:image/svg+xml;base64,{default_avatar_data}"
                }
            else:
                # Fallback to simple default avatar data
                return {
                    "success": True,
                    "profile_picture": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI1MCIgZmlsbD0iI2NjY2NjYyIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iNDAiIHI9IjE1IiBmaWxsPSIjZmZmZmZmIi8+PHBhdGggZD0iTTUwIDYwIFE1MCA4MCAzMCA4NSBRNzAgODUgNTAgNjAiIGZpbGw9IiNmZmZmZmYiLz48L3N2Zz4="
                }
        
        return {
            "success": True,
            "profile_picture": picture_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile picture: {e}")
        raise HTTPException(
            status_code=500,
            detail="Interner Serverfehler"
        )
    except Exception as e:
        logger.error(f"Error getting profile picture: {e}")
        raise HTTPException(
            status_code=500,
            detail="Fehler beim Laden des Profilbilds"
        )

@app.delete("/api/user/profile/picture")
async def delete_profile_picture(current_user: UserInDB = Depends(get_current_user_flexible)):
    """Delete user's profile picture"""
    try:
        success = await db.delete_profile_picture(current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Fehler beim L?schen des Profilbilds"
            )
        
        return {
            "success": True,
            "message": "Profilbild entfernt"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profile picture: {e}")
        raise HTTPException(
            status_code=500,
            detail="Fehler beim L?schen des Profilbilds"
        )

# ============ GMAIL INTEGRATION ============


def _json_safe(value):
    """Recursively convert datetimes and unsupported types to JSON-safe values."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, Mapping):
        try:
            return {key: _json_safe(val) for key, val in dict(value).items()}
        except Exception:
            return {key: _json_safe(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(val) for key, val in value.items()}
    if isinstance(value, set):
        return [_json_safe(item) for item in value]
    return value


def _coerce_to_dict(value: Any) -> Tuple[Optional[Dict[str, Any]], bool]:
    """Return a plain dict representation of value (if possible) and whether sanitisation was required."""
    if value is None:
        return None, False
    if isinstance(value, dict):
        return dict(value), False
    if isinstance(value, Mapping):
        try:
            return dict(value), True
        except Exception:
            try:
                return {key: value[key] for key in value.keys()}, True
            except Exception:
                return {}, True
    if hasattr(value, "_asdict"):
        try:
            return dict(value._asdict()), True
        except Exception:
            pass
    if hasattr(value, "__dict__"):
        data = {
            key: getattr(value, key)
            for key in dir(value)
            if not key.startswith("_") and not callable(getattr(value, key))
        }
        return data, True
    return {}, True


def _normalize_gmail_account(account: Any) -> Tuple[Optional[Dict[str, Any]], bool]:
    """Normalise account payloads so downstream code works with predictable dicts."""
    account_dict, sanitised = _coerce_to_dict(account)
    if account_dict is None:
        return None, sanitised

    normalised = dict(account_dict)

    # Normalise identifiers
    if "id" in normalised:
        try:
            normalised["id"] = str(normalised["id"])
        except Exception:
            normalised["id"] = str(normalised.get("id"))

    # Drop user_id to avoid leaking internal ids
    normalised.pop("user_id", None)

    # Ensure booleans are proper bools
    for field in ("oauth_consent", "ai_read_consent", "draft_only_mode", "is_primary", "is_active"):
        if field in normalised and normalised[field] is not None:
            normalised[field] = bool(normalised[field])

    # Coerce timestamps to ISO strings where possible
    for ts_field in (
        "linked_at",
        "last_connected_at",
        "last_consent_update",
        "updated_at",
        "consent_timestamp",
        "ai_consent_revoked_at",
        "revoked_at",
    ):
        if ts_field in normalised and normalised[ts_field]:
            ts_value = normalised[ts_field]
            try:
                if isinstance(ts_value, datetime):
                    normalised[ts_field] = ts_value
                elif hasattr(ts_value, "isoformat"):
                    normalised[ts_field] = ts_value.isoformat()
                else:
                    normalised[ts_field] = datetime.fromisoformat(str(ts_value)).isoformat()
            except Exception:
                # Leave as-is; final JSON guard will stringify
                pass

    return normalised, sanitised


def _normalize_gmail_status(raw_status: Any, user_id: uuid.UUID) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Return a safe gmail status dict plus sanitisation metadata."""
    status_dict, root_sanitised = _coerce_to_dict(raw_status)
    if status_dict is None:
        status_dict = {}

    sanitisation_flags = {
        "root_sanitised": root_sanitised,
        "active_sanitised": False,
        "accounts_sanitised": 0,
    }

    accounts_payload = status_dict.get("accounts") or []
    normalised_accounts: List[Dict[str, Any]] = []
    for account in accounts_payload if isinstance(accounts_payload, (list, tuple, set)) else []:
        normalised_account, sanitised = _normalize_gmail_account(account)
        if normalised_account:
            normalised_accounts.append(normalised_account)
        if sanitised:
            sanitisation_flags["accounts_sanitised"] += 1

    active_account_raw = status_dict.get("active_account")
    normalised_active, active_sanitised = _normalize_gmail_account(active_account_raw)
    sanitisation_flags["active_sanitised"] = active_sanitised

    active_id = normalised_active.get("id") if normalised_active else None
    for account in normalised_accounts:
        account["is_active"] = bool(active_id and account.get("id") == active_id)

    connected = bool(normalised_active)
    oauth_consent = bool(normalised_active and normalised_active.get("oauth_consent"))
    ai_read_consent = bool(normalised_active and normalised_active.get("ai_read_consent"))
    draft_only_mode = bool(normalised_active.get("draft_only_mode")) if normalised_active else True
    consent_timestamp = normalised_active.get("consent_timestamp") if normalised_active else None

    normalised_status: Dict[str, Any] = {
        "connected": connected,
        "accounts": normalised_accounts,
        "active_account": normalised_active,
        "oauth_consent": oauth_consent,
        "ai_read_consent": ai_read_consent,
        "draft_only_mode": draft_only_mode,
        "consent_timestamp": consent_timestamp,
        "has_refresh_token": connected,
    }

    # Preserve other known fields if present
    for key in ("last_sync", "latest_error", "error_code"):
        if key in status_dict:
            normalised_status[key] = status_dict[key]

    return normalised_status, sanitisation_flags


async def _reset_gmail_runtime_state(user_id: uuid.UUID) -> None:
    """Best-effort reset of cached Gmail runtime state for the given user."""
    if not cache_service or not getattr(cache_service, "redis_client", None):
        return
    cache_keys = [
        f"gmail:status:{user_id}",
        f"gmail:messages:{user_id}",
        f"gmail:last_sync:{user_id}",
    ]
    for key in cache_keys:
        try:
            await cache_service.redis_client.delete(key)
        except Exception as redis_err:
            logger.debug("Failed to delete Gmail cache key %s: %s", key, redis_err)

@app.get("/api/user/gmail/status")
async def get_gmail_status(current_user: UserInDB = Depends(get_current_user_flexible)):
    """Get Gmail connection status for current user"""
    try:
        # Apply rate limiting (60 requests per hour per user)
        if not await _rate_limit(str(current_user.id), "gmail_status", 60, 3600):
            logger.warning(f"Rate limit exceeded for Gmail status check by user {current_user.id}")
            raise HTTPException(
                status_code=429,
                detail="Zu viele Anfragen. Bitte versuchen Sie es sp?ter erneut."
            )

        status = await db.get_gmail_connection_status(current_user.id)
        normalised_status, sanitisation_flags = _normalize_gmail_status(status, current_user.id)

        if any(sanitisation_flags.values()):
            logger.warning(
                "Gmail status sanitised for user %s (flags=%s)",
                current_user.id,
                sanitisation_flags,
            )

        safe_status = _json_safe(normalised_status)
        # Final guard: ensure any remaining unsupported types are stringified
        try:
            safe_status = json.loads(json.dumps(safe_status, default=str))
        except Exception as stringify_err:
            logger.error(
                "Failed to stringify Gmail status for user %s; returning minimal projection (%s)",
                current_user.id,
                stringify_err,
            )
            safe_status = {"connected": bool(normalised_status.get("connected")), "accounts": []}

        # Add cache-busting headers to prevent stale data
        response = JSONResponse(content=safe_status)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Gmail status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Fehler beim Abrufen des Gmail-Status"
        )

@app.post("/api/user/gmail/sync")
async def trigger_gmail_sync(
    folder: str = Query("inbox"),
    label: Optional[str] = Query(None),
    page_token: Optional[str] = Query(None, alias="pageToken"),
    limit: int = Query(50, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Manually trigger Gmail sync for current user."""
    try:
        # Rate limiting
        if not await _rate_limit(str(current_user.id), "gmail_sync", 10, 3600):
            logger.warning(f"Rate limit exceeded for Gmail sync by user {current_user.id}")
            raise HTTPException(
                status_code=429,
                detail="Zu viele Sync-Anfragen. Bitte versuchen Sie es sp?ter erneut."
            )
        
        # Get active account
        account = await db.get_active_email_account(current_user.id)
        if not account:
            raise HTTPException(
                status_code=401,
                detail="Kein verkn?pftes E-Mail-Konto ausgew?hlt"
            )
        
        if not account.get("ai_read_consent"):
            raise HTTPException(
                status_code=403,
                detail="Gmail-Zugriff nicht autorisiert. Bitte erteilen Sie die Lesezustimmung."
            )
        
        selected_folder = folder or "inbox"
        result = await _fetch_gmail_message_list(
            user_id=current_user.id,
            account=account,
            label=label,
            folder=selected_folder,
            limit=limit,
            page_token=page_token,
        )

        emails = result.get("emails", [])
        logger.info(
            "Gmail sync for user %s: %s messages from folder=%s (label=%s)",
            current_user.id,
            len(emails),
            selected_folder,
            result.get("label"),
        )

        return {
            "success": True,
            "synced": len(emails),
            "folder": selected_folder,
            "label": result.get("label"),
            "emails": emails,
            "total": result.get("total", len(emails)),
            "nextPageToken": result.get("nextPageToken", ""),
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gmail sync error for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Fehler bei der E-Mail-Synchronisation: {str(e)}"
        )



@app.get("/api/email/accounts")
async def list_email_accounts_api(current_user: UserInDB = Depends(get_current_user_flexible)):
    """Return linked email accounts for the current user."""
    accounts = await db.list_email_accounts(current_user.id)
    active_account = await db.get_active_email_account(current_user.id)

    def _serialize(account: Dict[str, Any]) -> Dict[str, Any]:
        data = dict(account)
        try:
            data["id"] = str(account["id"]) if "id" in account else data.get("id")
        except Exception:
            pass
        data.pop("user_id", None)
        for field in ("linked_at", "last_connected_at", "updated_at", "consent_timestamp", "ai_consent_revoked_at", "revoked_at"):
            if data.get(field):
                try:
                    data[field] = data[field].isoformat()
                except AttributeError:
                    pass
        return data

    serialized_accounts = [_serialize(account) for account in accounts]
    active_id = str(active_account["id"]) if active_account else None
    for account in serialized_accounts:
        account["is_active"] = account["id"] == active_id

    return {
        "accounts": serialized_accounts,
        "active_account_id": active_id,
    }

@app.post("/api/email/accounts/select")
async def select_email_account(
    payload: Dict[str, Any],
    response: Response,
    current_user: UserInDB = Depends(get_current_user_flexible),
):
    """Select the active email account for the current user."""
    raw_account_id = payload.get("account_id") or payload.get("accountId") or payload.get("id")
    if not raw_account_id:
        raise HTTPException(status_code=400, detail="account_id fehlt")
    try:
        account_uuid = uuid.UUID(str(raw_account_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Ung?ltige account_id")

    updated = await db.set_active_email_account(current_user.id, account_uuid)
    if not updated:
        raise HTTPException(status_code=404, detail="E-Mail-Konto nicht gefunden")

    response.set_cookie(
        key="active_email_account",
        value=str(account_uuid),
        httponly=False,
        secure=True,
        samesite="lax",
        max_age=86400,
        path="/",
    )
    return {"success": True, "active_account_id": str(account_uuid)}

@app.delete("/api/email/accounts/{account_id}")
async def delete_email_account(account_id: uuid.UUID, response: Response, current_user: UserInDB = Depends(get_current_user_flexible)):
    """Revoke a specific email account."""
    success = await db.revoke_email_account(current_user.id, account_id)
    if not success:
        raise HTTPException(status_code=404, detail="E-Mail-Konto nicht gefunden")
    response.delete_cookie(key="active_email_account", path="/")
    return {"success": True}

@app.post("/api/user/gmail/revoke")
async def revoke_gmail_access(
    payload: Optional[Dict[str, Any]] = None,
    current_user: UserInDB = Depends(get_current_user_flexible),
):
    """Revoke Gmail access for current user"""
    try:
        # Apply rate limiting (10 revoke requests per hour per user)
        if not await _rate_limit(str(current_user.id), "gmail_revoke", 10, 3600):
            logger.warning(f"Rate limit exceeded for Gmail revoke by user {current_user.id}")
            raise HTTPException(
                status_code=429,
                detail="Zu viele Anfragen. Bitte versuchen Sie es sp?ter erneut."
            )

        account_id_value: Optional[str] = None
        if isinstance(payload, dict):
            account_id_value = payload.get("account_id") or payload.get("accountId")
        account_uuid = uuid.UUID(account_id_value) if account_id_value else None

        success = await db.revoke_gmail_access(current_user.id, account_uuid)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Fehler beim Widerrufen des Gmail-Zugriffs"
            )

        from fastapi.responses import JSONResponse
        response = JSONResponse(content={
            "success": True,
            "message": "Gmail-Zugriff widerrufen"
        })

        response.delete_cookie(key="active_email_account", path="/")
        response.delete_cookie(key="email_link_uid", path="/")

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking Gmail access: {e}")
        raise HTTPException(
            status_code=500,
            detail="Fehler beim Widerrufen des Gmail-Zugriffs"
        )


@app.get("/api/email/labels")
async def list_email_labels(
    account_id: Optional[uuid.UUID] = Query(None),
    current_user: UserInDB = Depends(get_current_user_flexible),
):
    """List Gmail labels for the active email account."""
    try:
        if not await _rate_limit(str(current_user.id), "email_labels", 120, 3600):
            raise HTTPException(status_code=429, detail="Zu viele Anfragen. Bitte versuchen Sie es sp?ter erneut.")

        if account_id:
            account = await db.get_email_account(current_user.id, account_id)
            if not account:
                raise HTTPException(status_code=404, detail="E-Mail-Konto nicht gefunden")
            await db.set_active_email_account(current_user.id, account_id)
        else:
            account = await db.get_active_email_account(current_user.id)
        if not account:
            raise HTTPException(status_code=401, detail="Kein verkn?pftes E-Mail-Konto ausgew?hlt")

        refresh_token = await db.get_gmail_refresh_token(current_user.id, account.get("id"))
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Gmail-Token nicht gefunden")

        client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

        async with httpx.AsyncClient(timeout=30) as client:
            token_res = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if not token_res.is_success:
                raise HTTPException(status_code=401, detail="Gmail-Token-Aktualisierung fehlgeschlagen")
            access_token = token_res.json().get("access_token")

            gmail_res = await client.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/labels",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if not gmail_res.is_success:
                raise HTTPException(status_code=502, detail="Fehler beim Abrufen der Labels von Gmail")
            data = gmail_res.json()
        return {"success": True, "labels": data.get("labels", [])}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error listing Gmail labels: {exc}")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Gmail-Labels")


@app.post("/api/email/modify")
async def modify_email_labels(
    payload: Dict[str, Any],
    current_user: UserInDB = Depends(get_current_user_flexible),
):
    """Modify Gmail labels for a message."""
    try:
        if not await _rate_limit(str(current_user.id), "email_modify", 120, 3600):
            raise HTTPException(status_code=429, detail="Zu viele Anfragen. Bitte versuchen Sie es sp?ter erneut.")

        message_id = payload.get("id") or payload.get("message_id")
        if not message_id:
            raise HTTPException(status_code=400, detail="id fehlt")
        add_labels = payload.get("add") or []
        remove_labels = payload.get("remove") or []

        raw_account_id = payload.get("account_id") or payload.get("accountId")
        if raw_account_id:
            try:
                account_uuid = uuid.UUID(str(raw_account_id))
            except ValueError:
                raise HTTPException(status_code=400, detail="Ung?ltige account_id")
            account = await db.get_email_account(current_user.id, account_uuid)
            if not account:
                raise HTTPException(status_code=404, detail="E-Mail-Konto nicht gefunden")
            await db.set_active_email_account(current_user.id, account_uuid)
        else:
            account = await db.get_active_email_account(current_user.id)
        if not account:
            raise HTTPException(status_code=401, detail="Kein verkn?pftes E-Mail-Konto ausgew?hlt")

        refresh_token = await db.get_gmail_refresh_token(current_user.id, account.get("id"))
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Gmail-Token nicht gefunden")

        client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

        async with httpx.AsyncClient(timeout=30) as client:
            token_res = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if not token_res.is_success:
                raise HTTPException(status_code=401, detail="Gmail-Token-Aktualisierung fehlgeschlagen")
            access_token = token_res.json().get("access_token")

            gmail_res = await client.post(
                f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/modify",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"addLabelIds": add_labels, "removeLabelIds": remove_labels},
            )
            if not gmail_res.is_success:
                raise HTTPException(status_code=gmail_res.status_code, detail="Aktualisierung der Labels fehlgeschlagen")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error modifying Gmail labels: {exc}")
        raise HTTPException(status_code=500, detail="Fehler beim ?ndern der Gmail-Labels")


@app.post("/api/user/gmail/consent")
async def set_gmail_consent(
    consent: GmailConsentRequest,
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Persist Gmail consent preferences before OAuth redirect."""
    try:
        if not await _rate_limit(str(current_user.id), "gmail_consent", 30, 3600):
            logger.warning(f"Rate limit exceeded for Gmail consent by user {current_user.id}")
            raise HTTPException(
                status_code=429,
                detail="Zu viele Anfragen. Bitte versuchen Sie es sp?ter erneut."
            )

        success = await db.set_gmail_consent(
            current_user.id,
            oauth_consent=consent.oauth_consent,
            ai_read_consent=consent.ai_read_consent,
            draft_only_mode=consent.draft_only_mode,
        )

        pending = False
        if not success:
            pending = True
            await db.set_pending_gmail_consent(
                current_user.id,
                oauth_consent=consent.oauth_consent,
                ai_read_consent=consent.ai_read_consent,
                draft_only_mode=consent.draft_only_mode,
            )

        return {
            "success": True,
            "pending": pending,
            "message": "Zustimmungen gespeichert",
        }
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error storing Gmail consent: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error storing Gmail consent: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Speichern der Gmail-Zustimmungen: {str(e)}"
        )


@app.post("/api/domain-email/connections", response_model=DomainEmailConnectionResponse)
async def create_domain_email_connection(
    payload: DomainEmailConnectRequest,
    current_user: UserInDB = Depends(get_current_user_flexible),
):
    """Create a firm-domain email connector (IMAP/Graph)."""
    _assert_admin(current_user)
    if not payload.consent_mailbox or not payload.consent_ai:
        raise HTTPException(
            status_code=400,
            detail="Beide Zustimmungen (Mailbox-Zugriff und KI-Verarbeitung) sind erforderlich.",
        )
    protocol = payload.protocol.lower()
    if protocol != "imap":
        raise HTTPException(
            status_code=400,
            detail="Derzeit wird nur IMAP für Firmenkonten unterstützt.",
        )

    await _verify_domain_imap_credentials(
        host=payload.host,
        port=payload.port,
        username=payload.username,
        password=payload.password,
        use_ssl=payload.use_ssl,
    )

    record = await db.create_domain_email_account(
        current_user.id,
        email_address=str(payload.email),
        host=payload.host,
        port=payload.port,
        username=payload.username,
        password=payload.password,
        use_ssl=payload.use_ssl,
        protocol=protocol,
        mailbox_access_consent=payload.consent_mailbox,
        ai_read_consent=payload.consent_ai,
        status="connected",
        verified_at=datetime.utcnow(),
    )
    return DomainEmailConnectionResponse(
        id=record["id"],
        email=record["email_address"],
        host=record["host"],
        port=record["port"],
        username=record["username"],
        use_ssl=record["use_ssl"],
        protocol=record["protocol"],
        mailbox_access_consent=record["mailbox_access_consent"],
        ai_read_consent=record["ai_read_consent"],
        last_verified_at=record["last_verified_at"],
        last_status=record["last_status"],
        created_at=record["created_at"],
        updated_at=record["updated_at"],
    )


@app.get("/api/domain-email/connections")
async def list_domain_email_connections(
    current_user: UserInDB = Depends(get_current_user_flexible),
):
    """List firm-domain email connectors for the current admin."""
    _assert_admin(current_user)
    records = await db.list_domain_email_accounts(current_user.id)
    payload = [
        DomainEmailConnectionResponse(
            id=record["id"],
            email=record["email_address"],
            host=record["host"],
            port=record["port"],
            username=record["username"],
            use_ssl=record["use_ssl"],
            protocol=record["protocol"],
            mailbox_access_consent=record["mailbox_access_consent"],
            ai_read_consent=record["ai_read_consent"],
            last_verified_at=record["last_verified_at"],
            last_status=record["last_status"],
            created_at=record["created_at"],
            updated_at=record["updated_at"],
        )
        for record in records
    ]
    return {"connections": payload}


@app.delete("/api/domain-email/connections/{connection_id}")
async def delete_domain_email_connection(
    connection_id: uuid.UUID,
    current_user: UserInDB = Depends(get_current_user_flexible),
):
    """Remove a firm-domain email connector."""
    _assert_admin(current_user)
    deleted = await db.delete_domain_email_account(connection_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Domain-E-Mail-Verbindung nicht gefunden")
    return {"success": True}

@app.get("/api/test")
async def test_endpoint():
    return {"message": "test"}


EMAIL_FOLDER_LABELS = {
    "inbox": "INBOX",
    "starred": "STARRED",
    "flagged": "STARRED",
    "sent": "SENT",
    "drafts": "DRAFT",
    "trash": "TRASH",
    "spam": "SPAM",
    "archive": "ARCHIVE",
    "all": "ALL",
}


def _extract_header(headers: List[Dict[str, str]], name: str) -> str:
    """Best-effort header lookup with case-insensitive matching."""
    if not headers:
        return ""
    lower = name.lower()
    for header in headers:
        header_name = header.get("name", "")
        if header_name.lower() == lower:
            return header.get("value", "") or ""
    return ""


def _payload_has_attachments(payload: Dict[str, Any]) -> bool:
    """Recursively inspect payload parts for attachments."""
    if not payload:
        return False
    stack = [payload]
    while stack:
        part = stack.pop()
        filename = part.get("filename")
        body = part.get("body") or {}
        if filename and body.get("attachmentId"):
            return True
        stack.extend(part.get("parts") or [])
    return False


async def _fetch_gmail_message_list(
    *,
    user_id: uuid.UUID,
    account: Dict[str, Any],
    label: Optional[str],
    folder: Optional[str],
    limit: int,
    page_token: Optional[str],
) -> Dict[str, Any]:
    """Fetch Gmail messages (metadata) for the given account using stored refresh token."""
    refresh_token = await db.get_gmail_refresh_token(user_id, account.get("id"))
    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Gmail-Token nicht gefunden",
        )

    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

    resolved_label = label or None
    folder_slug = (folder or "").strip().lower() or None
    if not resolved_label and folder_slug:
        resolved_label = EMAIL_FOLDER_LABELS.get(folder_slug)
    if not resolved_label:
        resolved_label = "INBOX"

    label_upper = (resolved_label or "").upper()
    page_token = page_token or None
    limit = max(1, min(limit or 20, 100))

    async with httpx.AsyncClient(timeout=30) as client:
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if not token_res.is_success:
            logger.error(
                "Gmail token refresh failed for user %s account %s: %s",
                user_id,
                account.get("id"),
                token_res.text,
            )
            raise HTTPException(
                status_code=401,
                detail="Gmail-Token-Aktualisierung fehlgeschlagen",
            )

        access_token = token_res.json().get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=401,
                detail="Gmail-Token-Aktualisierung fehlgeschlagen",
            )

        gmail_params: Dict[str, Any] = {"maxResults": limit}
        if page_token:
            gmail_params["pageToken"] = page_token

        if label_upper == "ARCHIVE":
            gmail_params["q"] = "-label:INBOX"
        elif label_upper and label_upper not in {"ALL"}:
            gmail_params["labelIds"] = [label_upper]

        gmail_res = await client.get(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages",
            headers={"Authorization": f"Bearer {access_token}"},
            params=gmail_params,
        )

        if not gmail_res.is_success:
            logger.error(
                "Gmail list API failed for user %s account %s: %s",
                user_id,
                account.get("id"),
                gmail_res.text,
            )
            raise HTTPException(
                status_code=502,
                detail="Fehler beim Abrufen der E-Mails von Gmail",
            )

        email_list_data = gmail_res.json()
        next_page_token = email_list_data.get("nextPageToken") or ""
        messages_raw = email_list_data.get("messages", []) or []
        message_ids = [msg.get("id") for msg in messages_raw if msg.get("id")]

        if not message_ids:
            return {
                "success": True,
                "emails": [],
                "total": email_list_data.get("resultSizeEstimate") or 0,
                "nextPageToken": next_page_token,
                "label": label_upper,
            }

        detail_tasks = [
            client.get(
                f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
                headers={"Authorization": f"Bearer {access_token}"},
                params={
                    "format": "metadata",
                    "metadataHeaders": ["From", "Subject", "Date", "To"],
                },
            )
            for msg_id in message_ids
        ]

        detail_results = await asyncio.gather(*detail_tasks, return_exceptions=True)

        emails: List[Dict[str, Any]] = []
        for msg_id, msg_res in zip(message_ids, detail_results):
            if isinstance(msg_res, Exception):
                logger.warning("Failed to load Gmail message %s: %s", msg_id, msg_res)
                continue
            if not getattr(msg_res, "is_success", False):
                logger.warning(
                    "Gmail message %s returned %s",
                    msg_id,
                    getattr(msg_res, "status_code", "unknown"),
                )
                continue

            msg_data = msg_res.json()
            payload = msg_data.get("payload", {}) or {}
            headers = payload.get("headers", []) or []

            sender_raw = _extract_header(headers, "From") or "Unbekannt"
            subject = _extract_header(headers, "Subject") or "(Kein Betreff)"
            date_header = _extract_header(headers, "Date")

            sender_match = re.search(r"(.*)<(.*)>", sender_raw)
            if sender_match:
                sender_name = sender_match.group(1).strip().strip('"') or sender_match.group(2).strip()
                sender_email = sender_match.group(2).strip()
            else:
                parsed_name, parsed_email = parseaddr(sender_raw)
                sender_name = parsed_name or sender_raw
                sender_email = parsed_email or sender_raw

            label_ids = msg_data.get("labelIds") or []
            internal_date = msg_data.get("internalDate")
            date_iso = date_header
            if internal_date:
                try:
                    timestamp = datetime.fromtimestamp(int(internal_date) / 1000, tz=timezone.utc)
                    date_iso = timestamp.isoformat()
                except (ValueError, TypeError):
                    pass

            emails.append(
                {
                    "id": msg_id,
                    "threadId": msg_data.get("threadId"),
                    "labelIds": label_ids,
                    "senderName": sender_name,
                    "senderEmail": sender_email,
                    "subject": subject,
                    "snippet": msg_data.get("snippet", ""),
                    "date": date_iso or "",
                    "unread": "UNREAD" in label_ids,
                    "starred": "STARRED" in label_ids,
                    "hasAttachment": _payload_has_attachments(payload),
                }
            )

        return {
            "success": True,
            "emails": emails,
            "total": email_list_data.get("resultSizeEstimate") or len(emails),
            "nextPageToken": next_page_token,
            "label": label_upper,
        }



async def _summarize_email_for_user(
    current_user: UserInDB,
    email_id: Optional[str],
    subject: Optional[str],
    body_text: Optional[str],
    refresh: bool = False,
) -> Dict[str, Any]:
    if not body_text and not subject:
        raise HTTPException(status_code=400, detail="Keine E-Mail-Inhalte vorhanden")

    cached_payload = None
    if email_id and not refresh:
        cached_payload = await db.get_email_summary(current_user.id, email_id)
        if cached_payload:
            return {
                "success": True,
                "summary": cached_payload["summary"],
                "model": cached_payload["summary"].get("model"),
                "cached": True,
                "cached_at": cached_payload.get("created_at"),
            }

    ai_response = await ai_service.summarize_email_message(subject, body_text)
    summary_raw = ai_response.content or ""
    summary_payload: Dict[str, Any]
    try:
        summary_payload = json.loads(summary_raw)
    except Exception:
        summary_payload = {
            "summary_points": [summary_raw.strip()] if summary_raw.strip() else [],
            "raw": summary_raw,
        }

    model_used = ai_response.model_used or ai_response.model
    summary_payload.setdefault("model", model_used)

    if email_id:
        try:
            await db.upsert_email_summary(current_user.id, email_id, summary_payload)
        except Exception as cache_error:
            logger.warning(f"Could not cache email summary for {email_id}: {cache_error}")

    return {
        "success": True,
        "summary": summary_payload,
        "model": model_used,
        "usage": getattr(ai_response, "usage", {}),
        "cached": False,
    }


async def _fetch_gmail_message_contents(
    current_user: UserInDB,
    email_id: str,
    account_id: Optional[uuid.UUID] = None,
) -> Dict[str, Any]:
    if not email_id:
        raise HTTPException(status_code=400, detail="email_id erforderlich")

    if account_id:
        try:
            account_uuid = uuid.UUID(str(account_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Ung?ltige account_id")
        account = await db.get_email_account(current_user.id, account_uuid)
        if not account:
            raise HTTPException(status_code=404, detail="E-Mail-Konto nicht gefunden")
        await db.set_active_email_account(current_user.id, account_uuid)
    else:
        account = await db.get_active_email_account(current_user.id)
    if not account:
        raise HTTPException(status_code=401, detail="Kein verkn?pftes E-Mail-Konto ausgew?hlt")

    refresh_token = await db.get_gmail_refresh_token(current_user.id, account.get("id"))
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Gmail-Token nicht gefunden")

    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

    async with httpx.AsyncClient(timeout=30) as client:
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if not token_res.is_success:
            raise HTTPException(status_code=401, detail="Gmail-Token-Aktualisierung fehlgeschlagen")

        tokens = token_res.json()
        access_token = tokens.get("access_token")

        gmail_res = await client.get(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{email_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"format": "full"},
        )

        if not gmail_res.is_success:
            raise HTTPException(
                status_code=502,
                detail="Fehler beim Abrufen der E-Mail von Gmail",
            )

        email_data = gmail_res.json()

    def extract_body(payload):
        if "body" in payload and payload["body"].get("data"):
            import base64

            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    if "data" in part.get("body", {}):
                        import base64

                        return base64.urlsafe_b64decode(part["body"]["data"]).decode(
                            "utf-8", errors="ignore"
                        )
                result = extract_body(part)
                if result:
                    return result
        return ""

    body_text = extract_body(email_data.get("payload", {}))
    headers = email_data.get("payload", {}).get("headers", [])
    subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "")

    max_length = 4000
    if len(body_text) > max_length:
        body_text = body_text[:max_length] + "..."

    return {
        "subject": subject,
        "body": body_text,
        "account": account,
    }


@app.get("/api/email/list")
async def list_emails(
    account_id: Optional[uuid.UUID] = Query(None),
    label: Optional[str] = Query(None),
    page_token: Optional[str] = Query(None, alias="pageToken"),
    limit: int = Query(20, ge=1, le=100),
    folder: Optional[str] = Query(None),
    current_user: UserInDB = Depends(get_current_user_flexible),
):
    """List emails from Gmail for current user"""
    try:
        if account_id:
            account = await db.get_email_account(current_user.id, account_id)
            if not account:
                raise HTTPException(status_code=404, detail="E-Mail-Konto nicht gefunden")
            await db.set_active_email_account(current_user.id, account_id)
        else:
            account = await db.get_active_email_account(current_user.id)
        if not account:
            raise HTTPException(status_code=401, detail="Kein verkn?pftes E-Mail-Konto ausgew?hlt")

        result = await _fetch_gmail_message_list(
            user_id=current_user.id,
            account=account,
            label=label,
            folder=folder,
            limit=limit,
            page_token=page_token,
        )

        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing emails: {e}")
        raise HTTPException(
            status_code=500,
            detail="Fehler beim Abrufen der E-Mails"
        )


@app.post("/api/email/process")
async def process_email_with_ai(
    request: dict,
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Process email with AI for summarization and categorization"""
    try:
        # Apply rate limiting (30 AI email processing requests per hour per user)
        if not await _rate_limit(str(current_user.id), "email_ai_process", 30, 3600):
            logger.warning(f"Rate limit exceeded for email AI processing by user {current_user.id}")
            raise HTTPException(
                status_code=429,
                detail="Zu viele AI-Verarbeitungsanfragen. Bitte versuchen Sie es sp?ter erneut."
            )

        email_id = request.get("email_id")
        if not email_id:
            raise HTTPException(status_code=400, detail="email_id erforderlich")
        refresh_summary = bool(request.get("refresh"))

        if email_id and not refresh_summary:
            cached = await db.get_email_summary(current_user.id, email_id)
            if cached:
                return {
                    "success": True,
                    "summary": cached["summary"],
                    "model": cached["summary"].get("model"),
                    "cached": True,
                    "cached_at": cached.get("created_at"),
                }

        account_hint = request.get("account_id") or request.get("accountId")
        gmail_payload = await _fetch_gmail_message_contents(
            current_user=current_user,
            email_id=email_id,
            account_id=account_hint,
        )
        subject = gmail_payload["subject"]
        body_text = gmail_payload["body"]

        summary_payload = await _summarize_email_for_user(
            current_user=current_user,
            email_id=email_id,
            subject=subject,
            body_text=body_text,
            refresh=refresh_summary,
        )
        summary_payload["subject"] = subject
        summary_payload["body_excerpt"] = body_text[:500]
        return summary_payload
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing email with AI: {e}")
        raise HTTPException(
            status_code=500,
            detail="Fehler bei der E-Mail-Verarbeitung"
        )


@app.post("/api/email/summarize")
async def summarize_email_endpoint(
    payload: EmailSummarizeRequest,
    current_user: UserInDB = Depends(get_current_user_flexible),
):
    """Summarize email content using Together AI (or configured provider)."""
    try:
        if not await _rate_limit(str(current_user.id), "email_ai_process", 30, 3600):
            raise HTTPException(
                status_code=429,
                detail="Zu viele AI-Verarbeitungsanfragen. Bitte versuchen Sie es sp?ter erneut.",
            )

        email_id = payload.email_id
        subject = payload.subject
        body_text = payload.body

        if email_id and not body_text:
            gmail_payload = await _fetch_gmail_message_contents(
                current_user=current_user,
                email_id=email_id,
                account_id=payload.account_id,
            )
            subject = subject or gmail_payload.get("subject")
            body_text = gmail_payload.get("body")

        summary_payload = await _summarize_email_for_user(
            current_user=current_user,
            email_id=email_id,
            subject=subject,
            body_text=body_text,
            refresh=payload.refresh,
        )
        if subject:
            summary_payload.setdefault("subject", subject)
        if body_text:
            summary_payload.setdefault("body_excerpt", body_text[:500])
        return summary_payload
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Email summarize endpoint error: {exc}")
        raise HTTPException(status_code=500, detail="Zusammenfassung fehlgeschlagen")


@app.post("/api/email/reply")
async def generate_email_reply(
    payload: EmailReplyRequest,
    current_user: UserInDB = Depends(get_current_user_flexible),
):
    """Generate a German legal reply draft for an email."""
    try:
        # Rate limit reply drafts (20/hr)
        if not await _rate_limit(str(current_user.id), "email_ai_reply", 20, 3600):
            raise HTTPException(status_code=429, detail="Zu viele Entwurfsanfragen. Bitte kurz warten.")

        subject = (payload.subject or "").strip()
        body_text = (payload.body or "").strip()
        if payload.email_id and not body_text:
            gmail_payload = await _fetch_gmail_message_contents(
                current_user=current_user,
                email_id=payload.email_id,
                account_id=payload.account_id,
            )
            subject = subject or gmail_payload.get("subject") or ""
            body_text = gmail_payload.get("body") or ""

        if not subject and not body_text:
            raise HTTPException(status_code=400, detail="E-Mail-Inhalt fehlt")

        # Compose reply prompt
        tone_hint = {
            "legal": "Juristisch pr?zise, formell (Sie-Form)",
            "legal+plain": "Juristisch pr?zise, zugleich gut lesbar (Sie-Form)",
            "plain": "Einfach und klar (Sie-Form)",
            "neutral": "Neutral und sachlich (Sie-Form)",
        }.get((payload.tone or "legal").lower(), "Juristisch pr?zise, formell (Sie-Form)")

        prompt = f"""
[task:email_reply][language:de]
Formuliere eine professionelle Antwort-E-Mail in der Sie-Form.

ANFORDERUNGEN:
- Ton: {tone_hint}
- Enth?lt: h?fliche Anrede, Bezug auf Anliegen, klare Antwort/Schritte, h?flicher Abschluss.
- Keine vertraulichen Daten erfinden; keine rechtlich verbindlichen Zusagen ohne Kontext.
- Ausgabe: Nur der E-Mail-Text (ohne JSON, ohne Markdown).

BETREFF: {subject or '(kein Betreff)'}

ORIGINALTEXT (Auszug):
{body_text[:12000]}
""".strip()

        ai_resp = await ai_service.generate_completion(
            prompt=prompt,
            model=payload.model,
            max_tokens=700,
            temperature=0.25,
        )
        reply_text = (ai_resp.content or "").strip()
        reply_subject = f"Re: {subject}" if subject else "Antwort"
        return {
            "success": True,
            "subject": reply_subject,
            "reply": reply_text,
            "model": ai_resp.model_used or ai_resp.model,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Email reply generation failed: {exc}")
        raise HTTPException(status_code=500, detail="Antwortentwurf fehlgeschlagen")


@app.post("/api/email/to-document")
async def email_to_document(
    payload: EmailToDocumentRequest,
    current_user: UserInDB = Depends(get_current_user_flexible),
):
    """Generate a legal document from an email and save it."""
    try:
        # Rate limit (10/hr)
        if not await _rate_limit(str(current_user.id), "email_to_document", 10, 3600):
            raise HTTPException(status_code=429, detail="Zu viele Dokumenterstellungen. Bitte kurz warten.")

        subject = (payload.subject or "").strip()
        body_text = (payload.body or "").strip()
        if payload.email_id and not body_text:
            gmail_payload = await _fetch_gmail_message_contents(
                current_user=current_user,
                email_id=payload.email_id,
                account_id=payload.account_id,
            )
            subject = subject or gmail_payload.get("subject") or ""
            body_text = gmail_payload.get("body") or ""

        if not subject and not body_text:
            raise HTTPException(status_code=400, detail="E-Mail-Inhalt fehlt")

        doc_type = (payload.document_type or "email-briefing").strip().lower()
        title = (payload.title or subject or "Dokument aus E-Mail").strip()

        instructions = f"Aus der folgenden E-Mail ist ein juristisches Dokument zu erstellen. Betreff: {subject or '(kein Betreff)'}\n\nE-Mail-Inhalt:\n{body_text[:15000]}"

        ai_doc = await ai_service.generate_document(
            document_type=doc_type,
            title=title,
            instructions=instructions,
            tone="legal",
            model=payload.model,
            fail_hard=False,
        )

        # Try to parse JSON result for title/content
        raw = ai_doc.content or ""
        doc_title = title
        doc_content = raw
        try:
            parsed = json.loads(raw)
            doc_title = (parsed.get("title") or doc_title).strip()
            doc_content = parsed.get("content") or raw
        except Exception:
            pass

        created = await db.create_document(
            user_id=current_user.id,
            title=doc_title or title,
            content=doc_content or "",
            document_type=doc_type,
        )
        doc_id = created.get("id")
        download = {}
        if doc_id:
            download = {
                "docx": f"/api/documents/{doc_id}/export?format=docx",
                "pdf": f"/api/documents/{doc_id}/export?format=pdf",
            }
        return {
            "success": True,
            "documentId": doc_id,
            "title": created.get("title", doc_title),
            "download": download,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Email to document generation failed: {exc}")
        raise HTTPException(status_code=500, detail="Dokumenterstellung fehlgeschlagen")


@app.post("/api/chat")
async def together_chat_endpoint(
    payload: ChatSessionRequest,
    current_user: UserInDB = Depends(get_current_user_flexible),
):
    """Conversational chat endpoint backed by Together AI integration."""
    try:
        if not payload.messages:
            raise HTTPException(status_code=400, detail="messages erforderlich")
        latest = payload.messages[-1]
        if latest.role != "user":
            raise HTTPException(status_code=400, detail="Letzte Nachricht muss vom Nutzer stammen")
        if not latest.content.strip():
            raise HTTPException(status_code=400, detail="Nachricht darf nicht leer sein")

        if not await _rate_limit(str(current_user.id), "together_chat", 20, 3600):
            raise HTTPException(
                status_code=429,
                detail="Zu viele Chat-Anfragen. Bitte warten Sie kurz.",
            )

        session_uuid = None
        if payload.session_id and not payload.reset:
            try:
                session_uuid = uuid.UUID(str(payload.session_id))
            except ValueError:
                raise HTTPException(status_code=400, detail="Ung?ltige session_id")

        if payload.reset:
            session_uuid = None

        session_id = await db.get_or_create_chat_session(
            user_id=current_user.id,
            session_id=session_uuid,
            title=payload.title,
        )

        # Persist user message
        await db.add_chat_message(
            session_id=session_id,
            user_id=current_user.id,
            role="user",
            content=latest.content.strip(),
            metadata={"source": "portal", "model": payload.model},
        )

        history_records = await db.get_chat_history(session_id, current_user.id, limit=40)
        ai_messages: List[Dict[str, str]] = [
            {"role": record["role"], "content": record["content"]}
            for record in history_records
        ]

        ai_response = await ai_service.chat_completion(
            messages=ai_messages,
            model=payload.model,
            temperature=payload.temperature or 0.6,
        )
        assistant_text = (ai_response.content or "").strip()

        message_id = await db.add_chat_message(
            session_id=session_id,
            user_id=current_user.id,
            role="assistant",
            content=assistant_text,
            metadata={
                "model": ai_response.model_used or payload.model,
                "usage": getattr(ai_response, "usage", {}),
            },
        )

        return {
            "session_id": str(session_id),
            "message_id": str(message_id),
            "content": assistant_text,
            "model": ai_response.model_used or payload.model,
            "usage": getattr(ai_response, "usage", {}),
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Chat endpoint error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Chat fehlgeschlagen")


@app.post("/api/documents/analyze")
async def analyze_document_endpoint(
    payload: DocumentAnalyzeRequest,
    current_user: UserInDB = Depends(get_current_user_flexible),
):
    """Analyze uploaded document content and extract legal insights."""
    try:
        if not payload.content or not payload.content.strip():
            raise HTTPException(status_code=400, detail="content erforderlich")

        if not await _rate_limit(str(current_user.id), "document_analyze", 15, 3600):
            raise HTTPException(
                status_code=429,
                detail="Zu viele Analyse-Anfragen. Bitte versuchen Sie es sp?ter erneut.",
            )

        ai_response = await ai_service.analyze_document_text(
            title=payload.title,
            document_text=payload.content,
            categories=payload.categories,
            max_tokens=1100,
        )

        raw_content = ai_response.content or ""
        try:
            analysis_payload = json.loads(raw_content)
        except json.JSONDecodeError:
            analysis_payload = {"analysis": raw_content}

        return {
            "success": True,
            "analysis": analysis_payload,
            "model": ai_response.model_used or payload.model,
            "usage": getattr(ai_response, "usage", {}),
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Document analysis error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Dokumentanalyse fehlgeschlagen")

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(request: Request, response: Response):
    """Get current user information with cookie or Authorization fallback."""
    # Prefer Authorization header; fallback to sid cookie set during OAuth
    token = None
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
    if not token:
        token = request.cookies.get("auth_token")
    if not token:
        token = request.cookies.get("anwalts_auth_token")
    session_cookie_name = os.getenv("SESSION_COOKIE_NAME", "sid")
    public_cookie_name = os.getenv("PUBLIC_SESSION_COOKIE", "sat")
    if not token:
        token = request.cookies.get(session_cookie_name)
    if not token:
        # Fallback to non-HttpOnly public session cookie
        token = request.cookies.get(public_cookie_name)
    cookie_token_present = any(
        [
            bool(request.cookies.get("auth_token")),
            bool(request.cookies.get("anwalts_auth_token")),
            bool(request.cookies.get(session_cookie_name)),
        ]
    )
    logger.info(
        "[auth_me] has_auth_header=%s has_token_cookie=%s has_sat_cookie=%s",
        bool(auth_header),
        cookie_token_present,
        bool(request.cookies.get(public_cookie_name)),
    )
    if not token:
        logger.warning("[auth_me] no token found in header or cookies")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    try:
        payload = auth_service.verify_token(token)
        user = await db.get_user_by_id(payload.get("sub"))
        if not user:
            logger.warning("[auth_me] user not found for sub=%s", payload.get("sub"))
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    except HTTPException:
        raise
    except Exception:
        logger.exception("[auth_me] token verification failed")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

    # Best-effort avatar from email (identicon)
    avatar = None
    try:
        import hashlib
        md5 = hashlib.md5(user.email.strip().lower().encode()).hexdigest()
        avatar = f"https://www.gravatar.com/avatar/{md5}?d=identicon"
    except Exception:
        pass
    # No-store to avoid stale identity
    response.headers["Cache-Control"] = "no-store"
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        avatarUrl=avatar
    )

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info_api(request: Request, response: Response):
    """API alias to support frontend fetches under /api namespace."""
    return await get_current_user_info(request, response)

# Lightweight guard endpoint for client-side check
@app.get("/auth/validate")
async def validate_token(current_user: UserInDB = Depends(get_current_user)):
    return {"valid": True, "user": {"id": str(current_user.id), "email": current_user.email, "name": current_user.name, "role": current_user.role}}

# Dashboard helper: lightweight user roster (admin/assistant overview)
@app.get("/api/auth/users")
async def list_recent_users(
    limit: int = 5,
    current_user: UserInDB = Depends(get_current_user_flexible),
):
    try:
        limit = max(1, min(limit, 25))
        rows = await db.list_recent_users(limit)
        users = []
        for row in rows:
            avatar = None
            try:
                md5 = hashlib.md5(row["email"].strip().lower().encode()).hexdigest()
                avatar = f"https://www.gravatar.com/avatar/{md5}?d=identicon"
            except Exception:
                pass
            user_payload = UserResponse(
                id=row["id"],
                email=row["email"],
                name=row.get("name") or row["email"],
                role=row.get("role") or "assistant",
                avatarUrl=avatar,
            ).model_dump()
            users.append(user_payload)
        return {"users": users}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"list_recent_users error: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to load users")

# ============ TEMPLATE ENDPOINTS ============

# Logout endpoint to revoke token (blacklist) and clear auth cookies
@app.post("/auth/logout")
async def logout(response: Response, request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Revoke token and clear cookies to fully sign the user out."""
    try:
        token = credentials.credentials
        # Blacklist the token (access token)
        auth_service.blacklist_token(token)

        # Clear cookies set during OAuth login
        session_cookie = os.getenv("SESSION_COOKIE_NAME", "sid")
        public_cookie = os.getenv("PUBLIC_SESSION_COOKIE", "sat")
        cookie_domain = os.getenv("SESSION_DOMAIN", "portal-anwalts.ai")

        # Primary delete with explicit domain
        response.delete_cookie(key=session_cookie, domain=cookie_domain, path="/")
        response.delete_cookie(key=public_cookie, domain=cookie_domain, path="/")
        response.delete_cookie(key="auth_token", domain=cookie_domain, path="/")
        response.delete_cookie(key="anwalts_auth_token", domain=cookie_domain, path="/")
        response.delete_cookie(key="user_id", domain=cookie_domain, path="/")
        response.delete_cookie(key="active_email_account", domain=cookie_domain, path="/")
        response.delete_cookie(key="email_link_uid", domain=cookie_domain, path="/")

        # Best-effort delete without domain (host-only), in case attributes differ
        try:
            response.delete_cookie(key=session_cookie, path="/")
            response.delete_cookie(key=public_cookie, path="/")
            response.delete_cookie(key="auth_token", path="/")
            response.delete_cookie(key="anwalts_auth_token", path="/")
            response.delete_cookie(key="user_id", path="/")
            response.delete_cookie(key="active_email_account", path="/")
            response.delete_cookie(key="email_link_uid", path="/")
        except Exception:
            pass

        try:
            payload = auth_service.verify_token(token)
            sub = payload.get("sub")
            if sub:
                await _reset_gmail_runtime_state(uuid.UUID(str(sub)))
        except Exception as reset_err:
            logger.debug("Failed to clear Gmail cache during logout: %s", reset_err)

        return {"success": True}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"success": False}

@app.get("/api/dashboard/summary")
async def get_dashboard_summary_api(
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Get complete dashboard summary for current user"""
    try:
        # Get dashboard stats
        summary = await db.get_dashboard_summary(current_user.id)
        
        # Fetch recent documents (limit 5)
        async with db.get_connection() as conn:
            docs_rows = await conn.fetch(
                """
                SELECT id, title, updated_at, created_at, status
                FROM documents
                WHERE user_id = $1
                ORDER BY updated_at DESC NULLS LAST, created_at DESC
                LIMIT 5
                """,
                current_user.id
            )
            
            recent_documents = []
            for row in docs_rows:
                recent_documents.append({
                    "id": str(row['id']),
                    "title": row['title'] or "Untitled Document",
                    "updated_at": row['updated_at'].isoformat() if row['updated_at'] else row['created_at'].isoformat(),
                    "status": row['status'] or "draft",
                    "progress": 50,  # Default progress
                    "statusType": "info",
                    "details": ""
                })
        
        # Return data in format expected by frontend
        return {
            "stats": {
                "newCases": summary.get("new_cases", 0),
                "documents": summary.get("documents_total", 0),
                "emails": summary.get("emails_total", 0),
                "nextDeadline": summary.get("next_deadline")
            },
            "recentDocuments": recent_documents,
            "upcomingDeadlines": [],  # TODO: Implement proper deadlines
            "recentActivity": [],  # Removed as requested
            "continueSuggestion": None,  # TODO: Implement continue suggestion
            "user": {
                "name": current_user.name,
                "email": current_user.email
            },
            "warnings": []
        }
    except Exception as e:
        logger.error(f"Dashboard summary error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard summary"
        )

@app.get("/api/templates", response_model=List[TemplateResponse])
async def get_templates(
    category: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Get user templates with optional category filter"""
    try:
        templates = await db.get_templates(current_user.id, category)
        # Auto-seed curated templates when user has none, then re-fetch
        if not templates:
            try:
                seeded = await db.seed_default_templates(current_user.id)
                if seeded:
                    templates = await db.get_templates(current_user.id, category)
            except Exception as seed_err:
                logger.warning(f"Template seeding skipped: {seed_err}")
        results: List[TemplateResponse] = []
        for item in templates:
            title = (item.get("title") or "").strip()
            try:
                template_id = _coerce_uuid(item.get("id"))
            except Exception as exc:
                logger.warning(f"Skipping template with invalid id: {item.get('id')} ({exc})")
                continue
            results.append(
                TemplateResponse(
                    id=template_id,
                    title=title,
                    name=title or item.get("name"),
                    content=item.get("content", ""),
                    category=item.get("category"),
                    type="document",
                    created_at=item.get("created_at") or datetime.utcnow(),
                    updated_at=item.get("updated_at"),
                )
            )
        return results
    except Exception as e:
        logger.error(f"Get templates error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve templates"
        )

@app.get("/api/documents/templates", response_model=List[TemplateResponse])
async def get_documents_templates_alias(
    category: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Alias for /api/templates to support newer frontend routes."""
    return await get_templates(category=category, current_user=current_user)

@app.post("/api/templates", response_model=TemplateResponse)
async def create_template(
    template_data: TemplateCreate,
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Create new template"""
    try:
        title = (template_data.title or template_data.name or "").strip()
        if not title:
            raise HTTPException(status_code=400, detail="Template title is required")
        category = (template_data.category or "").strip() or None
        created = await db.create_template(
            user_id=current_user.id,
            title=title,
            content=template_data.content,
            category=category,
        )
        try:
            template_id = _coerce_uuid(created.get("id"))
        except Exception as exc:
            logger.error(f"Create template returned invalid id: {created.get('id')} ({exc})")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create template"
            )
        return TemplateResponse(
            id=template_id,
            title=created.get("title", title),
            name=created.get("title", title),
            content=created.get("content", template_data.content),
            category=created.get("category"),
            type=(template_data.type or "document"),
            created_at=created.get("created_at") or datetime.utcnow(),
            updated_at=created.get("updated_at"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create template error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create template"
        )

@app.post("/api/templates/import", response_model=TemplateResponse)
async def import_template(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Import a document, have AI derive a template, and persist it."""
    if upload_processor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Importdienst ist derzeit nicht verf?gbar."
        )

    try:
        upload_meta = await upload_processor.handle_upload(file, str(current_user.id), db)
        content_text = upload_processor.get_file_content(upload_meta["file_id"])
        if not content_text or not content_text.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Die Datei enth?lt keinen verwertbaren Text.")

        original_name = upload_meta.get("original_filename") or upload_meta.get("filename") or file.filename or "Import"
        ai_payload, ai_response, meta = await ai_service.generate_template_from_document(
            document_text=content_text,
            filename=original_name,
            fail_hard=True,
        )

        title = (ai_payload.get("title") or os.path.splitext(original_name)[0] or "Importierte Vorlage").strip() or "Importierte Vorlage"
        category = (ai_payload.get("category") or "Importiert").strip() or "Importiert"
        content = (ai_payload.get("content") or "").strip()

        if not content:
            logger.error(f"Template import returned empty content. AI usage: {ai_response.usage}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Die KI konnte keinen verwertbaren Vorlageninhalt erzeugen."
            )

        created = await db.create_template(
            user_id=current_user.id,
            title=title,
            content=content,
            category=category,
        )
        template_id = _coerce_uuid(created.get("id"))
        return TemplateResponse(
            id=template_id,
            title=created.get("title", title),
            name=created.get("title", title),
            content=created.get("content", content),
            category=created.get("category"),
            type="document",
            created_at=created.get("created_at") or datetime.utcnow(),
            updated_at=created.get("updated_at"),
        )
    except HTTPException:
        raise
    except ValueError as exc:
        logger.error(f"Template import validation error: {exc}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as e:
        logger.error(f"Template import error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Import fehlgeschlagen."
        )

@app.get("/api/templates/insights", response_model=TemplateInsightsResponse)
async def get_template_insights_route(
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Expose aggregate metadata for the templates catalog."""
    try:
        raw = await db.get_template_insights(current_user.id)
        counts = raw.get("counts") or {}
        last_updated_at = _parse_client_datetime(raw.get("last_updated_at"))

        suggestions_payload: List[TemplateSuggestion] = []
        for item in raw.get("suggestions", []):
            try:
                suggestion_id = _coerce_uuid(item.get("id"))
            except Exception as exc:
                logger.debug(f"Skipping suggestion with invalid id: {item.get('id')} ({exc})")
                continue
            suggestions_payload.append(
                TemplateSuggestion(
                    id=suggestion_id,
                    name=item.get("name") or "Vorlage",
                    category=item.get("category"),
                    usage_count=int(item.get("usage_count") or 0),
                    updated_at=_parse_client_datetime(item.get("updated_at")),
                    match_score=int(item.get("match_score") or 35)
                )
            )

        categories_payload: List[TemplateCategoryStat] = [
            TemplateCategoryStat(
                label=item.get("label") or "Allgemein",
                count=int(item.get("count") or 0)
            )
            for item in raw.get("top_categories", [])
        ]

        recent_payload: List[Template] = []
        for item in raw.get("recent_templates", []):
            template_id = item.get("id")
            if not template_id:
                continue
            recent_payload.append(
                Template(
                    id=str(template_id),
                    title=item.get("title") or "Vorlage",
                    name=item.get("title") or "Vorlage",
                    content=item.get("content") or "",
                    category=item.get("category"),
                    type=item.get("type") or "document",
                    created_at=item.get("created_at") or datetime.utcnow(),
                    updated_at=item.get("updated_at")
                )
            )

        return TemplateInsightsResponse(
            counts=TemplateInsightsCounts(
                active=int(counts.get("active") or 0),
                updated_recent=int(counts.get("updated_recent") or 0),
                usage_events=int(counts.get("usage_events") or 0),
            ),
            last_updated_at=last_updated_at,
            suggestions=suggestions_payload,
            top_categories=categories_payload,
            recent_templates=recent_payload
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template insights error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute template insights"
        )

@app.put("/api/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: uuid.UUID,
    template_data: TemplateUpdate,
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Update existing template"""
    try:
        payload = template_data.dict(exclude_unset=True)
        if "name" in payload and "title" not in payload:
            payload["title"] = payload.pop("name")
        expected_updated_at = payload.pop("updated_at", None) or template_data.updated_at
        if isinstance(expected_updated_at, str):
            expected_updated_at = _parse_client_datetime(expected_updated_at)
        if expected_updated_at is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Template version is required for update."
            )
        updated = await db.update_template(
            template_id=template_id,
            user_id=current_user.id,
            title=payload.get("title"),
            content=payload.get("content"),
            category=payload.get("category"),
            expected_updated_at=expected_updated_at,
        )

        if not updated:
            existing = await db.get_template_by_id(template_id, current_user.id)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Template was modified by another session. Please refresh and try again."
                )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )

        title = (updated.get("title") or "").strip()
        return TemplateResponse(
            id=_coerce_uuid(updated.get("id")),
            title=title,
            name=title or payload.get("title"),
            content=updated.get("content", payload.get("content", "")),
            category=updated.get("category"),
            type=(payload.get("type") or "document"),
            created_at=updated.get("created_at") or datetime.utcnow(),
            updated_at=updated.get("updated_at"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update template error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update template"
        )

@app.delete("/api/templates/{template_id}")
async def delete_template(
    template_id: uuid.UUID,
    updated_at: Optional[str] = Query(None, description="Expected updated_at timestamp for concurrency control"),
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Delete template"""
    try:
        expected_updated_at = _parse_client_datetime(updated_at)
        success = await db.delete_template(template_id, current_user.id, expected_updated_at)
        if not success:
            existing = await db.get_template_by_id(template_id, current_user.id)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Template was modified by another session. Bitte aktualisieren Sie die Seite."
                )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )

        return {"message": "Template deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete template error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete template"
        )

# ============ CLAUSE ENDPOINTS ============

@app.get("/api/clauses", response_model=List[ClauseResponse])
async def get_clauses(
    category: Optional[str] = None,
    language: Optional[str] = "de",
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Get user clauses with optional filters"""
    try:
        clauses = await db.get_clauses(current_user.id, category, language)
        results: List[ClauseResponse] = []
        for clause in clauses:
            results.append(
                ClauseResponse(
                    id=clause.get("id"),
                    title=clause.get("title", ""),
                    content=clause.get("content", ""),
                    category=clause.get("category"),
                    language=clause.get("language"),
                    created_at=clause.get("created_at") or datetime.utcnow(),
                )
            )
        return results
    except Exception as e:
        logger.error(f"Get clauses error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve clauses"
        )

@app.get("/api/documents/clauses", response_model=List[ClauseResponse])
async def get_documents_clauses_alias(
    category: Optional[str] = None,
    language: Optional[str] = "de",
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Alias for /api/clauses for legacy/newer client routes."""
    return await get_clauses(category=category, language=language, current_user=current_user)

@app.post("/api/clauses", response_model=ClauseResponse)
async def create_clause(
    clause_data: ClauseCreate,
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Create new clause"""
    try:
        clause = await db.create_clause(
            user_id=current_user.id,
            category=clause_data.category,
            title=clause_data.title,
            content=clause_data.content,
            tags=clause_data.tags,
            language=clause_data.language
        )
        return ClauseResponse(
            id=clause.get("id"),
            title=clause.get("title", clause_data.title),
            content=clause.get("content", clause_data.content),
            category=clause.get("category", clause_data.category),
            language=clause.get("language", clause_data.language),
            created_at=clause.get("created_at") or datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Create clause error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create clause"
        )

# ============ CLIPBOARD ENDPOINTS ============

@app.get("/api/clipboard", response_model=List[ClipboardResponse])
async def get_clipboard_entries(
    limit: int = 50,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get user clipboard entries"""
    try:
        entries = await db.get_clipboard_entries(current_user.id, limit)
        return [
            ClipboardResponse(
                id=e.id,
                content=e.content,
                source_type=e.source_type,
                metadata=e.metadata,
                created_at=e.created_at
            ) for e in entries
        ]
    except Exception as e:
        logger.error(f"Get clipboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve clipboard entries"
        )

@app.post("/api/clipboard", response_model=ClipboardResponse)
async def add_clipboard_entry(
    entry_data: ClipboardCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Add entry to clipboard"""
    try:
        entry = await db.create_clipboard_entry(
            user_id=current_user.id,
            content=entry_data.content,
        )
    except Exception as e:
        logger.error(f"Add clipboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add clipboard entry"
        )
        model = request_data.model or ""
        temp = request_data.temperature if request_data.temperature is not None else ""
        key_raw = f"u:{current_user.id}|m:{model}|t:{temp}|p:{_sha256(ptxt)}|c:{_sha256(ctxt)}"
        cache_key = f"ai:complete:v1:{_sha256(key_raw)}"

        # Try cache first
        try:
            cached = await cache_service.redis_client.get(cache_key)
            if cached:
                data = json.loads(cached)
                # Return as dict; response_model will validate/serialize
                return data
        except Exception as ce:
            logger.warning(f"AI cache get failed: {ce}")

        # No cache hit: generate
        response = await ai_service.generate_completion(
            prompt=ptxt,
            model=model,
            max_tokens=request_data.max_tokens,
            temperature=request_data.temperature,
            context=ctxt,
        )

        # Track usage (best-effort)
        try:
            await db.create_analytics_event(
                user_id=current_user.id,
                event_type="ai_completion",
                data={
                    "model": model,
                    "tokens_used": getattr(response, "tokens_used", None),
                    "cost_estimate": getattr(response, "cost_estimate", None),
                },
            )
        except Exception as te:
            logger.warning(f"Analytics event failed: {te}")

        # Store in cache (TTL 1 day) when response is healthy
        response_usage = getattr(response, "usage", {}) or {}
        if not response_usage.get("error"):
            try:
                payload = {
                    "content": getattr(response, "content", None),
                    "tokens_used": getattr(response, "tokens_used", None),
                    "model_used": getattr(response, "model_used", None),
                    "generation_time_ms": getattr(response, "generation_time_ms", None),
                    "cost_estimate": getattr(response, "cost_estimate", None),
                    "prompt_used": getattr(response, "prompt_used", None),
                }
                await cache_service.redis_client.setex(cache_key, 86400, json.dumps(payload))
            except Exception as se:
                logger.warning(f"AI cache set failed: {se}")

        return response
    except Exception as e:
        logger.error(f"AI completion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI completion failed"
        )

@app.post("/api/assistant/feedback")
async def submit_feedback(req: FeedbackRequest, request: Request, current_user: UserInDB = Depends(get_current_user)):
    if not FEEDBACK_V1_ENABLED:
        raise HTTPException(status_code=404, detail="Not enabled")
    # Rate limit: 60/hour
    ok = await _rate_limit(str(current_user.id), "fb", 60)
    if not ok:
        raise HTTPException(status_code=429, detail="rate limit")
    if req.rating not in (-1, 1):
        raise HTTPException(status_code=400, detail="invalid rating")
    if req.rating == -1 and not (req.reasons and isinstance(req.reasons, list) and len(req.reasons)>0):
        raise HTTPException(status_code=400, detail="reasons required for negative rating")
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    try:
        # ensure message row
        await _ensure_message_exists(req.message_id, str(current_user.id), conversation_id=req.conversation_id, model=req.model)
        async with db.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO message_feedback (message_id, user_id, rating, reasons, note, model, message_hash, ip_hash, user_agent)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (user_id, message_id) DO UPDATE SET
                    rating = EXCLUDED.rating,
                    reasons = EXCLUDED.reasons,
                    note = EXCLUDED.note,
                    model = EXCLUDED.model,
                    message_hash = EXCLUDED.message_hash,
                    ip_hash = EXCLUDED.ip_hash,
                    user_agent = EXCLUDED.user_agent,
                    updated_at = NOW()
                """,
                uuid.UUID(req.message_id), current_user.id, req.rating, req.reasons, req.note,
                req.model, req.message_hash, _hash_ip(ip), ua
            )
        return {"ok": True, "feedback_id": str(uuid.uuid4())}
    except Exception as e:
        logger.error(f"feedback error: {e}")
        raise HTTPException(status_code=500, detail="feedback failed")

@app.post("/api/assistant/edit")
async def submit_edit(req: EditRequest, request: Request, current_user: UserInDB = Depends(get_current_user)):
    if not FEEDBACK_V1_ENABLED:
        raise HTTPException(status_code=404, detail="Not enabled")
    # Rate limit: 30/hour
    ok = await _rate_limit(str(current_user.id), "edit", 30)
    if not ok:
        raise HTTPException(status_code=429, detail="rate limit")
    if not req.edited_content or len(req.edited_content.strip()) < 20:
        raise HTTPException(status_code=400, detail="edited_content too short")
    try:
        await _ensure_message_exists(req.message_id, str(current_user.id), conversation_id=req.conversation_id)
        async with db.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO message_edits (message_id, user_id, edited_content, allow_training, message_hash, diff)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                uuid.UUID(req.message_id), current_user.id, req.edited_content, req.allow_training, req.message_hash, None
            )
        return {"ok": True, "edit_id": str(uuid.uuid4())}
    except Exception as e:
            logger.error(f"edit error: {e}")
            raise HTTPException(status_code=500, detail="edit failed")

class AbuseRequest(BaseModel):
    message_id: str
    category: str
    note: _Optional[str] = None

@app.post("/api/assistant/abuse")
async def report_abuse(req: AbuseRequest, request: Request, current_user: UserInDB = Depends(get_current_user)):
    if not FEEDBACK_V1_ENABLED:
        raise HTTPException(status_code=404, detail="Not enabled")
    ok = await _rate_limit(str(current_user.id), "abuse", 10)
    if not ok:
        raise HTTPException(status_code=429, detail="rate limit")
    try:
        await db.create_analytics_event(
            user_id=current_user.id,
            event_type="assistant_abuse",
            event_data={"message_id": req.message_id, "category": req.category, "note": req.note},
            ip_address=(request.client.host if request.client else None),
            user_agent=request.headers.get("user-agent")
        )
        return {"ok": True}
    except Exception as e:
        logger.error(f"abuse report error: {e}")
        raise HTTPException(status_code=500, detail="abuse report failed")

class ChatRequest(BaseModel):
    message: str
    conversation_id: _Optional[str] = None
    model: _Optional[str] = None
    max_tokens: _Optional[int] = 1000
    temperature: _Optional[float] = 0.7

@app.post("/api/assistant/chat")
async def assistant_chat(
    req: ChatRequest,
    request: Request,
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Conversational AI chat endpoint with context awareness"""
    try:
        # Validate message length
        if not req.message or not req.message.strip():
            raise HTTPException(status_code=400, detail="Nachricht darf nicht leer sein")
        if len(req.message) > 4000:
            raise HTTPException(
                status_code=400,
                detail="Ihre Nachricht ist zu lang. Maximal 4000 Zeichen erlaubt."
            )
        
        # Rate limiting: 10 messages per minute
        ok = await _rate_limit(str(current_user.id), "assistant_chat", 10)
        if not ok:
            raise HTTPException(
                status_code=429,
                detail="Sie haben das Nachrichtenlimit ?berschritten. Bitte warten Sie einen Moment."
            )
        
        # Retrieve conversation history if conversation_id provided
        conversation_uuid = None
        context_text = ""
        if req.conversation_id:
            try:
                conversation_uuid = uuid.UUID(req.conversation_id)
                history = await db.get_conversation_history(
                    conversation_id=conversation_uuid,
                    user_id=current_user.id,
                    limit=5  # Last 5 messages for context
                )
                
                if not history:
                    raise HTTPException(
                        status_code=404,
                        detail="Diese Konversation wurde nicht gefunden."
                    )
                
                # Build context from conversation history
                context_parts = []
                for msg in history[-5:]:  # Take last 5 messages
                    role = "User" if msg['role'] == 'user' else "Assistant"
                    context_parts.append(f"{role}: {msg['content']}")
                context_text = "\n\n".join(context_parts)
                
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Ung?ltige Konversations-ID."
                )
        
        # Save user message to database (before AI generation)
        user_msg_result = await db.create_conversation_message(
            user_id=current_user.id,
            role="user",
            content=req.message,
            conversation_id=conversation_uuid,
            model=None
        )
        
        # Use the returned conversation_id (new or existing)
        conversation_id_str = user_msg_result['conversation_id']
        conversation_uuid = uuid.UUID(conversation_id_str)
        
        # Generate AI response with context
        start_time = datetime.utcnow()
        try:
            ai_response = await ai_service.generate_completion(
                prompt=req.message,
                model=req.model,
                max_tokens=req.max_tokens,
                temperature=req.temperature,
                context=context_text
            )
            generation_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            # Log empty/short responses for monitoring
            try:
                content_preview = (ai_response.content or "").strip()
                if not content_preview or len(content_preview) < 20:
                    logger.warning(
                        "assistant_chat: sidecar returned empty/short text",
                        extra={
                            "conversation_id": conversation_id_str,
                            "user_id": str(current_user.id),
                            "model": ai_response.model_used or req.model or "qwen_legal_q4_k_m",
                            "latency_ms": generation_time_ms,
                        }
                    )
            except Exception:
                pass
            
            # Save assistant response to database
            assistant_msg_result = await db.create_conversation_message(
                user_id=current_user.id,
                role="assistant",
                content=ai_response.content,
                conversation_id=conversation_uuid,
                model=ai_response.model_used or req.model or "qwen_legal_q4_k_m"
            )
            
            # Return response with metadata
            return {
                "content": ai_response.content,
                "conversation_id": conversation_id_str,
                "message_id": assistant_msg_result['message_id'],
                "model": ai_response.model_used or req.model or "qwen_legal_q4_k_m",
                "usage": ai_response.usage if hasattr(ai_response, 'usage') else {},
                "generation_time_ms": generation_time_ms
            }
            
        except Exception as ai_error:
            logger.error(f"AI service error in chat: {ai_error}")
            raise HTTPException(
                status_code=503,
                detail="Ich konnte die Antwort gerade nicht fertigstellen. Bitte stellen Sie Ihre Frage gleich noch einmal ? ich helfe sofort weiter."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Assistant chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut."
        )

@app.get("/api/rag/test")
async def rag_test(query: str = "? 823 BGB"):
    """Test RAG retrieval endpoint"""
    try:
        from rag_service import rag_service
        
        start_time = time.time()
        results = rag_service.retrieve(query)
        retrieval_time = int((time.time() - start_time) * 1000)
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "retrieval_time_ms": retrieval_time
        }
    except Exception as e:
        logger.error(f"RAG test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/complete-test")
async def ai_complete_test(request_data: dict):
    """Temporary unauthenticated endpoint for on-box quality testing.
    Caps max_tokens to 512 to avoid overload.
    """
    try:
        prompt = (request_data.get("prompt") or "").strip()
        if not prompt:
            raise HTTPException(status_code=400, detail="Missing prompt")
        model = request_data.get("model")
        max_tokens = min(int(request_data.get("max_tokens") or 256), 512)
        temperature = request_data.get("temperature")
        context = request_data.get("context") or "general"

        response = await ai_service.generate_completion(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            context=context,
        )
        return {
            "content": response.content,
            "tokens_used": response.tokens_used,
            "model_used": response.model_used,
            "generation_time_ms": response.generation_time_ms,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"complete-test error: {e}")
        raise HTTPException(status_code=500, detail="AI test failed")

@app.post("/api/ai/generate-document", response_model=DocumentResponse)
async def generate_document(
    request_data: DocumentGenerateRequest,
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Generate legal document using AI"""
    # Rate limit to 10 document generations per hour per user
    if not await _rate_limit(str(current_user.id), "ai_generate_document", 10, 3600):
        logger.warning(f"Rate limit exceeded for document generation by user {current_user.id}")
        raise HTTPException(
            status_code=429,
            detail="Sie haben das Limit f?r Dokumentenerstellung ?berschritten. Bitte versuchen Sie es sp?ter erneut."
        )

    try:
        upload_excerpt = ""
        if request_data.upload_id and upload_processor:
            try:
                upload_excerpt = upload_processor.get_file_content(request_data.upload_id) or ""
            except Exception as _ue:
                logger.warning(f"upload text retrieval failed for {request_data.upload_id}: {_ue}")

        try:
            ai_response = await ai_service.generate_document(
                document_type=request_data.document_type,
                title=request_data.title,
                instructions=request_data.instructions,
                tone=request_data.tone,
                template_content=request_data.template_content or "",
                variables=request_data.variables,
                upload_excerpt=upload_excerpt,
                model=request_data.model,
                fail_hard=True,
            )
        except httpx.HTTPStatusError as exc:
            detail = _http_error_detail(exc)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
        except Exception as exc:
            logger.error(f"AI provider failure: {exc}")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI provider unavailable")

        try:
            rendered_html = ai_service.format_document_json(ai_response.content)
        except Exception:
            rendered_html = None
        safe_content = rendered_html if rendered_html else ai_service._normalize_document_output(ai_response.content)

        if not safe_content or not safe_content.strip():
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI response did not contain usable content")

        document = await db.create_document(
            user_id=current_user.id,
            title=request_data.title or f"{request_data.document_type.title()} ({datetime.utcnow().strftime('%d.%m.%Y')})",
            content=safe_content,
            document_type=request_data.document_type,
        )
        
        metadata = {
            "model_used": ai_response.model_used or request_data.model,
            "generation_time_ms": ai_response.generation_time_ms,
            "redactions": (ai_response.usage or {}).get("redactions"),
            "sanitized": (ai_response.usage or {}).get("sanitized"),
        }

        template_uuid = _try_uuid(request_data.template_id)
        if template_uuid:
            await db.record_template_usage(current_user.id, template_uuid)

        resp = DocumentResponse(
            id=str(document.get("id")),
            title=document.get("title", request_data.title or request_data.document_type),
            content=document.get("content", safe_content),
            document_type=document.get("document_type") or document.get("type") or request_data.document_type,
            created_at=document.get("created_at") or datetime.utcnow(),
            metadata=metadata,
            processing_state="generated",
        )
        return resp
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document generation failed"
        )

# ============ FILE UPLOAD ENDPOINTS ============

@app.get("/api/files")
async def list_files(current_user: UserInDB = Depends(get_current_user_flexible)):
    if not upload_processor:
        raise HTTPException(status_code=500, detail="Upload subsystem not available")
    try:
        items = upload_processor.list_user_files(str(current_user.id))
        return {"files": items}
    except Exception as e:
        logger.error(f"List files error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list files")


@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...), current_user: UserInDB = Depends(get_current_user_flexible)):
    if not upload_processor:
        raise HTTPException(status_code=500, detail="Upload subsystem not available")
    try:
        result = await upload_processor.handle_upload(file, str(current_user.id), db=db)
        normalized = {**result, "id": result.get("file_id"), "fileId": result.get("file_id"), "name": result.get("filename")}
        return {"success": True, **normalized}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/files/{file_id}/content")
async def get_file_content_endpoint(file_id: str, current_user: UserInDB = Depends(get_current_user_flexible)):
    if not upload_processor:
        raise HTTPException(status_code=500, detail="Upload subsystem not available")
    content = upload_processor.get_file_content(file_id)
    if content is None:
        raise HTTPException(status_code=404, detail="File not found")
    return {"success": True, "file_id": file_id, "content": content}


@app.get("/api/files/{file_id}/metadata")
async def get_file_metadata_endpoint(file_id: str, current_user: UserInDB = Depends(get_current_user_flexible)):
    if not upload_processor:
        raise HTTPException(status_code=500, detail="Upload subsystem not available")
    meta = upload_processor.get_file_metadata(file_id)
    if not meta or str(meta.get("user_id")) != str(current_user.id):
        raise HTTPException(status_code=404, detail="File not found")
    return meta


@app.delete("/api/files/{file_id}")
async def delete_file_endpoint(file_id: str, current_user: UserInDB = Depends(get_current_user_flexible)):
    if not upload_processor:
        raise HTTPException(status_code=500, detail="Upload subsystem not available")
    ok = upload_processor.delete_file(file_id)
    if not ok:
        raise HTTPException(status_code=404, detail="File not found")
    return {"success": True}


@app.post("/api/files/{file_id}/process")
async def process_file_endpoint(file_id: str, current_user: UserInDB = Depends(get_current_user_flexible)):
    if not upload_processor:
        raise HTTPException(status_code=500, detail="Upload subsystem not available")
    try:
        result = await upload_processor.process_existing(file_id, db=db)
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"Process file error: {e}")
        raise HTTPException(status_code=500, detail="Processing failed")


# ============ DOCUMENT PROCESSING HELPERS ============

def _coerce_document_generation_payload(raw: Dict[str, Any]) -> Dict[str, Any]:
    payload: Dict[str, Any] = dict(raw or {})
    upload_id = payload.get("uploadId") or payload.get("upload_id") or payload.get("uploadedFileId")
    if upload_id:
        payload["uploadId"] = upload_id
        payload["upload_id"] = upload_id
    template_content = (
        payload.get("template_content")
        or payload.get("templateContent")
        or payload.get("template")
    )
    if template_content is not None:
        payload["template_content"] = template_content
    document_type = (payload.get("document_type") or payload.get("docType") or "custom").strip() or "custom"
    payload["document_type"] = document_type
    title = payload.get("title") or document_type or "Rechtsdokument"
    payload["title"] = title
    instructions = (
        payload.get("instructions")
        or payload.get("prompt")
        or payload.get("requirements")
        or ""
    )
    payload["instructions"] = instructions
    tone = (payload.get("tone") or "neutral").strip() or "neutral"
    payload["tone"] = tone
    if "variables" not in payload or payload["variables"] is None:
        payload["variables"] = {}
    return payload


def _normalize_document_process_result(raw: Any, default_state: str = "generated") -> Dict[str, Any]:
    if isinstance(raw, BaseModel):
        data = raw.model_dump()
    elif isinstance(raw, dict):
        data = dict(raw)
    else:
        data = {}

    document = data.get("document")
    if isinstance(document, BaseModel):
        document = document.model_dump()
    if not isinstance(document, dict):
        document = {}

    doc_source = document if document else data
    if isinstance(doc_source, BaseModel):
        doc_source = doc_source.model_dump()
    if not isinstance(doc_source, dict):
        doc_source = {}

    raw_doc_id = doc_source.get("id") or data.get("id") or data.get("documentId")
    doc_id = str(raw_doc_id) if raw_doc_id else None

    download = data.get("download") or doc_source.get("download")
    if not download and doc_id:
        download = {
            "docx": f"/api/documents/{doc_id}/export?format=docx",
            "pdf": f"/api/documents/{doc_id}/export?format=pdf",
        }

    metadata = doc_source.get("metadata") or data.get("metadata") or {}
    processing_state = (
        doc_source.get("processing_state")
        or data.get("processing_state")
        or default_state
    )
    status_value = (
        doc_source.get("status")
        or data.get("status")
        or ("submitted" if processing_state == "submitted" else "generated")
    )
    title = (
        doc_source.get("title")
        or data.get("title")
        or doc_source.get("document_type")
        or "Rechtsdokument"
    )
    content = doc_source.get("content") or data.get("content") or ""
    doc_type = (
        doc_source.get("document_type")
        or doc_source.get("type")
        or data.get("document_type")
        or "custom"
    )
    created_at = doc_source.get("created_at") or data.get("created_at")
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()
    if created_at is None:
        created_at = datetime.utcnow().isoformat()

    normalized_document = {
        "id": doc_id,
        "title": title,
        "content": content,
        "document_type": doc_type,
        "created_at": created_at,
        "metadata": metadata,
        "status": status_value,
        "processing_state": processing_state,
        "download": download,
    }

    return {
        "success": bool(data.get("success", True)),
        "document": normalized_document,
        "metadata": metadata,
        "processing_state": processing_state,
        "status": status_value,
        "documentId": doc_id,
        "id": doc_id,
        "download": download,
    }


@app.post("/api/documents/process")
async def process_document_action(
    request: Request,
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    logger.info(f"?? Document process request from user {current_user.id}")
    try:
        body = await request.json()
        logger.info(f"?? Request body keys: {list(body.keys())}")
    except Exception as e:
        logger.error(f"?? Failed to parse JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    action = str((body.get("action") or "generate")).strip().lower()
    raw_payload = body.get("payload") or body or {}
    logger.info(f"?? Action: {action}, Payload keys: {list(raw_payload.keys())}")

    if action not in {"generate", "submit"}:
        raise HTTPException(status_code=400, detail=f"Unsupported action '{action}'")

    if action == "generate":
        payload = _coerce_document_generation_payload(raw_payload)
        logger.info(f"?? Generating document for user {current_user.id}, type: {payload.get('document_type')}")
        template_uuid = _try_uuid(payload.get("template_id") or payload.get("templateId"))
        try:
            simple_result = await generate_document_working(payload, current_user)  # type: ignore[arg-type]
            logger.info(f"? Document generated successfully (simple path)")
            if template_uuid:
                await db.record_template_usage(current_user.id, template_uuid)
            return _normalize_document_process_result(simple_result, "generated")
        except HTTPException as exc:
            if exc.status_code != status.HTTP_403_FORBIDDEN:
                logger.error(f"? Document generation failed (simple path): {exc.detail}")
                raise
            logger.info("?? Simple path returned 403, trying full path")

        try:
            full_request = DocumentGenerateRequest(
                document_type=payload.get("document_type") or "custom",
                title=payload.get("title"),
                instructions=payload.get("instructions"),
                tone=payload.get("tone"),
                variables=payload.get("variables"),
                model=payload.get("model"),
                template_id=payload.get("template_id") or payload.get("templateId"),
                template_content=payload.get("template_content"),
                upload_id=payload.get("uploadId") or payload.get("upload_id"),
            )
        except Exception as validation_error:
            logger.error(f"? Invalid payload for document generation: {validation_error}")
            raise HTTPException(status_code=400, detail=f"Invalid payload: {validation_error}")

        logger.info(f"?? Calling full document generation for: {full_request.document_type}")
        full_result = await generate_document(full_request, current_user)
        logger.info(f"? Document generated successfully (full path)")
        template_uuid = template_uuid or _try_uuid(full_request.template_id)
        if template_uuid:
            await db.record_template_usage(current_user.id, template_uuid)
        return _normalize_document_process_result(full_result, full_result.processing_state or "generated")

    submission_payload = dict(raw_payload or {})
    submission_result = await save_document_endpoint(submission_payload, current_user)
    doc_id = submission_result.get("id") or submission_result.get("documentId")
    desired_status = submission_payload.get("status")
    if doc_id and desired_status:
        try:
            await update_document_status_endpoint(str(doc_id), {"status": desired_status}, current_user)
        except Exception as status_error:
            logger.warning(f"Document status update failed: {status_error}")
    return _normalize_document_process_result(submission_result, submission_result.get("processing_state") or "submitted")


# ============ DOCUMENT SAVE/EXPORT/STATUS ENDPOINTS ============

@app.post("/api/documents/save")
async def save_document_endpoint(payload: dict, current_user: UserInDB = Depends(get_current_user_flexible)):
    try:
        title = (payload.get("title") or "Unbenanntes Dokument").strip()
        content = payload.get("content") or payload.get("html") or ""
        doc_type = payload.get("document_type") or "custom"
        template_id = payload.get("template_id")
        metadata = payload.get("metadata")
        requested_status = (payload.get("status") or "").strip().lower()
        processing_state = payload.get("processing_state")

        document = await db.create_document(
            user_id=current_user.id,
            title=title,
            content=content,
            document_type=doc_type,
        )
        template_uuid = _try_uuid(template_id)
        if template_uuid:
            await db.record_template_usage(current_user.id, template_uuid)
        raw_id = document.get("id")
        doc_id = str(raw_id) if raw_id else None
        status_value = requested_status or document.get("status") or "saved"
        normalized_processing_state = processing_state or ("submitted" if status_value in {"submitted", "sent", "final"} else "saved")
        download_links = {}
        if doc_id:
            download_links = {
                "docx": f"/api/documents/{doc_id}/export?format=docx",
                "pdf": f"/api/documents/{doc_id}/export?format=pdf",
            }
        # Normalize mapping from DB result (dict)
        return {
            "success": True,
            "id": doc_id,
            "documentId": doc_id,
            "status": status_value,
            "processing_state": normalized_processing_state,
            "download": download_links,
            "document": {
                "id": doc_id,
                "title": document.get("title", title),
                "content": document.get("content", content),
                "document_type": document.get("document_type") or document.get("type") or doc_type,
                "created_at": document.get("created_at") or datetime.utcnow().isoformat(),
                "metadata": metadata or {},
                "status": status_value,
                "processing_state": normalized_processing_state,
                "download": download_links,
            },
        }
    except Exception as e:
        logger.error(f"Save document error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save document")


@app.get("/api/documents/{doc_id}/export")
async def export_document_endpoint(doc_id: str, format: str = "docx", current_user: UserInDB = Depends(get_current_user_flexible)):
    try:
        import export_utils  # type: ignore
    except Exception:
        raise HTTPException(status_code=500, detail="Export utilities not available")
    try:
        async with db.get_connection() as conn:
            row = await conn.fetchrow("SELECT id, title, content FROM documents WHERE id = $1 AND user_id = $2", uuid.UUID(doc_id), current_user.id)
        if not row:
            raise HTTPException(status_code=404, detail="Document not found")
        data, filename, media_type = export_utils.export_document(format=format, title=row["title"], content=row["content"])
        return StreamingResponse(iter([data]), media_type=media_type, headers={"Content-Disposition": f"attachment; filename=\"{filename}\""})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export document error: {e}")
        raise HTTPException(status_code=500, detail="Export failed")


@app.post("/api/documents/{doc_id}/status")
async def update_document_status_endpoint(doc_id: str, payload: dict, current_user: UserInDB = Depends(get_current_user_flexible)):
    try:
        new_status = (payload.get("status") or "").strip().lower()
        async with db.get_connection() as conn:
            try:
                await conn.execute(
                    "UPDATE documents SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2 AND user_id = $3",
                    new_status, uuid.UUID(doc_id), current_user.id
                )
            except Exception as e:
                # Auto-heal: add missing status column and retry once
                if "column \"status\" of relation \"documents\" does not exist" in str(e).lower():
                    try:
                        await conn.execute("ALTER TABLE documents ADD COLUMN IF NOT EXISTS status TEXT")
                        await conn.execute(
                            "UPDATE documents SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2 AND user_id = $3",
                            new_status, uuid.UUID(doc_id), current_user.id
                        )
                    except Exception as e2:
                        logger.error(f"Auto-heal status column failed: {e2}")
                        raise
                else:
                    raise
        return {"success": True, "status": new_status}
    except Exception as e:
        logger.error(f"Update document status error: {e}")
        raise HTTPException(status_code=500, detail="Status update failed")


@app.post("/api/documents/status")
async def update_document_status_noid_endpoint(payload: dict, current_user: UserInDB = Depends(get_current_user_flexible)):
    doc_id = payload.get("doc_id") or payload.get("document_id") or payload.get("id")
    if not doc_id:
        raise HTTPException(status_code=400, detail="Missing doc_id")
    return await update_document_status_endpoint(str(doc_id), payload, current_user)


@app.get("/internal/dashboard-summary/{user_id}")
async def internal_dashboard_summary(user_id: str, request: Request):
    """Return aggregated dashboard metrics for the specified user."""
    key_required = DASHBOARD_SERVICE_KEY
    provided_key = (request.headers.get("x-service-key") or "").strip()

    if key_required:
        if not provided_key or not secrets.compare_digest(provided_key, key_required):
            logger.warning("Dashboard summary access denied: invalid service key")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")

    if not db:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")

    try:
        summary = await db.get_dashboard_summary(user_uuid)
        return summary
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to compute dashboard summary", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Dashboard summary unavailable") from exc

# ============ WORKING LOGIN ENDPOINT ============

@app.post("/auth/login-working")
async def login_working(request: dict):
    """Working login endpoint for frontend"""
    try:
        email = request.get("email", "").strip().lower()
        password = request.get("password", "")
        
        logger.info(f"Login attempt for: {email}")
        
        if not email or not password:
            return {"error": "Email and password required", "success": False}
        
        # Get user
        user = await db.get_user_by_email(email)
        if not user:
            logger.warning(f"User not found: {email}")
            return {"error": "Invalid credentials", "success": False}
        
        # Verify password  
        if not auth_service.verify_password(password, user.password_hash):
            logger.warning(f"Invalid password for: {email}")
            return {"error": "Invalid credentials", "success": False}
        
        # Check active status
        if hasattr(user, "is_active") and not user.is_active:
            logger.warning(f"Inactive user: {email}")
            return {"error": "Account disabled", "success": False}
        
        # Create token
        token = auth_service.create_access_token(data={"sub": str(user.id)})
        
        # Store session
        session_id = str(uuid.uuid4())
        if cache_service:
            await cache_service.store_session(session_id, str(user.id), expires_in=86400)
        
        logger.info(f"Login successful for: {email}")
        
        payload = {
            "success": True,
            "token": token,
            "token_type": "bearer", 
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
        }
        response = JSONResponse(content=payload)
        _set_auth_cookies(response, token)
        return response
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"error": f"Server error: {str(e)}", "success": False}

# ============ PASSWORD RESET (OTP) ============

@app.post("/auth/forgot-password")
async def forgot_password(payload: dict):
    """Initiate password reset by generating an OTP and sending via email.
    Non-destructive; stores OTP in Redis with short TTL.
    """
    try:
        email = (payload.get("email") or "").strip().lower()
        if not email or "@" not in email:
            raise HTTPException(status_code=400, detail="G?ltige E-Mail-Adresse erforderlich")

        user = await db.get_user_by_email(email)
        if not user:
            # Do not reveal existence; return success
            return {"success": True}

        # Generate 6-digit OTP
        otp = f"{secrets.randbelow(1000000):06d}"
        key = f"pwd:otp:{email}"
        try:
            # Use cache service helper for consistency
            await cache_service.set(key, otp, ttl=600)  # 10 minutes
        except Exception as e:
            logger.error(f"OTP store failed: {e}")
            raise HTTPException(status_code=500, detail="Reset failed")

        # Send email via SMTP or log
        sent = send_email(
            subject="Ihr Anwalts.AI Einmal-Code",
            to_email=email,
            body_text=f"Ihr Einmal-Code lautet: {otp}. Er ist 10 Minuten g?ltig."
        )
        if not sent:
            logger.warning("SMTP send returned False; check SMTP_* env or MailHog availability")
        resp = {"success": True}
        if os.getenv("DEBUG_PASSWORD_RESET", "0") == "1":
            resp["otp"] = otp
            resp["sent"] = sent
        return resp
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"forgot-password error: {e}")
        raise HTTPException(status_code=500, detail="Reset failed")


@app.post("/auth/reset-password")
async def reset_password(payload: dict):
    """Verify OTP and set a new password."""
    try:
        email = (payload.get("email") or "").strip().lower()
        otp = (payload.get("otp") or "").strip()
        new_password = payload.get("new_password") or ""
        if not email or not otp or not new_password:
            raise HTTPException(status_code=400, detail="Missing fields")
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Passwort ist zu kurz")

        user = await db.get_user_by_email(email)
        if not user:
            # Don't reveal; pretend success
            return {"success": True}

        key = f"pwd:otp:{email}"
        try:
            stored = await cache_service.get(key)
        except Exception as e:
            logger.error(f"OTP get failed: {e}")
            raise HTTPException(status_code=500, detail="Reset failed")
        if not stored or stored != otp:
            raise HTTPException(status_code=400, detail="Ung?ltiger Code")

        # Update password
        new_hash = auth_service.hash_password(new_password)
        ok = await db.update_user_password(user.id, new_hash)
        if not ok:
            raise HTTPException(status_code=500, detail="Reset failed")

        try:
            await cache_service.delete(key)
        except Exception:
            pass

        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"reset-password error: {e}")
        raise HTTPException(status_code=500, detail="Reset failed")


@app.post("/auth/change-password")
async def change_password(payload: dict, current_user: UserInDB = Depends(get_current_user)):
    """Change password for authenticated user."""
    try:
        current_password = payload.get("current_password") or ""
        new_password = payload.get("new_password") or ""
        if not current_password or not new_password:
            raise HTTPException(status_code=400, detail="Missing fields")
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Passwort ist zu kurz")

        # Fetch fresh user and verify current password
        user = await db.get_user_by_id(str(current_user.id))
        if not user or not auth_service.verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Aktuelles Passwort ist falsch")

        new_hash = auth_service.hash_password(new_password)
        ok = await db.update_user_password(user.id, new_hash)
        if not ok:
            raise HTTPException(status_code=500, detail="?nderung fehlgeschlagen")

        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"change-password error: {e}")
        raise HTTPException(status_code=500, detail="?nderung fehlgeschlagen")

# ============ HEALTH CHECK ============

@app.post("/test-simple")
async def test_simple(data: dict):
    """Simple test endpoint"""
    logger.info(f"Test endpoint called with data: {data}")
    return {"status": "success", "received": data}

@app.post("/auth/quick-login")
async def quick_login():
    """Quick test login endpoint"""
    return {
        "success": True,
        "token": "test-token-12345",
        "token_type": "bearer",
        "user": {
            "id": "test-id",
            "email": "admin@anwalts-ai.com", 
            "name": "Administrator",
            "role": "admin"
        }
    }


@app.post("/api/ai/generate-document-simple")
async def generate_document_working(
    request: dict,
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Lightweight document generation endpoint using Together-backed prompt."""
    # Rate limit to 20 simple document generations per hour per user
    if not await _rate_limit(str(current_user.id), "ai_generate_document_simple", 20, 3600):
        logger.warning(f"Rate limit exceeded for simple document generation by user {current_user.id}")
        raise HTTPException(
            status_code=429,
            detail="Sie haben das Limit f?r Dokumentenerstellung ?berschritten. Bitte versuchen Sie es sp?ter erneut."
        )

    try:
        title = request.get("title", "Neues Dokument")
        doc_type = request.get("document_type", "contract")
        # Frontend sends 'instructions'; keep backward-compat with 'prompt'/'requirements'
        user_instructions = (
            request.get("instructions")
            or request.get("prompt")
            or request.get("requirements")
            or ""
        )
        template_content = ""
        upload_id = request.get("uploadId") or request.get("upload_id") or None
        variables = request.get("variables") or {}
        tone = (request.get("tone") or "neutral").strip().lower()
        preferred_model = (request.get("model") or None)
        # Try to pull OCR/text extracted from uploaded file
        extracted_text = ""
        try:
            if upload_id and upload_processor:
                extracted_text = upload_processor.get_file_content(upload_id) or ""
        except Exception as _e:
            logger.warning(f"Upload text retrieval failed for {upload_id}: {_e}")
        
        logger.info(f"?? Generating document with AI: {title} ({doc_type})")

        ai_prompt, prompt_meta = ai_service.compose_document_prompt(
            document_type=doc_type,
            title=title,
            instructions=user_instructions,
            tone=tone,
            template_content=template_content,
            variables=variables,
            upload_excerpt=extracted_text,
        )

        start_time = time.time()

        # Cache check
        try:
            cache_model = preferred_model
            if not cache_model:
                cache_model = ai_service.together_model if ai_service.provider == "together" else (os.getenv("LOCAL_AI_MODEL") or ai_service.local_default_model)
            prompt_hash = cache_service.hash_prompt(
                ai_prompt,
                cache_model,
                max_tokens=1800,
                temperature=0.2,
                mode="docgen_simple_v1",
                tone=tone,
            )
            cached = await cache_service.get_cached_ai_response(prompt_hash)
        except Exception as _ce:
            logger.warning(f"simple docgen cache get failed: {_ce}")
            cached = None

        if cached and isinstance(cached, dict) and cached.get("content"):
            generation_time = int((time.time() - start_time) * 1000)
            # Sanitize or render cached content
            try:
                rendered_html = ai_service.format_document_json(cached.get("content", ""))
            except Exception:
                rendered_html = None
            safe_cached = rendered_html if rendered_html else ai_service._sanitize_output_text(cached.get("content", ""))
            metadata = {
                "model_used": cached.get("model_used") or cache_model,
                "generation_time_ms": generation_time,
                "redactions": dict(prompt_meta.get("redactions", {})),
                "sanitized": {
                    "instructions": prompt_meta.get("sanitized_instructions"),
                    "upload_excerpt": prompt_meta.get("sanitized_upload"),
                    "template": prompt_meta.get("sanitized_template"),
                    "variables": prompt_meta.get("sanitized_variables"),
                },
            }
            return {
                "success": True,
                "document": {
                    "id": f"doc_{uuid.uuid4().hex[:8]}",
                    "title": title,
                    "content": safe_cached,
                    "document_type": doc_type,
                    "created_at": datetime.utcnow().isoformat(),
                    "tokens_used": int(cached.get("tokens_used") or 0),
                    "model_used": cached.get("model_used") or cache_model,
                    "generation_time_ms": generation_time,
                    "processing_time": generation_time / 1000,
                    "confidence": 0.95,
                    "cost_estimate": float(cached.get("cost_estimate") or 0.0),
                    "metadata": metadata,
                    "processing_state": "generated",
                },
            }
        
        # Call AI service (prefer model from request, fallback to LOCAL_AI_MODEL)
        from os import getenv as _getenv
        if not preferred_model:
            if ai_service.provider == "together":
                preferred_model = ai_service.together_model
            else:
                preferred_model = _getenv("LOCAL_AI_MODEL") or ai_service.local_default_model
        try:
            ai_response = await ai_service.generate_completion(
                prompt=ai_prompt,
                model=preferred_model,
                max_tokens=getattr(ai_service, "llm_max_tokens_default", 900),
                temperature=0.2,
                fail_hard=True,
            )
        except httpx.HTTPStatusError as exc:
            detail = _http_error_detail(exc)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
        except Exception as exc:
            logger.error(f"Together completion failed: {exc}")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI provider unavailable")
        ai_response.prompt_used = ai_prompt
        try:
            ai_response.usage = ai_response.usage or {}
            ai_response.usage["redactions"] = dict(prompt_meta.get("redactions", {}))
            ai_response.usage["sanitized"] = {
                "instructions": prompt_meta.get("sanitized_instructions"),
                "upload_excerpt": prompt_meta.get("sanitized_upload"),
                "template": prompt_meta.get("sanitized_template"),
                "variables": prompt_meta.get("sanitized_variables"),
            }
        except Exception:
            pass
        
        generation_time = int((time.time() - start_time) * 1000)
        
        logger.info(f"? AI generation completed in {generation_time}ms")

        # Write to cache (best-effort)
        try:
            await cache_service.cache_ai_response(prompt_hash, {
                "content": ai_response.content,
                "tokens_used": ai_response.tokens_used,
                "model_used": ai_response.model_used,
                "generation_time_ms": generation_time,
                "cost_estimate": ai_response.cost_estimate,
                "redactions": dict(prompt_meta.get("redactions", {})),
                "sanitized": {
                    "instructions": prompt_meta.get("sanitized_instructions"),
                    "upload_excerpt": prompt_meta.get("sanitized_upload"),
                    "template": prompt_meta.get("sanitized_template"),
                    "variables": prompt_meta.get("sanitized_variables"),
                },
            }, ttl=3600)
        except Exception as _se:
            logger.warning(f"simple docgen cache set failed: {_se}")
        
        # Try structured rendering to HTML; fallback to sanitized text
        try:
            rendered_html = ai_service.format_document_json(ai_response.content)
        except Exception:
            rendered_html = None
        safe_content = rendered_html if rendered_html else ai_service._normalize_document_output(ai_response.content)
        if not safe_content or not safe_content.strip():
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI response did not contain usable content")

        return {
            "success": True,
            "document": {
                "id": f"doc_{uuid.uuid4().hex[:8]}",
                "title": title,
                "content": safe_content,
                "document_type": doc_type,
                "created_at": datetime.utcnow().isoformat(),
                "tokens_used": ai_response.tokens_used,
                "model_used": ai_response.model_used,
                "generation_time_ms": generation_time,
                "processing_time": generation_time / 1000,
                "confidence": 0.95,
                "cost_estimate": ai_response.cost_estimate,
                "metadata": {
                    "model_used": ai_response.model_used or preferred_model,
                    "generation_time_ms": generation_time,
                    "redactions": ai_response.usage.get("redactions") if ai_response.usage else None,
                    "sanitized": ai_response.usage.get("sanitized") if ai_response.usage else None,
                },
                "processing_state": "generated",
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"? AI document generation error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AI generation failed")

# Add missing import
import time

@app.get("/api/generate-test-doc")
async def generate_test_document():
    """Simple GET endpoint for document generation testing"""
    content = f"""# Testdokument

## Automatisch generiert am {datetime.utcnow().strftime('%d.%m.%Y um %H:%M Uhr')}

### Inhalt

Dies ist ein Testdokument von AnwaltsAI.

**Funktionen:**
- ? Backend-Verbindung
- ? Dokumentenerstellung  
- ? Deutsche Rechtsinhalte

### Rechtlicher Hinweis

Dieses Dokument dient nur zu Testzwecken.

---
*AnwaltsAI - Ihr KI-Partner f?r deutsche Rechtsdokumente*"""

    return {
        "success": True,
        "document": {
            "id": f"test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "title": "AnwaltsAI Testdokument",
            "content": content,
            "document_type": "test",
            "created_at": datetime.utcnow().isoformat(),
            "model_used": "Backend Template"
        }
    }

# =========================
# NOTIFICATIONS ENDPOINTS
# =========================

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Helper function to get current user ID"""
    global auth_service
    if not auth_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not initialized"
        )
    return auth_service.get_current_user_id(credentials)

@app.get("/api/notifications")
async def get_notifications(
    limit: int = 50,
    unread: bool = False,
    user_id: str = Depends(get_current_user_id)
):
    """Get user notifications"""
    try:
        # For demo purposes, return mock notifications
        # In real implementation, query database for user-specific notifications
        mock_notifications = [
            {
                "id": 1,
                "title": "Dokument erstellt",
                "message": "Ihr Kaufvertrag wurde erfolgreich generiert.",
                "type": "success",
                "timestamp": datetime.utcnow() - timedelta(minutes=5),
                "read": False,
                "icon": "file-check"
            },
            {
                "id": 2,
                "title": "E-Mail verarbeitet",
                "message": "Neue E-Mail von Mandant M?ller eingetroffen.",
                "type": "info",
                "timestamp": datetime.utcnow() - timedelta(minutes=15),
                "read": False,
                "icon": "mail"
            },
            {
                "id": 3,
                "title": "Template gespeichert",
                "message": "Neue Vorlage \"Mietvertrag\" wurde hinzugef?gt.",
                "type": "info",
                "timestamp": datetime.utcnow() - timedelta(hours=1),
                "read": True,
                "icon": "bookmark"
            },
            {
                "id": 4,
                "title": "System Update",
                "message": "AnwaltsAI wurde auf Version 2.1.0 aktualisiert.",
                "type": "warning",
                "timestamp": datetime.utcnow() - timedelta(days=1),
                "read": True,
                "icon": "alert-circle"
            }
        ]
        
        if unread:
            mock_notifications = [n for n in mock_notifications if not n['read']]
            
        if limit:
            mock_notifications = mock_notifications[:limit]
            
        return {
            "success": True,
            "notifications": mock_notifications,
            "total": len(mock_notifications),
            "unread_count": len([n for n in mock_notifications if not n['read']])
        }
        
    except Exception as e:
        logger.error(f"Get notifications error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Laden der Benachrichtigungen"
        )

@app.post("/api/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    user_id: str = Depends(get_current_user_id)
):
    """Mark a notification as read"""
    try:
        # In real implementation, update notification in database
        logger.info(f"Marking notification {notification_id} as read for user {user_id}")
        
        return {
            "success": True,
            "message": "Benachrichtigung als gelesen markiert"
        }
        
    except Exception as e:
        logger.error(f"Mark notification read error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Markieren der Benachrichtigung"
        )

@app.post("/api/notifications/mark-all-read")
async def mark_all_notifications_read(
    user_id: str = Depends(get_current_user_id)
):
    """Mark all notifications as read for user"""
    try:
        # In real implementation, update all user notifications in database
        logger.info(f"Marking all notifications as read for user {user_id}")
        
        return {
            "success": True,
            "message": "Alle Benachrichtigungen als gelesen markiert"
        }
        
    except Exception as e:
        logger.error(f"Mark all notifications read error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Markieren aller Benachrichtigungen"
        )

# =========================
# USER SETTINGS ENDPOINTS
# =========================

@app.get("/api/user/settings")
async def get_user_settings(
    user_id: str = Depends(get_current_user_id)
):
    """Get user settings"""
    try:
        # In real implementation, fetch from database
        # For now, return default settings
        default_settings = {
            "language": "de",
            "theme": "dark",
            "emailNotifications": True,
            "browserNotifications": False,
            "aiUpdates": True,
            "aiModel": "deepseek-v3",
            "aiCreativity": 70,
            "autoSave": True
        }
        
        return {
            "success": True,
            "settings": default_settings
        }
        
    except Exception as e:
        logger.error(f"Get user settings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Laden der Benutzereinstellungen"
        )

@app.post("/api/user/settings")
async def update_user_settings(
    settings: dict,
    user_id: str = Depends(get_current_user_id)
):
    """Update user settings"""
    try:
        # In real implementation, validate and save to database
        logger.info(f"Updating settings for user {user_id}: {settings}")
        
        # Validate settings structure (simplified)
        allowed_keys = {
            'language', 'theme', 'emailNotifications', 'browserNotifications',
            'aiUpdates', 'aiModel', 'aiCreativity', 'autoSave'
        }
        
        invalid_keys = set(settings.keys()) - allowed_keys
        if invalid_keys:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ung?ltige Einstellungsschl?ssel: {invalid_keys}"
            )
        
        # In real implementation: await db.update_user_settings(user_id, settings)
        
        return {
            "success": True,
            "message": "Benutzereinstellungen erfolgreich aktualisiert",
            "settings": settings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user settings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Speichern der Benutzereinstellungen"
        )

@app.put("/api/user/profile", response_model=UserProfileResponse)
async def update_user_profile_put(
    profile_data: UserProfileUpdate,
    current_user: UserInDB = Depends(get_current_user_flexible)
):
    """Alias for profile upsert using PUT.

    Persists extended profile fields to `user_profiles.data` and returns the
    portal identity only, keeping login identity independent from any linked
    email accounts.
    """
    return await upsert_user_profile(profile_data, current_user)  # type: ignore[arg-type]


# =========================
# SETTINGS ADMIN ENDPOINTS
# =========================


@app.get("/api/settings/overview")
async def settings_overview(current_user: UserInDB = Depends(get_current_user_flexible)):
    _assert_admin(current_user)
    cache_key = "settings:overview:v2"
    cache_ttl_seconds = 60
    metrics_payload: Optional[Dict[str, Any]] = None

    if cache_service:
        try:
            cached = await cache_service.get(cache_key)
            if isinstance(cached, dict):
                metrics_payload = cached
        except Exception as cache_err:  # pragma: no cover - diagnostic only
            logger.debug(f"Overview cache read failed: {cache_err}")

    if not metrics_payload:
        try:
            async with db.get_connection() as conn:
                active_users_total = int(
                    await conn.fetchval("SELECT COUNT(*) FROM users WHERE is_active = TRUE") or 0
                )
                new_users_current = int(
                    await conn.fetchval(
                        "SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '7 days'"
                    )
                    or 0
                )
                new_users_previous = int(
                    await conn.fetchval(
                        """
                        SELECT COUNT(*)
                        FROM users
                        WHERE created_at >= NOW() - INTERVAL '14 days'
                          AND created_at < NOW() - INTERVAL '7 days'
                        """
                    )
                    or 0
                )

                documents_total = int(await conn.fetchval("SELECT COUNT(*) FROM documents") or 0)
                documents_current = int(
                    await conn.fetchval(
                        "SELECT COUNT(*) FROM documents WHERE created_at >= NOW() - INTERVAL '7 days'"
                    )
                    or 0
                )
                documents_previous = int(
                    await conn.fetchval(
                        """
                        SELECT COUNT(*)
                        FROM documents
                        WHERE created_at >= NOW() - INTERVAL '14 days'
                          AND created_at < NOW() - INTERVAL '7 days'
                        """
                    )
                    or 0
                )

                cases_current = int(
                    await conn.fetchval(
                        """
                        SELECT COUNT(*)
                        FROM analytics_events
                        WHERE created_at >= NOW() - INTERVAL '7 days'
                          AND (event_type ILIKE 'case%' OR event_type ILIKE 'matter%' OR event_type ILIKE 'mandat%')
                        """
                    )
                    or 0
                )
                cases_previous = int(
                    await conn.fetchval(
                        """
                        SELECT COUNT(*)
                        FROM analytics_events
                        WHERE created_at >= NOW() - INTERVAL '14 days'
                          AND created_at < NOW() - INTERVAL '7 days'
                          AND (event_type ILIKE 'case%' OR event_type ILIKE 'matter%' OR event_type ILIKE 'mandat%')
                        """
                    )
                    or 0
                )

                api_row = await conn.fetchrow(
                    """
                    SELECT
                        COALESCE(SUM(request_count), 0) AS total_calls,
                        COALESCE(SUM(total_latency_ms), 0) AS total_latency,
                        COALESCE(SUM(success_count), 0) AS success_calls,
                        COALESCE(SUM(error_count), 0) AS error_calls
                    FROM api_request_metrics
                    WHERE bucket_start >= NOW() - INTERVAL '7 days'
                    """
                )
                api_prev_row = await conn.fetchrow(
                    """
                    SELECT COALESCE(SUM(request_count), 0) AS total_calls
                    FROM api_request_metrics
                    WHERE bucket_start >= NOW() - INTERVAL '14 days'
                      AND bucket_start < NOW() - INTERVAL '7 days'
                    """
                )

                templates_total = int(
                    await conn.fetchval("SELECT COUNT(*) FROM templates") or 0
                )
                webhooks_total = int(
                    await conn.fetchval(
                        "SELECT COUNT(*) FROM webhooks WHERE is_active IS DISTINCT FROM FALSE"
                    )
                    or 0
                )

                user_growth_rows = await conn.fetch(
                    """
                    SELECT date_trunc('day', created_at) AS day, COUNT(*) AS count
                    FROM users
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    GROUP BY 1
                    ORDER BY 1
                    """
                )
                api_usage_rows = await conn.fetch(
                    """
                    SELECT date_trunc('day', bucket_start) AS day,
                           SUM(success_count + error_count) AS count
                    FROM api_request_metrics
                    WHERE bucket_start >= NOW() - INTERVAL '30 days'
                    GROUP BY 1
                    ORDER BY 1
                    """
                )
        except Exception as e:
            logger.error(f"Settings overview query error: {e}")
            raise HTTPException(status_code=500, detail="Konnte ?bersichtsdaten nicht laden")

        start_date = datetime.utcnow().date() - timedelta(days=29)
        user_map = {row["day"].date(): int(row["count"]) for row in user_growth_rows}
        api_map = {row["day"].date(): int(row["count"] or 0) for row in api_usage_rows}

        user_growth: List[Dict[str, Any]] = []
        api_usage: List[Dict[str, Any]] = []
        for i in range(30):
            day = start_date + timedelta(days=i)
            day_dt = datetime.combine(day, datetime.min.time()).replace(tzinfo=timezone.utc)
            user_growth.append({"date": day_dt.isoformat(), "value": user_map.get(day, 0)})
            api_usage.append({"date": day_dt.isoformat(), "value": api_map.get(day, 0)})

        api_total_calls = int(api_row["total_calls"] or 0) if api_row else 0
        api_success_calls = int(api_row["success_calls"] or 0) if api_row else 0
        api_error_calls = int(api_row["error_calls"] or 0) if api_row else 0
        api_total_latency = int(api_row["total_latency"] or 0) if api_row else 0
        api_avg_latency = 0.0
        if api_total_calls > 0:
            api_avg_latency = round(api_total_latency / api_total_calls, 2)

        generated_at = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
        metrics_payload = {
            "generatedAt": generated_at,
            "users": {
                "active_total": active_users_total,
                "new_current": new_users_current,
                "new_previous": new_users_previous,
            },
            "documents": {
                "total": documents_total,
                "current": documents_current,
                "previous": documents_previous,
            },
            "cases": {
                "current": cases_current,
                "previous": cases_previous,
            },
            "api": {
                "total_current": api_total_calls,
                "total_previous": int(api_prev_row["total_calls"] or 0) if api_prev_row else 0,
                "success_calls": api_success_calls,
                "error_calls": api_error_calls,
                "avg_latency_ms": api_avg_latency,
            },
            "templates_total": templates_total,
            "webhooks_total": webhooks_total,
            "userGrowth": user_growth,
            "apiUsage": api_usage,
        }

        if cache_service:
            try:
                await cache_service.set(cache_key, metrics_payload, ttl=cache_ttl_seconds)
            except Exception as cache_err:  # pragma: no cover - diagnostic only
                logger.debug(f"Overview cache write failed: {cache_err}")

    users_data = metrics_payload["users"]
    documents_data = metrics_payload["documents"]
    cases_data = metrics_payload["cases"]
    api_data = metrics_payload["api"]

    # Run live health checks and log telemetry
    db_latency_ms: Optional[int] = None
    redis_latency_ms: Optional[int] = None
    ai_latency_ms: Optional[int] = None

    db_status_ok = False
    start_timer = time.perf_counter()
    try:
        await db.health_check()
        db_latency_ms = int((time.perf_counter() - start_timer) * 1000)
        db_status_ok = True
    except Exception:
        db_status_ok = False
    await db.log_service_health("postgres", db_status_ok, db_latency_ms)

    redis_status_ok = False
    if cache_service:
        redis_status_ok, redis_latency_ms = await cache_service.ping_with_latency()
        await db.log_service_health("redis", redis_status_ok, redis_latency_ms)

    ai_status_ok = False
    ai_status_label = "Betriebsbereit"
    if ai_service:
        try:
            start_timer = time.perf_counter()
            ai_response = await ai_service.generate_completion(
                prompt="health",
                model=ai_service.together_model
                if ai_service.provider == "together"
                else ai_service.local_default_model,
                max_tokens=8,
                temperature=0.1,
                fail_hard=True,
            )
            ai_latency_ms = (
                ai_response.generation_time_ms
                if hasattr(ai_response, "generation_time_ms")
                and ai_response.generation_time_ms is not None
                else int((time.perf_counter() - start_timer) * 1000)
            )
            ai_status_ok = True
        except Exception:
            ai_status_label = "Eingeschr?nkt"
            ai_status_ok = False
    await db.log_service_health("ai_service", ai_status_ok, ai_latency_ms)

    total_calls = int(api_data.get("total_current", 0) or 0)
    success_calls = int(api_data.get("success_calls", 0) or 0)
    error_calls = int(api_data.get("error_calls", 0) or 0)
    avg_latency_ms = api_data.get("avg_latency_ms")
    webserver_status_ok = total_calls == 0 or success_calls >= error_calls
    await db.log_service_health(
        "webserver",
        webserver_status_ok,
        int(avg_latency_ms) if isinstance(avg_latency_ms, (int, float)) else None,
    )

    health_summary = await db.get_service_health_summary(
        ["postgres", "redis", "ai_service", "webserver"], window_minutes=1440
    )

    def build_health_entry(key: str, label: str, fallback_status: str = "St?rung") -> Dict[str, Any]:
        data = health_summary.get(key, {})
        uptime = data.get("uptime")
        latest_status = data.get("latest_status")
        latency = data.get("avg_latency_ms")
        if latest_status is True:
            status = "Betriebsbereit" if (uptime is None or uptime >= 95) else "Eingeschr?nkt"
        elif latest_status is False:
            status = "St?rung"
        else:
            status = fallback_status
        entry = {
            "name": label,
            "status": status,
            "uptime": uptime,
        }
        if latency is not None:
            entry["latency_ms"] = round(latency, 2)
        return entry

    system_health = [
        build_health_entry("postgres", "PostgreSQL"),
        build_health_entry("redis", "Redis Cache"),
        {
            **build_health_entry("ai_service", "KI-Service", ai_status_label),
            "latency_ms": ai_latency_ms if ai_latency_ms is not None else None,
        },
        build_health_entry("webserver", "Webserver"),
    ]

    kpis = [
        {
            "label": "Aktive Benutzer",
            "value": _format_metric_value(users_data["active_total"]),
            "change": _percent_change(users_data["new_current"], users_data["new_previous"]),
            "iconPath": "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z",
            "iconBg": "bg-blue-100",
            "iconColor": "text-blue-600",
        },
        {
            "label": "Dokumente",
            "value": _format_metric_value(documents_data["total"]),
            "change": _percent_change(documents_data["current"], documents_data["previous"]),
            "iconPath": "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
            "iconBg": "bg-green-100",
            "iconColor": "text-green-600",
        },
        {
            "label": "Neue F?lle",
            "value": _format_metric_value(cases_data["current"]),
            "change": _percent_change(cases_data["current"], cases_data["previous"]),
            "iconPath": "M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z",
            "iconBg": "bg-yellow-100",
            "iconColor": "text-yellow-600",
        },
        {
            "label": "API-Aufrufe",
            "value": _format_metric_value(api_data["total_current"]),
            "change": _percent_change(api_data["total_current"], api_data["total_previous"]),
            "iconPath": "M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 00-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01",
            "iconBg": "bg-purple-100",
            "iconColor": "text-purple-600",
        },
    ]

    api_success_rate = 0.0
    if total_calls > 0:
        api_success_rate = round((success_calls / total_calls) * 100, 2)

    return {
        "generatedAt": metrics_payload["generatedAt"],
        "kpis": kpis,
        "userGrowth": metrics_payload["userGrowth"],
        "apiUsage": metrics_payload["apiUsage"],
        "systemHealth": system_health,
        "meta": {
            "users": users_data,
            "documents": documents_data,
            "cases": cases_data,
            "api": {
                **api_data,
                "success_rate": api_success_rate,
                "avg_latency_ms": avg_latency_ms,
            },
            "templates_total": metrics_payload.get("templates_total", 0),
            "webhooks_total": metrics_payload.get("webhooks_total", 0),
        },
    }


@app.get("/api/settings/preferences")
async def get_settings_preferences(current_user: UserInDB = Depends(get_current_user_flexible)):
    _assert_admin(current_user)
    prefs = await db.get_org_settings()
    return {"preferences": prefs}


@app.post("/api/settings/preferences")
async def update_settings_preferences(payload: SettingsPreferences, current_user: UserInDB = Depends(get_current_user_flexible)):
    _assert_admin(current_user)
    saved = await db.upsert_org_settings(payload.model_dump(), current_user.id)
    return {"success": True, "preferences": saved}


@app.get("/api/settings/api/tokens")
async def list_settings_tokens(current_user: UserInDB = Depends(get_current_user_flexible)):
    _assert_admin(current_user)
    tokens = await db.list_api_tokens(current_user.id)
    for token in tokens:
        token["id"] = str(token.get("id"))
        if token.get("created_at"):
            token["created_at"] = token["created_at"].isoformat()
        if token.get("expires_at"):
            token["expires_at"] = token["expires_at"].isoformat()
        if token.get("last_used_at"):
            token["last_used_at"] = token["last_used_at"].isoformat()
        token.pop("revoked_at", None)
    return {"tokens": tokens}


@app.post("/api/settings/api/tokens")
async def create_settings_token(payload: ApiTokenCreateRequest, current_user: UserInDB = Depends(get_current_user_flexible)):
    _assert_admin(current_user)
    expires_days = payload.expires_in_days or 365
    expires_at = datetime.utcnow() + timedelta(days=expires_days)
    raw_token = f"anw_{uuid.uuid4().hex}{uuid.uuid4().hex}"
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    metadata = await db.create_api_token(current_user.id, token_hash, expires_at, raw_token[-4:])
    metadata["created_at"] = metadata["created_at"].isoformat()
    metadata["expires_at"] = metadata["expires_at"].isoformat()
    metadata["active"] = True
    return {"token": raw_token, "metadata": metadata}


@app.delete("/api/settings/api/tokens/{token_id}")
async def revoke_settings_token(token_id: str, current_user: UserInDB = Depends(get_current_user_flexible)):
    _assert_admin(current_user)
    try:
        token_uuid = uuid.UUID(token_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Ung?ltige Token-ID")
    success = await db.revoke_api_token(current_user.id, token_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Token nicht gefunden")
    return {"success": True}


@app.get("/api/settings/api/endpoints")
async def get_api_endpoint_metrics(current_user: UserInDB = Depends(get_current_user_flexible), window_days: int = Query(7, ge=1, le=30)):
    _assert_admin(current_user)
    metrics = await db.get_api_endpoint_metrics(window_days)
    return {"metrics": metrics}


@app.get("/api/settings/webhooks")
async def list_webhooks_route(current_user: UserInDB = Depends(get_current_user_flexible)):
    _assert_admin(current_user)
    webhooks = await db.list_webhooks()
    result = []
    for record in webhooks:
        webhook_id = record.get("id")
        logs = []
        if webhook_id:
            logs_raw = await db.list_webhook_logs(webhook_id, limit=5)
            for log in logs_raw:
                logs.append(
                    {
                        "id": str(log["id"]),
                        "status": log.get("status_code"),
                        "latency_ms": log.get("latency_ms"),
                        "response": log.get("response_body"),
                        "timestamp": log.get("created_at").isoformat() if log.get("created_at") else None,
                    }
                )
        result.append(
            {
                "id": str(webhook_id),
                "name": record.get("name"),
                "url": record.get("url"),
                "events": record.get("events") or [],
                "is_active": record.get("is_active", True),
                "created_at": record.get("created_at").isoformat() if record.get("created_at") else None,
                "updated_at": record.get("updated_at").isoformat() if record.get("updated_at") else None,
                "has_secret": bool(record.get("secret")),
                "recent_logs": logs,
            }
        )
    return {"webhooks": result}


@app.post("/api/settings/webhooks")
async def create_webhook_route(payload: WebhookRequest, current_user: UserInDB = Depends(get_current_user_flexible)):
    _assert_admin(current_user)
    record = await db.create_webhook(
        name=payload.name,
        url=str(payload.url),
        events=payload.events,
        is_active=payload.is_active,
        secret=payload.secret,
        created_by=current_user.id,
    )
    record["id"] = record["id"] if isinstance(record["id"], str) else str(record["id"])
    record["created_at"] = record["created_at"].isoformat() if record.get("created_at") else None
    record["updated_at"] = record.get("updated_at").isoformat() if record.get("updated_at") else None
    record.pop("secret", None)
    record["recent_logs"] = []
    return record


@app.put("/api/settings/webhooks/{webhook_id}")
async def update_webhook_route(webhook_id: str, payload: WebhookRequest, current_user: UserInDB = Depends(get_current_user_flexible)):
    _assert_admin(current_user)
    try:
        webhook_uuid = uuid.UUID(webhook_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Ung?ltige Webhook-ID")
    updated = await db.update_webhook(
        webhook_uuid,
        payload.name,
        str(payload.url),
        payload.events,
        payload.is_active,
        payload.secret,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Webhook nicht gefunden")
    refreshed = await db.get_webhook(webhook_uuid)
    if not refreshed:
        raise HTTPException(status_code=404, detail="Webhook nicht gefunden")
    refreshed["id"] = str(refreshed["id"])
    refreshed["created_at"] = refreshed.get("created_at").isoformat() if refreshed.get("created_at") else None
    refreshed["updated_at"] = refreshed.get("updated_at").isoformat() if refreshed.get("updated_at") else None
    refreshed["has_secret"] = bool(refreshed.get("secret"))
    refreshed.pop("secret", None)
    refreshed["recent_logs"] = []
    return refreshed


@app.delete("/api/settings/webhooks/{webhook_id}")
async def delete_webhook_route(webhook_id: str, current_user: UserInDB = Depends(get_current_user_flexible)):
    _assert_admin(current_user)
    try:
        webhook_uuid = uuid.UUID(webhook_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Ung?ltige Webhook-ID")
    success = await db.delete_webhook(webhook_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook nicht gefunden")
    return {"success": True}


@app.post("/api/settings/webhooks/{webhook_id}/test")
async def test_webhook_route(webhook_id: str, current_user: UserInDB = Depends(get_current_user_flexible)):
    _assert_admin(current_user)
    try:
        webhook_uuid = uuid.UUID(webhook_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Ung?ltige Webhook-ID")
    webhook = await db.get_webhook(webhook_uuid)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook nicht gefunden")

    payload = {
        "event": "webhook.test",
        "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
        "source": "anwalts-ai",
        "data": {"message": "Testausl?sung vom Administrationsbereich"},
    }

    headers = {"Content-Type": "application/json", "User-Agent": "AnwaltsAI-WebhookTester/1.0"}
    secret = webhook.get("secret")
    if secret:
        signature = hmac.new(secret.encode("utf-8"), json.dumps(payload).encode("utf-8"), hashlib.sha256).hexdigest()
        headers["X-Anwalts-Signature"] = signature

    status_code = None
    latency_ms = None
    response_text = None
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            start = time.perf_counter()
            response = await client.post(webhook.get("url"), json=payload, headers=headers)
            latency_ms = int((time.perf_counter() - start) * 1000)
            status_code = response.status_code
            response_text = response.text[:512]
    except Exception as exc:
        status_code = None
        response_text = str(exc)

    await db.record_webhook_log(webhook_uuid, status_code, latency_ms, response_text)
    return {
        "status": status_code,
        "latency_ms": latency_ms,
        "response": response_text,
    }


@app.get("/api/settings/users")
async def list_users_route(
    current_user: UserInDB = Depends(get_current_user_flexible),
    search: Optional[str] = Query(default=None),
    role: Optional[str] = Query(default="all"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
):
    _assert_admin(current_user)
    offset = (page - 1) * page_size
    users_rows, total = await db.list_users_paginated(search=search, role=role, limit=page_size, offset=offset)
    users_payload = []
    for row in users_rows:
        users_payload.append(
            {
                "id": str(row.get("id")),
                "email": row.get("email"),
                "name": row.get("name"),
                "role": row.get("role"),
                "created_at": row.get("created_at").isoformat() if row.get("created_at") else None,
                "is_active": row.get("is_active", True),
                "last_activity": row.get("last_activity").isoformat() if row.get("last_activity") else None,
            }
        )
    return {
        "users": users_payload,
        "page": page,
        "pageSize": page_size,
        "total": total,
    }


@app.post("/api/settings/users/{user_id}/toggle")
async def toggle_user_activation(user_id: str, payload: UserActivationRequest = None, current_user: UserInDB = Depends(get_current_user_flexible)):
    _assert_admin(current_user)
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Ung?ltige Benutzer-ID")

    target_user = await db.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    desired_state = payload.active if payload and payload.active is not None else not target_user.is_active
    if not await db.set_user_active_state(user_uuid, desired_state):
        raise HTTPException(status_code=500, detail="Status konnte nicht aktualisiert werden")

    refreshed = await db.get_user_by_id(user_id)
    return {
        "id": str(refreshed.id),
        "is_active": refreshed.is_active,
    }


# ============ ADMIN SETTINGS ENDPOINTS ============

@app.get("/api/admin/settings")
async def get_admin_settings(current_user: UserInDB = Depends(get_current_user_flexible)):
    """Get comprehensive system settings (admin only)"""
    _assert_admin(current_user)
    
    # Get organization settings (most recent)
    try:
        async with db.get_connection() as conn:
            org_settings_row = await conn.fetchrow(
                "SELECT * FROM organization_settings ORDER BY updated_at DESC LIMIT 1"
            )
            org_settings = dict(org_settings_row) if org_settings_row else {}
    except Exception as e:
        logger.warning(f"Could not fetch organization_settings: {e}")
        org_settings = {}
    
    # Get system statistics
    try:
        async with db.get_connection() as conn:
            stats_row = await conn.fetchrow("""
                SELECT 
                    (SELECT COUNT(*) FROM users WHERE is_active = true) as active_users,
                    (SELECT COUNT(*) FROM email_accounts WHERE revoked_at IS NULL) as connected_emails,
                    (SELECT COUNT(*) FROM documents) as total_documents,
                    (SELECT COUNT(*) FROM templates) as total_templates,
                    (SELECT COUNT(*) FROM api_tokens WHERE revoked_at IS NULL) as active_tokens,
                    (SELECT COUNT(*) FROM webhooks WHERE is_active = true) as active_webhooks
            """)
            stats = dict(stats_row) if stats_row else {
                "active_users": 0,
                "connected_emails": 0,
                "total_documents": 0,
                "total_templates": 0,
                "active_tokens": 0,
                "active_webhooks": 0
            }
    except Exception as e:
        logger.warning(f"Could not fetch statistics: {e}")
        stats = {
            "active_users": 0,
            "connected_emails": 0,
            "total_documents": 0,
            "total_templates": 0,
            "active_tokens": 0,
            "active_webhooks": 0
        }
    
    # Get recent system activity (last 7 days)
    try:
        async with db.get_connection() as conn:
            recent_activity_rows = await conn.fetch("""
                SELECT 
                    event_type, 
                    COUNT(*) as count,
                    MAX(created_at) as last_occurrence
                FROM analytics_events
                WHERE created_at > NOW() - INTERVAL '7 days'
                GROUP BY event_type
                ORDER BY count DESC
                LIMIT 10
            """)
            recent_activity = [dict(row) for row in recent_activity_rows] if recent_activity_rows else []
    except Exception as e:
        logger.warning(f"Could not fetch recent activity: {e}")
        recent_activity = []
    
    return {
        "organization": org_settings,
        "statistics": stats,
        "recent_activity": recent_activity,
        "current_user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role
        }
    }


@app.put("/api/admin/settings/organization")
async def update_organization_settings(
    settings: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update organization settings (admin only)"""
    _assert_admin(current_user)
    
    allowed_fields = [
        "language", "timezone", "require_two_factor", "enable_sso",
        "password_min_length", "password_require_special", "password_require_numbers",
        "email_notifications", "browser_notifications", "ai_updates",
        "ai_model", "ai_creativity", "auto_save"
    ]
    
    # Build UPDATE query dynamically
    updates = []
    values = []
    for field, value in settings.items():
        if field in allowed_fields:
            updates.append(f"{field} = ${len(values) + 1}")
            values.append(value)
    
    if not updates:
        raise HTTPException(400, "No valid fields to update")
    
    values.append(str(current_user.id))  # updated_by
    
    try:
        query = f"""
            UPDATE organization_settings 
            SET {', '.join(updates)}, updated_at = NOW(), updated_by = ${len(values)}
            WHERE id = (SELECT id FROM organization_settings ORDER BY updated_at DESC LIMIT 1)
            RETURNING *
        """
        
        async with db.get_connection() as conn:
            result = await conn.fetchrow(query, *values)
            
            if not result:
                # If no row exists, insert a new one
                insert_fields = allowed_fields + ["updated_by"]
                insert_values = [settings.get(f) for f in allowed_fields] + [str(current_user.id)]
                placeholders = [f"${i+1}" for i in range(len(insert_values))]
                
                insert_query = f"""
                    INSERT INTO organization_settings ({', '.join(insert_fields)}, updated_at)
                    VALUES ({', '.join(placeholders)}, NOW())
                    RETURNING *
                """
                result = await conn.fetchrow(insert_query, *insert_values)
        
        return dict(result) if result else {}
    except Exception as e:
        logger.error(f"Failed to update organization settings: {e}")
        raise HTTPException(500, f"Failed to update settings: {str(e)}")


@app.post("/api/settings/users/{user_id}/role")
async def update_user_role(user_id: str, payload: UserRoleUpdateRequest, current_user: UserInDB = Depends(get_current_user_flexible)):
    _assert_admin(current_user)
    target_role = payload.role.strip().lower()
    allowed_roles = {"admin", "staff", "viewer", "assistant", "owner"}
    if target_role not in allowed_roles:
        raise HTTPException(status_code=400, detail="Ung?ltige Rolle")
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Ung?ltige Benutzer-ID")
    if not await db.change_user_role(user_uuid, target_role):
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    refreshed = await db.get_user_by_id(user_id)
    return {
        "id": str(refreshed.id),
        "role": refreshed.role,
    }


@app.get("/api/settings/export.csv")
async def export_settings_csv(current_user: UserInDB = Depends(get_current_user_flexible)):
    _assert_admin(current_user)
    snapshot = await db.export_snapshot()

    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow(["users"])
    writer.writerow(["id", "email", "name", "role", "is_active", "created_at"])
    for user in snapshot.get("users", []):
        writer.writerow([
            user.get("id"),
            user.get("email"),
            user.get("name"),
            user.get("role"),
            user.get("is_active"),
            user.get("created_at"),
        ])

    writer.writerow([])
    writer.writerow(["documents"])
    writer.writerow(["id", "user_id", "title", "created_at"])
    for doc in snapshot.get("documents", []):
        writer.writerow([doc.get("id"), doc.get("user_id"), doc.get("title"), doc.get("created_at")])

    writer.writerow([])
    writer.writerow(["templates"])
    writer.writerow(["id", "user_id", "title", "category", "created_at"])
    for tpl in snapshot.get("templates", []):
        writer.writerow([
            tpl.get("id"), tpl.get("user_id"), tpl.get("title"), tpl.get("category"), tpl.get("created_at")
        ])

    writer.writerow([])
    writer.writerow(["webhooks"])
    writer.writerow(["id", "name", "url", "events", "is_active", "created_at"])
    for wh in snapshot.get("webhooks", []):
        writer.writerow([
            wh.get("id"),
            wh.get("name"),
            wh.get("url"),
            "|".join(wh.get("events", [])),
            wh.get("is_active"),
            wh.get("created_at"),
        ])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue().encode("utf-8")]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=anwalts-settings-export.csv"},
    )


@app.get("/api/settings/export.json")
async def export_settings_json(current_user: UserInDB = Depends(get_current_user_flexible)):
    _assert_admin(current_user)
    snapshot = await db.export_snapshot()
    payload = json.dumps(snapshot, default=str)
    return StreamingResponse(
        iter([payload.encode("utf-8")]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=anwalts-settings-export.json"},
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        await db.health_check()
        
        # Check cache connection (optional)
        cache_status = "not configured"
        if cache_service:
            cache_healthy = await cache_service.health_check()
            cache_status = "healthy" if cache_healthy else "unhealthy"
        
        # Check AI service (non-blocking)
        ai_status = "unknown"
        try:
            test_response = await ai_service.generate_completion(
                prompt="Test",
                model=ai_service.together_model if ai_service.provider == "together" else ai_service.local_default_model,
                max_tokens=5,
                temperature=0.1,
                fail_hard=True
            )
            ai_status = "healthy" if test_response.content else "degraded"
        except Exception:
            ai_status = "degraded"
        
        return {
            "status": "healthy" if ai_status != "unhealthy" else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "healthy",
                "cache": cache_status,
                "ai_service": {
                    "status": ai_status,
                    "provider": ai_service.provider,
                    "model": ai_service.together_model if ai_service.provider == "together" else ai_service.local_default_model
                }
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

@app.get("/api/health")
async def health_check_api_alias():
    return await health_check()

@app.get("/health/ai")
async def health_check_ai():
    """AI service health check endpoint"""
    try:
        start = time.time()
        response = await ai_service.generate_completion(
            prompt="Test",
            model=ai_service.together_model if ai_service.provider == "together" else ai_service.local_default_model,
            max_tokens=10,
            temperature=0.1,
            fail_hard=True
        )
        latency_ms = int((time.time() - start) * 1000)
        
        return {
            "status": "healthy",
            "provider": ai_service.provider,
            "model": response.model or (ai_service.together_model if ai_service.provider == "together" else ai_service.local_default_model),
            "latency_ms": latency_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "provider": ai_service.provider,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    
# ============ API TOKENS (reuse sessions table) ============

@app.get("/api/tokens")
async def list_tokens(current_user: UserInDB = Depends(get_current_user)):
    try:
        tokens = await db.list_api_tokens(current_user.id)
        formatted = []
        for token in tokens:
            formatted.append(
                {
                    "id": str(token.get("id")),
                    "last4": token.get("last4"),
                    "expires_at": token.get("expires_at").isoformat() if token.get("expires_at") else None,
                    "created_at": token.get("created_at").isoformat() if token.get("created_at") else None,
                    "last_used_at": token.get("last_used_at").isoformat() if token.get("last_used_at") else None,
                    "active": token.get("active", True),
                }
            )
        return {"tokens": formatted}
    except Exception as e:
        logger.error(f"List tokens error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list tokens")

@app.post("/api/tokens")
async def create_token(payload: dict, current_user: UserInDB = Depends(get_current_user)):
    try:
        expires_days = int(payload.get("expires_in_days") or 365)
        expires_at = datetime.utcnow() + timedelta(days=expires_days)

        raw = uuid.uuid4().hex + uuid.uuid4().hex
        token = f"anw_{raw}"
        last4 = token[-4:]
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        rec = await db.create_api_token(current_user.id, token_hash, expires_at, last4)
        rec["created_at"] = rec.get("created_at").isoformat() if rec.get("created_at") else None
        rec["expires_at"] = rec.get("expires_at").isoformat() if rec.get("expires_at") else None
        rec["active"] = True
        return {"token": token, "metadata": rec}
    except Exception as e:
        logger.error(f"Create token error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create token")

@app.delete("/api/tokens/{token_id}")
async def revoke_token(token_id: str, current_user: UserInDB = Depends(get_current_user)):
    try:
        tid = uuid.UUID(token_id)
        ok = await db.revoke_api_token(current_user.id, tid)
        if not ok:
            raise HTTPException(status_code=404, detail="Token not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Revoke token error: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke token")

# ============ PUBLIC ALIAS PROXY ============

_ALLOWED_ALIAS: List[str] = []

def _is_allowed_target(url: str) -> bool:
    try:
        from urllib.parse import urlparse
        u = urlparse(url)
        if u.scheme not in ("http", "https"):
            return False
        if not u.hostname:
            return False
        if not _ALLOWED_ALIAS:
            return True
        host = u.hostname.lower()
        return host in _ALLOWED_ALIAS
    except Exception:
        return False

_user_aliases: Dict[str, Dict[str, Any]] = {}

def _alias_key(user_id: str, slug: str) -> str:
    return f"{user_id}:{slug}"

@app.get("/api/aliases")
async def list_aliases(current_user: UserInDB = Depends(get_current_user)):
    try:
        result = []
        prefix = f"{current_user.id}:"
        for key, val in _user_aliases.items():
            if key.startswith(prefix):
                result.append({
                    "id": hashlib.sha1(key.encode()).hexdigest()[:16],
                    "slug": key.split(":", 1)[1],
                    "method": val["method"],
                    "targetUrl": val["target"],
                    "forwardHeaders": val.get("headers", []),
                    "enabled": True,
                    "createdAt": val.get("created_at"),
                })
        return {"aliases": result}
    except Exception as e:
        logger.error(f"List aliases error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list aliases")

@app.post("/api/aliases")
async def create_alias(payload: dict, current_user: UserInDB = Depends(get_current_user)):
    try:
        slug = (payload.get("slug") or "").strip()
        method = (payload.get("method") or "POST").upper()
        target = (payload.get("targetUrl") or "").strip()
        headers = payload.get("forwardHeaders") or []

        if not re.fullmatch(r"[a-z0-9-]{3,64}", slug or ""):
            raise HTTPException(status_code=400, detail="Invalid slug")
        if method not in {"GET","POST","PUT","PATCH","DELETE"}:
            raise HTTPException(status_code=400, detail="Invalid method")
        if not _is_allowed_target(target):
            raise HTTPException(status_code=400, detail="Target URL not allowed")

        key = _alias_key(str(current_user.id), slug)
        _user_aliases[key] = {
            "method": method,
            "target": target,
            "headers": [h for h in headers if isinstance(h, str) and h],
            "created_at": datetime.utcnow().isoformat(),
        }
        return {"alias": {
            "id": hashlib.sha1(key.encode()).hexdigest()[:16],
            "slug": slug,
            "method": method,
            "targetUrl": target,
            "forwardHeaders": headers,
            "enabled": True,
            "createdAt": _user_aliases[key]["created_at"],
        }}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create alias error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create alias")

@app.delete("/api/aliases")
async def delete_alias(payload: dict, current_user: UserInDB = Depends(get_current_user)):
    try:
        alias_id = payload.get("id")
        if not alias_id:
            raise HTTPException(status_code=400, detail="Missing id")
        to_delete = None
        prefix = f"{current_user.id}:"
        for key in list(_user_aliases.keys()):
            if key.startswith(prefix):
                if hashlib.sha1(key.encode()).hexdigest()[:16] == alias_id:
                    to_delete = key
                    break
        if not to_delete:
            raise HTTPException(status_code=404, detail="Not found")
        _user_aliases.pop(to_delete, None)
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete alias error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete alias")

# =========================
# CALL REQUEST ENDPOINTS
# =========================

@app.post("/api/call-requests", response_model=CallRequestResponse)
async def create_call_request(request_data: CallRequestCreate, request: Request):
    """Submit a call request from the landing page"""
    try:
        # Get client IP and user agent
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Create call request
        call_request = await db.create_call_request(
            name=request_data.name,
            phone=request_data.phone,
            email=request_data.email,
            preferred_time=request_data.preferred_time,
            consultation_type=request_data.consultation_type,
            notes=request_data.notes,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        # Trigger webhook for n8n integration
        try:
            webhook_data = {
                "id": str(call_request['id']),
                "name": call_request['name'],
                "phone": call_request['phone'],
                "email": call_request['email'],
                "preferred_time": call_request['preferred_time'],
                "consultation_type": call_request['consultation_type'],
                "notes": call_request['notes'],
                "created_at": call_request['created_at'].isoformat(),
                "source": "website"
            }
            
            # Send to webhook asynchronously (don't block response)
            asyncio.create_task(send_webhook(webhook_data))
            
        except Exception as webhook_error:
            logger.error(f"Webhook error: {webhook_error}")
            # Don't fail the request if webhook fails
        
        logger.info(f"Call request created: {call_request['id']} for {call_request['name']}")
        
        return CallRequestResponse(
            id=call_request['id'],
            name=call_request['name'],
            phone=call_request['phone'],
            email=call_request['email'],
            status=call_request['status'],
            preferred_time=call_request['preferred_time'],
            consultation_type=call_request['consultation_type'],
            notes=call_request['notes'],
            created_at=call_request['created_at'],
            updated_at=call_request['updated_at']
        )
        
    except Exception as e:
        logger.error(f"Call request creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create call request"
        )

# =========================
# WEBHOOK ENDPOINTS  
# =========================

async def send_webhook(data: dict):
    """Send webhook to n8n for call request processing"""
    webhook_url = os.getenv("N8N_WEBHOOK_URL")
    if not webhook_url:
        logger.warning("N8N_WEBHOOK_URL not configured")
        return
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=data,
                timeout=10.0
            )
            if response.status_code == 200:
                logger.info(f"Webhook sent successfully for call request {data['id']}")
            else:
                logger.error(f"Webhook failed with status {response.status_code}")
    except Exception as e:
        logger.error(f"Webhook send error: {e}")

@app.api_route("/alias/{slug}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def alias_proxy(slug: str, request: Request):
    """Public alias endpoint: Authorization: Bearer <API token> required."""
    try:
        auth = request.headers.get("authorization") or ""
        token = auth.split(" ", 1)[1] if auth.lower().startswith("bearer ") else None
        if not token:
            raise HTTPException(status_code=401, detail="Missing bearer token")

        owner = await db.get_api_token_owner(token)
        if not owner:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        key = _alias_key(owner["user_id"], slug)
        cfg = _user_aliases.get(key)
        if not cfg:
            raise HTTPException(status_code=404, detail="Alias not found")
        if request.method != cfg["method"]:
            raise HTTPException(status_code=405, detail=f"Method not allowed; use {cfg['method']}")

        # Prepare outbound request
        headers: Dict[str, str] = {}
        for h in cfg.get("headers", []):
            val = request.headers.get(h)
            if val:
                headers[h] = val
        ct = request.headers.get("content-type")
        if ct:
            headers["content-type"] = ct

        body = await request.body() if request.method not in ("GET", "HEAD") else None
        timeout = httpx.Timeout(60.0, read=300.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
            resp = await client.request(cfg["method"], cfg["target"], headers=headers, content=body)
            safe_headers = {k: v for k, v in resp.headers.items() if k.lower() not in {"transfer-encoding", "connection"}}
            return FastAPIResponse(content=resp.content, status_code=resp.status_code, headers=safe_headers)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Alias proxy error for {slug}: {e}")
        raise HTTPException(status_code=500, detail="Proxy failed")
