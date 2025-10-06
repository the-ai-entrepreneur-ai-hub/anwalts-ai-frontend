from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# User models
class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    role: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserInDB(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    password_hash: str
    created_at: datetime

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str

class LoginResponse(BaseModel):
    token: str
    user: UserResponse

class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    created_at: datetime

class TemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    content: str
    category: str
    created_at: datetime
    updated_at: datetime

class ClauseResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    category: str
    created_at: datetime
    updated_at: datetime

class ClipboardResponse(BaseModel):
    id: uuid.UUID
    content: str
    created_at: datetime

class ClipboardCreate(BaseModel):
    content: str

class UserProfileUpdate(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    languages: Optional[List[str]] = None
    bio: Optional[str] = None

# Template models
class TemplateCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = None

class TemplateUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None

class Template(BaseModel):
    id: str
    title: str
    content: str
    category: Optional[str] = None
    created_at: datetime

# Clause models
class ClauseCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    language: Optional[str] = None

class Clause(BaseModel):
    id: str
    title: str
    content: str
    category: Optional[str] = None
    language: Optional[str] = None
    created_at: datetime

# Document models
class DocumentCreate(BaseModel):
    title: str
    content: str
    document_type: Optional[str] = None

class DocumentGenerateRequest(BaseModel):
    document_type: str
    title: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    model: Optional[str] = None
    template_id: Optional[str] = None
    template_content: Optional[str] = None

class Document(BaseModel):
    id: str
    title: str
    content: str
    document_type: Optional[str] = None
    created_at: datetime

class DocumentResponse(BaseModel):
    id: str
    title: str
    content: str
    document_type: Optional[str] = None
    created_at: datetime

# Clipboard models
class ClipboardEntryCreate(BaseModel):
    content: str
    entry_type: str = "text"

class ClipboardEntry(BaseModel):
    id: str
    content: str
    entry_type: str
    created_at: datetime

# AI Assistant models
class AssistantRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None

class AssistantResponse(BaseModel):
    content: str
    conversation_id: str
    message_id: str
    model: str
    usage: Optional[Dict[str, Any]] = None

# Generic AI request/response for /api/ai/complete
class AIRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7
    context: Optional[str] = None

class AIResponse(BaseModel):
    content: Optional[str] = None
    document: Optional[Dict[str, Any]] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    generation_time_ms: Optional[int] = None
    cost_estimate: Optional[float] = None
    prompt_used: Optional[str] = None

# Feedback models
class FeedbackRequest(BaseModel):
    conversation_id: Optional[str] = None
    message_id: str
    model: Optional[str] = None
    rating: int = Field(..., description="-1 or +1")
    reasons: Optional[List[str]] = None
    comment: Optional[str] = None
    client_ts: Optional[str] = None

class EditRequest(BaseModel):
    conversation_id: Optional[str] = None
    message_id: str
    edited_content: str
    allow_training: bool = False
    message_hash: Optional[str] = None

class AbuseRequest(BaseModel):
    message_id: str
    category: str
    note: Optional[str] = None

# API Token models
class APITokenCreate(BaseModel):
    name: Optional[str] = None
    expires_days: Optional[int] = 30

class APIToken(BaseModel):
    id: str
    last4: str
    expires_at: datetime
    created_at: datetime

# Call request models
class CallRequestCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    preferred_time: Optional[str] = None
    consultation_type: Optional[str] = None
    notes: Optional[str] = None

class CallRequest(BaseModel):
    id: str
    name: str
    phone: str
    email: Optional[str] = None
    status: Optional[str] = None
    preferred_time: Optional[str] = None
    consultation_type: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class CallRequestResponse(BaseModel):
    id: str
    name: str
    phone: str
    email: Optional[str] = None
    status: Optional[str] = None
    preferred_time: Optional[str] = None
    consultation_type: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Analytics models
class AnalyticsEvent(BaseModel):
    event_type: str
    data: Optional[Dict[str, Any]] = None

# OAuth models
class OAuthState(BaseModel):
    state: str
    redirect_uri: Optional[str] = None
    provider: str

# Settings models
class UserSettings(BaseModel):
    theme: Optional[str] = "light"
    language: Optional[str] = "de"
    notifications: Optional[bool] = True
    auto_save: Optional[bool] = True
    default_model: Optional[str] = None

# Response models
class SuccessResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[str] = None

# Health check models
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]

# File upload models
class FileUpload(BaseModel):
    filename: str
    content_type: str
    size: int
    content: str  # base64 encoded

# Search models
class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = 10
    offset: Optional[int] = 0

class SearchResult(BaseModel):
    id: str
    title: str
    content: str
    score: float
    type: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query: str
