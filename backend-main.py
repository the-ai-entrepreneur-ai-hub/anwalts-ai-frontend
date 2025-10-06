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
        raise HTTPException(status_code=500, detail="Authorization init failed")


# ============ OAUTH CALLBACKS ============

async def _redirect(path: str) -> RedirectResponse:
    return RedirectResponse(url=path, status_code=302)

@app.get("/auth/google/callback")
async def google_callback(code: Optional[str] = None, state: Optional[str] = None):
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    try:
        token_url = "https://oauth2.googleapis.com/token"
        client_id, client_secret, redirect_uri = _ensure_google_config(require_secret=True)
        # Pull verifier by state
        code_verifier = None
        try:
            if state:
                code_verifier = await cache_service.redis_client.get(f"oauth:pkce:{state}")
        except Exception as e:
            logger.warning(f"PKCE load failed: {e}")
        async with httpx.AsyncClient(timeout=10) as client:
            token_res = await client.post(token_url, data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                **({"code_verifier": code_verifier} if code_verifier else {}),
            }, headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"})
            token_res.raise_for_status()
            tokens = token_res.json()
            id_token = tokens.get("id_token")
            access_token = tokens.get("access_token")

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

        # Determine role by email allowlist/domain
        admin_domains = (os.getenv("ADMIN_EMAIL_DOMAINS", "").strip() or "").split(",")
        admin_emails = set((os.getenv("ADMIN_EMAILS", "").strip() or "").lower().split(","))
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

        # Create simple JWT token session
        token = auth_service.create_access_token(data={"sub": str(user.id), "email": email, "name": name, "role": user.role})
        session_id = str(uuid.uuid4())
        await cache_service.store_session(session_id, str(user.id), expires_in=86400)
        
        # Simple redirect with token in localStorage
        html = (
            "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>Signing in…</title></head><body>"
            "<script>"
            "try {"
            "  localStorage.setItem('auth_token', %s);"
            "  localStorage.setItem('user_id', %s);"
            "  localStorage.setItem('user_email', %s);"
            "  localStorage.setItem('user_name', %s);"
            "  localStorage.setItem('user_role', %s);"
            "  console.log('Auth data stored successfully');"
            "} catch (e) { console.error('Storage error:', e); }"
            "window.location.replace('/dashboard');"
            "</script>"
            "Signing in…</body></html>"
        ) % (
            repr(token),
            repr(str(user.id)),
            repr(email),
            repr(name),
            repr(user.role)
        )
        response = HTMLResponse(content=html, status_code=200)
        
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
        
        logger.info(f"OAuth login successful for: {email}")
        return response
    except httpx.HTTPError as e:
        try:
            detail = e.response.text
        except Exception:
            detail = str(e)
        logger.error(f"Google callback HTTP error: {e} | {detail}")
        raise HTTPException(status_code=502, detail="OAuth exchange failed")
    except Exception as e:
        logger.error(f"Google callback error: {e}")
        raise HTTPException(status_code=500, detail="Callback failed")


@app.get("/api/auth/google/callback")
async def google_callback_api_alias(code: Optional[str] = None, state: Optional[str] = None):
    return await google_callback(code=code, state=state)

@app.get("/auth/oauth/google/callback")
async def google_callback_legacy_auth(code: Optional[str] = None, state: Optional[str] = None):
    return await google_callback(code=code, state=state)

@app.get("/api/auth/oauth/google/callback")
async def google_callback_api_legacy_auth(code: Optional[str] = None, state: Optional[str] = None):
    return await google_callback(code=code, state=state)

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
async def login(request: dict):
    """Authenticate user and return JWT token"""
    try:
        # Extract email and password from request
        email = request.get("email")
        password = request.get("password")
        
        if not email or not password:
            return {"error": "Email and password are required", "status": 400}
        
        logger.info(f"Login attempt for email: {email}")
        
        # Get user from database
        user = await db.get_user_by_email(email)
        if not user:
            logger.warning(f"User not found: {email}")
            return {"error": "Invalid email or password", "status": 401}
        
        # Verify password
        if not auth_service.verify_password(password, user.password_hash):
            logger.warning(f"Invalid password for user: {email}")
            return {"error": "Invalid email or password", "status": 401}
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Inactive user login attempt: {email}")
            return {"error": "Account is disabled", "status": 401}
        
        # Create JWT token
        token = auth_service.create_access_token(data={"sub": str(user.id)})
        logger.info(f"JWT token created for user: {user.id}")
        
        # Store session
        session_id = str(uuid.uuid4())
        await cache_service.store_session(session_id, str(user.id), expires_in=86400)
        logger.info(f"Session stored for user: {user.id}")
        
        # Return successful response (include success flag for legacy clients)
        payload = {
            "success": True,
            "token": token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role
            },
            "status": 200
        }
        response = JSONResponse(content=payload)
        _set_auth_cookies(response, token)
        return response
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {"error": f"Login failed: {str(e)}", "status": 500}

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
async def get_user_profile(current_user: UserInDB = Depends(get_current_user)):
    profile = await db.get_user_profile(current_user.id)
    if not profile:
        return UserProfileResponse(user_id=current_user.id)
    return profile

