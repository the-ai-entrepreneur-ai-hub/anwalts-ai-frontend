"""
AnwaltsAI FastAPI Backend Server
Complete backend with PostgreSQL, Redis, and Together AI integration
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request, Response, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import os
from typing import Optional, List, Dict, Any, Tuple
import logging
from datetime import datetime, timedelta
import uuid
import hashlib
import re
import asyncio
import httpx
import json

from database import Database, get_database
from models import *
from ai_service import AIService
from cache_service import CacheService
from smtp_utils import send_email
from fastapi.responses import Response as FastAPIResponse
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse, StreamingResponse
import httpx
from auth_service import AuthService
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

# ===== Pydantic models for feedback/edit =====
from pydantic import BaseModel, Field
from typing import List as _List, Optional as _Optional

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

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def _hash_ip(ip: str) -> str:
    salt = _os.getenv("FEEDBACK_SALT", "anwaltsai-feedback-salt")
    return _sha256(salt + (ip or ""))

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
    
    cache_service = CacheService()
    await cache_service.connect()
    
    ai_service = AIService()
    auth_service = AuthService()
    
    logger.info("AnwaltsAI Backend started successfully")
    
    yield
    
    # Cleanup
    await db.disconnect()
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
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security
security = HTTPBearer()
# Admin guard middleware: block /api/admin/* unless role is admin
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
    return RedirectResponse(f"{prefix}/google/authorize")

@app.get("/auth/google")
async def google_auth(request: Request):
    """Redirect to Google OAuth authorize endpoint"""
    return await _google_entry_redirect(request)


@app.get("/auth/google/authorize")
async def google_authorize():
    try:
        import urllib.parse
        client_id, _, redirect_uri = _ensure_google_config()
        scope = urllib.parse.quote("openid email profile")
        state = uuid.uuid4().hex
        # PKCE (S256)
        code_verifier = _b64url_no_pad(secrets.token_bytes(32))
        code_challenge = _b64url_no_pad(hashlib.sha256(code_verifier.encode()).digest())
        try:
            await cache_service.redis_client.setex(f"oauth:pkce:{state}", 600, code_verifier)
        except Exception as e:
            logger.warning(f"PKCE store failed: {e}")
        base = "https://accounts.google.com/o/oauth2/v2/auth"
        url = (f"{base}?response_type=code&client_id={urllib.parse.quote(client_id)}"
               f"&redirect_uri={urllib.parse.quote(redirect_uri)}&scope={scope}&state={state}"
               f"&code_challenge={code_challenge}&code_challenge_method=S256"
               f"&access_type=offline&prompt=consent")
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url)
    except Exception as e:
        logger.error(f"Google authorize error: {e}")
        raise HTTPException(status_code=500, detail="Authorization init failed")

@app.get("/api/auth/google")
async def google_auth_api_alias(request: Request):
    return await _google_entry_redirect(request)

@app.get("/api/auth/google/authorize")
async def google_authorize_api_alias():
    return await google_authorize()

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