@app.post("/api/user/profile", response_model=UserProfileResponse)
async def upsert_user_profile(profile_data: UserProfileUpdate, current_user: UserInDB = Depends(get_current_user)):
    return await db.upsert_user_profile(current_user.id, profile_data)

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(request: Request, response: Response):
    """Get current user information with cookie or Authorization fallback."""
    # Prefer Authorization header; fallback to sid cookie set during OAuth
    token = None
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
    if not token:
        token = request.cookies.get(os.getenv("SESSION_COOKIE_NAME", "sid"))
    if not token:
        # Fallback to non-HttpOnly public session cookie
        token = request.cookies.get(os.getenv("PUBLIC_SESSION_COOKIE", "sat"))
    logger.info(
        "[auth_me] has_auth_header=%s has_sid_cookie=%s has_sat_cookie=%s",
        bool(auth_header),
        bool(request.cookies.get(os.getenv("SESSION_COOKIE_NAME", "sid"))),
        bool(request.cookies.get(os.getenv("PUBLIC_SESSION_COOKIE", "sat"))),
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

# Lightweight guard endpoint for client-side check
@app.get("/auth/validate")
async def validate_token(current_user: UserInDB = Depends(get_current_user)):
    return {"valid": True, "user": {"id": str(current_user.id), "email": current_user.email, "name": current_user.name, "role": current_user.role}}

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

        # Best-effort delete without domain (host-only), in case attributes differ
        try:
            response.delete_cookie(key=session_cookie, path="/")
            response.delete_cookie(key=public_cookie, path="/")
        except Exception:
            pass

        return {"success": True}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"success": False}

@app.get("/api/templates", response_model=List[TemplateResponse])
async def get_templates(
    category: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get user templates with optional category filter"""
    try:
        templates = await db.get_templates(current_user.id, category)
        return [
            TemplateResponse(
                id=t.id,
                name=t.name,
                content=t.content,
                category=t.category,
                type=t.type,
                usage_count=t.usage_count,
                created_at=t.created_at,
                updated_at=t.updated_at
            ) for t in templates
        ]
    except Exception as e:
        logger.error(f"Get templates error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve templates"
        )

@app.post("/api/templates", response_model=TemplateResponse)
async def create_template(
    template_data: TemplateCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Create new template"""
    try:
        template = await db.create_template(
            user_id=current_user.id,
            name=template_data.name,
            content=template_data.content,
            category=template_data.category,
            type=template_data.type
        )
        
        return TemplateResponse(
            id=template.id,
            name=template.name,
            content=template.content,
            category=template.category,
            type=template.type,
            usage_count=template.usage_count,
            created_at=template.created_at,
            updated_at=template.updated_at
        )
    except Exception as e:
        logger.error(f"Create template error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create template"
        )

@app.put("/api/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: uuid.UUID,
    template_data: TemplateUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update existing template"""
    try:
        template = await db.update_template(
            template_id=template_id,
            user_id=current_user.id,
            **template_data.dict(exclude_unset=True)
        )
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return TemplateResponse(
            id=template.id,
            name=template.name,
            content=template.content,
            category=template.category,
            type=template.type,
            usage_count=template.usage_count,
            created_at=template.created_at,
            updated_at=template.updated_at
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
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete template"""
    try:
        success = await db.delete_template(template_id, current_user.id)
        if not success:
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
    current_user: UserInDB = Depends(get_current_user)
):
    """Get user clauses with optional filters"""
    try:
        clauses = await db.get_clauses(current_user.id, category, language)
        return [
            ClauseResponse(
                id=c.id,
                category=c.category,
                title=c.title,
                content=c.content,
                tags=c.tags,
                language=c.language,
                is_favorite=c.is_favorite,
                usage_count=c.usage_count,
                created_at=c.created_at,
                updated_at=c.updated_at
            ) for c in clauses
        ]
    except Exception as e:
        logger.error(f"Get clauses error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve clauses"
        )

@app.post("/api/clauses", response_model=ClauseResponse)
async def create_clause(
    clause_data: ClauseCreate,
    current_user: UserInDB = Depends(get_current_user)
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
            id=clause.id,
            category=clause.category,
            title=clause.title,
            content=clause.content,
            tags=clause.tags,
            language=clause.language,
            is_favorite=clause.is_favorite,
            usage_count=clause.usage_count,
            created_at=clause.created_at,
            updated_at=clause.updated_at
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
            source_type=entry_data.source_type,
            metadata=entry_data.metadata,
            expires_at=entry_data.expires_at
        )
        
        return ClipboardResponse(
            id=entry.id,
            content=entry.content,
            source_type=entry.source_type,
            metadata=entry.metadata,
            created_at=entry.created_at
        )
    except Exception as e:
        logger.error(f"Add clipboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add clipboard entry"
        )

# ============ AI ENDPOINTS ============

@app.post("/api/ai/complete", response_model=AIResponse)
async def ai_complete(
    request_data: AIRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """Generate AI completion using Together API with Redis caching."""
    try:
        # Build deterministic cache key using user + params
        ptxt = (request_data.prompt or "").strip()
        ctxt = (request_data.context or "").strip()
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
                event_data={
                    "model": model,
                    "tokens_used": getattr(response, "tokens_used", None),
                    "cost_estimate": getattr(response, "cost_estimate", None),
                },
            )
        except Exception as te:
            logger.warning(f"Analytics event failed: {te}")

        # Store in cache (TTL 1 day)
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
@app.get("/api/rag/test")
async def rag_test(query: str = "§ 823 BGB"):
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
    current_user: UserInDB = Depends(get_current_user)
):
    """Generate legal document using AI"""
    try:
        # IMPORTANT: Disable cache for this endpoint to avoid stale/previous docs being reused
        # Caching remains enabled for the "generate-document-simple" endpoint only.

        # No cache hit: generate document content
        # Ignore template_content to avoid leaking templates into output
        ai_response = await ai_service.generate_document(
            document_type=request_data.document_type,
            template_content="",
            variables=request_data.variables,
            model=request_data.model
        )
        
        # Save document
        document = await db.create_document(
            user_id=current_user.id,
            title=request_data.title,
            content=ai_response.content,
            document_type=request_data.document_type,
            template_id=request_data.template_id,
            ai_model=request_data.model,
            ai_prompt=ai_response.prompt_used,
            generation_time_ms=ai_response.generation_time_ms,
            tokens_used=ai_response.tokens_used,
            cost_estimate=ai_response.cost_estimate
        )
        
        resp = DocumentResponse(
            id=document.id,
            title=document.title,
            content=document.content,
            document_type=document.document_type,
            created_at=document.created_at
        )

        # Store in cache (best-effort)
        try:
            payload = {
                "content": ai_response.content,
                "tokens_used": ai_response.tokens_used,
                "model_used": ai_response.model_used,
                "generation_time_ms": ai_response.generation_time_ms,
                "cost_estimate": ai_response.cost_estimate,
            }
            await cache_service.cache_ai_response(prompt_hash, payload, ttl=3600)
        except Exception as _se:
            logger.warning(f"docgen cache set failed: {_se}")

        return resp
    except Exception as e:
        logger.error(f"Document generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document generation failed"
        )

# ============ FILE UPLOAD ENDPOINTS ============

@app.get("/api/files")
async def list_files(current_user: UserInDB = Depends(get_current_user)):
    if not upload_processor:
        raise HTTPException(status_code=500, detail="Upload subsystem not available")
    try:
        items = upload_processor.list_user_files(str(current_user.id))
        return {"files": items}
    except Exception as e:
        logger.error(f"List files error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list files")


@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...), current_user: UserInDB = Depends(get_current_user)):
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
async def get_file_content_endpoint(file_id: str, current_user: UserInDB = Depends(get_current_user)):
    if not upload_processor:
        raise HTTPException(status_code=500, detail="Upload subsystem not available")
    content = upload_processor.get_file_content(file_id)
    if content is None:
        raise HTTPException(status_code=404, detail="File not found")
    return {"success": True, "file_id": file_id, "content": content}


@app.get("/api/files/{file_id}/metadata")
async def get_file_metadata_endpoint(file_id: str, current_user: UserInDB = Depends(get_current_user)):
    if not upload_processor:
        raise HTTPException(status_code=500, detail="Upload subsystem not available")
    meta = upload_processor.get_file_metadata(file_id)
    if not meta or str(meta.get("user_id")) != str(current_user.id):
        raise HTTPException(status_code=404, detail="File not found")
    return meta


@app.delete("/api/files/{file_id}")
async def delete_file_endpoint(file_id: str, current_user: UserInDB = Depends(get_current_user)):
    if not upload_processor:
        raise HTTPException(status_code=500, detail="Upload subsystem not available")
    ok = upload_processor.delete_file(file_id)
    if not ok:
        raise HTTPException(status_code=404, detail="File not found")
    return {"success": True}


@app.post("/api/files/{file_id}/process")
async def process_file_endpoint(file_id: str, current_user: UserInDB = Depends(get_current_user)):
    if not upload_processor:
        raise HTTPException(status_code=500, detail="Upload subsystem not available")
    try:
        result = await upload_processor.process_existing(file_id, db=db)
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"Process file error: {e}")
        raise HTTPException(status_code=500, detail="Processing failed")


# ============ DOCUMENT SAVE/EXPORT/STATUS ENDPOINTS ============

@app.post("/api/documents/save")
async def save_document_endpoint(payload: dict, current_user: UserInDB = Depends(get_current_user)):
    try:
        title = (payload.get("title") or "Unbenanntes Dokument").strip()
        content = payload.get("content") or payload.get("html") or ""
        doc_type = payload.get("document_type") or "custom"
        template_id = payload.get("template_id")

        document = await db.create_document(
            user_id=current_user.id,
            title=title,
            content=content,
            document_type=doc_type,
            template_id=template_id,
            ai_model=payload.get("ai_model"),
            ai_prompt=payload.get("ai_prompt"),
            generation_time_ms=payload.get("generation_time_ms"),
            tokens_used=payload.get("tokens_used"),
            cost_estimate=payload.get("cost_estimate"),
        )
        return {"success": True, "id": document.id, "documentId": document.id, "document": {"id": document.id, "title": document.title, "content": document.content, "document_type": document.document_type, "created_at": document.created_at}}
    except Exception as e:
        logger.error(f"Save document error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save document")


@app.get("/api/documents/{doc_id}/export")
async def export_document_endpoint(doc_id: str, format: str = "docx", current_user: UserInDB = Depends(get_current_user)):
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
async def update_document_status_endpoint(doc_id: str, payload: dict, current_user: UserInDB = Depends(get_current_user)):
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
async def update_document_status_noid_endpoint(payload: dict, current_user: UserInDB = Depends(get_current_user)):
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
            raise HTTPException(status_code=400, detail="Gültige E-Mail-Adresse erforderlich")

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
            body_text=f"Ihr Einmal-Code lautet: {otp}. Er ist 10 Minuten gültig."
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
            raise HTTPException(status_code=400, detail="Ungültiger Code")

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
            raise HTTPException(status_code=500, detail="Änderung fehlgeschlagen")

        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"change-password error: {e}")
        raise HTTPException(status_code=500, detail="Änderung fehlgeschlagen")

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
async def generate_document_working(request: dict):
    """Real AI-powered document generation using DeepSeek-V3"""
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
        # Ignore raw template content to prevent leaking templates into results
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
        
        logger.info(f"🤖 Generating document with AI: {title} ({doc_type})")
        
        # Build rich prompt including instructions, OCR text and optional template
        # Limit very long OCR text to keep context manageable
        ocr_excerpt = (extracted_text or "").strip()
        if len(ocr_excerpt) > 12000:
            ocr_excerpt = ocr_excerpt[:12000] + "\n[…]"

        tone_hint = {
            "legal": "Juristisch präzise Formulierung.",
            "plain": "Leicht verständliche Formulierung.",
            "legal+plain": "Juristisch präzise – zugleich gut lesbar.",
            "neutral": "Neutraler Stil."
        }.get(tone, "Neutraler Stil.")

        vars_block = "".join([f"- {k}: {v}\n" for k, v in (variables or {}).items()]) if variables else ""

        ai_prompt = f"""
[task:document][format:json]
Erstellen Sie ein vollständiges deutsches Rechtsdokument.

TITEL: {title}
DOKUMENTTYP: {doc_type}
STIL: {tone_hint}

NUTZERANGABEN:
{user_instructions or '(keine zusätzlichen Angaben)'}

EINGELESENER TEXT (aus Upload, ggf. OCR-bereinigt):
{(ocr_excerpt or '(kein Uploadtext)')}

VARIABLEN:
{(vars_block or '(keine)')}

ANFORDERUNGEN:
1. Verwenden Sie korrektes deutsches Recht und Rechtssprache; keine Platzhalter-Fragen.
2. Strukturieren Sie logisch (Überschriften, Abschnitte, ggf. Paragraphen) und formulieren Sie verbindlich.
3. Verfassen Sie den Text NEU; keine unveränderten Passagen aus Beispielen/Vorlagen übernehmen.
4. Fügen Sie übliche, passende Klauseln hinzu; keine sensiblen Daten re‑exponieren.
5. Erstellen Sie ein anwendungsbereites, kohärentes Dokument ohne Rückfragen.

AUSGABEFORMAT:
- JSON ONLY, ohne Prä-/Nachtext, in folgendem Schema: {json.dumps(ai_service.document_json_schema, ensure_ascii=False)}
""".strip()

        start_time = time.time()

        # Cache check
        try:
            prompt_hash = cache_service.hash_prompt(
                ai_prompt,
                preferred_model or (os.getenv("LOCAL_AI_MODEL") or ai_service.local_default_model),
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
            return {
                "success": True,
                "document": {
                    "id": f"doc_{uuid.uuid4().hex[:8]}",
                    "title": title,
                    "content": safe_cached,
                    "document_type": doc_type,
                    "created_at": datetime.utcnow().isoformat(),
                    "tokens_used": int(cached.get("tokens_used") or 0),
                    "model_used": cached.get("model_used") or preferred_model,
                    "generation_time_ms": generation_time,
                    "processing_time": generation_time / 1000,
                    "confidence": 0.95,
                    "cost_estimate": float(cached.get("cost_estimate") or 0.0),
                },
            }
        
        # Call AI service (prefer model from request, fallback to LOCAL_AI_MODEL)
        from os import getenv as _getenv
        if not preferred_model:
            preferred_model = _getenv("LOCAL_AI_MODEL") or None
        ai_response = await ai_service.generate_completion(
            prompt=ai_prompt,
            model=preferred_model,
            max_tokens=getattr(ai_service, "llm_max_tokens_default", 900),
            temperature=0.2
        )
        
        generation_time = int((time.time() - start_time) * 1000)
        
        logger.info(f"✅ AI generation completed in {generation_time}ms")

        # Write to cache (best-effort)
        try:
            await cache_service.cache_ai_response(prompt_hash, {
                "content": ai_response.content,
                "tokens_used": ai_response.tokens_used,
                "model_used": ai_response.model_used,
                "generation_time_ms": generation_time,
                "cost_estimate": ai_response.cost_estimate,
            }, ttl=3600)
        except Exception as _se:
            logger.warning(f"simple docgen cache set failed: {_se}")
        
        # Try structured rendering to HTML; fallback to sanitized text
        try:
            rendered_html = ai_service.format_document_json(ai_response.content)
        except Exception:
            rendered_html = None
        safe_content = rendered_html if rendered_html else ai_service._normalize_document_output(ai_response.content)

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
                "cost_estimate": ai_response.cost_estimate
            }
        }
        
    except Exception as e:
        logger.error(f"❌ AI document generation error: {e}")
        return {"success": False, "error": f"AI generation failed: {str(e)}"}

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
- ✅ Backend-Verbindung
- ✅ Dokumentenerstellung  
- ✅ Deutsche Rechtsinhalte

### Rechtlicher Hinweis

Dieses Dokument dient nur zu Testzwecken.

---
*AnwaltsAI - Ihr KI-Partner für deutsche Rechtsdokumente*"""

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
                "message": "Neue E-Mail von Mandant Müller eingetroffen.",
                "type": "info",
                "timestamp": datetime.utcnow() - timedelta(minutes=15),
                "read": False,
                "icon": "mail"
            },
            {
                "id": 3,
                "title": "Template gespeichert",
                "message": "Neue Vorlage \"Mietvertrag\" wurde hinzugefügt.",
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
                detail=f"Ungültige Einstellungsschlüssel: {invalid_keys}"
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

@app.put("/api/user/profile")
async def update_user_profile(
    profile_data: dict,
    user_id: str = Depends(get_current_user_id)
):
    """Update user profile information"""
    try:
        # In real implementation, validate and update user profile
        logger.info(f"Updating profile for user {user_id}: {profile_data}")
        
        # Validate required fields
        if 'name' in profile_data and not profile_data['name'].strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name darf nicht leer sein"
            )
        
        if 'email' in profile_data:
            email = profile_data['email'].strip()
            if not email or '@' not in email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Gültige E-Mail-Adresse erforderlich"
                )
        
        # In real implementation: await db.update_user_profile(user_id, profile_data)
        
        return {
            "success": True,
            "message": "Profil erfolgreich aktualisiert",
            "profile": profile_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fehler beim Aktualisieren des Profils"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        await db.health_check()
        
        # Check cache connection
        await cache_service.health_check()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "healthy",
                "cache": "healthy",
                "ai_service": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
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
        return {"tokens": tokens}
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

        rec = await db.create_api_token(current_user.id, token, expires_at, last4)
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
