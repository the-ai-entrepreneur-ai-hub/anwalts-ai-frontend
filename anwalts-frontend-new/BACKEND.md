# Anwalts AI - Backend Documentation

This repository contains both frontend (Nuxt.js) and backend (FastAPI) components of the Anwalts AI legal document generation system.

## Backend Architecture

### Core Components

1. **`backend-main.py`** - Main FastAPI server with complete API endpoints
2. **`rag_llamacpp/`** - RAG (Retrieval Augmented Generation) system for legal document processing
3. **`backend/snippets/`** - Reusable backend utilities and middleware
4. **`requirements.txt`** - Python dependencies

### Key Features

- **AI Document Generation** - Legal document creation with Together AI integration
- **User Authentication** - JWT-based auth with PostgreSQL user management  
- **File Upload Processing** - Document upload and analysis capabilities
- **RAG Integration** - Legal knowledge retrieval for enhanced AI responses
- **Template System** - Pre-built legal document templates
- **RESTful API** - Complete API for frontend integration

### API Endpoints

The backend provides comprehensive endpoints for:
- `/ai/generate-document` - AI document generation
- `/ai/generate-document-simple` - Simplified generation endpoint
- `/auth/*` - Authentication and user management
- `/templates/*` - Document template management
- `/documents/*` - Document CRUD operations
- `/upload/*` - File upload handling

### Setup Requirements

#### Python Dependencies
```bash
pip install -r requirements.txt
```

#### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/anwalts_ai
REDIS_URL=redis://localhost:6379

# AI Services  
TOGETHER_API_KEY=your_together_ai_key
OPENAI_API_KEY=your_openai_key

# Authentication
JWT_SECRET_KEY=your_jwt_secret
```

#### Database Setup
The system uses PostgreSQL with automatic table creation and Redis for caching.

### Running the Backend

#### Development
```bash
python backend-main.py
```

#### Production
```bash
uvicorn backend-main:app --host 0.0.0.0 --port 8000
```

### RAG System

The `rag_llamacpp/` module provides:
- **Legal Document Retrieval** - Find relevant legal precedents and statutes
- **Context Enhancement** - Improve AI responses with legal knowledge
- **Semantic Search** - Vector-based legal document search
- **Evaluation Framework** - Quality assessment for generated content

### Integration with Frontend

The Nuxt.js frontend integrates with the backend through:
- **Proxy middleware** - `/api/auth/proxy` routes for seamless integration  
- **Authentication flow** - JWT token management
- **File upload handling** - Document processing pipeline
- **Real-time features** - WebSocket connections for live updates

### Security Features

- **JWT Authentication** - Secure token-based auth
- **Password Hashing** - bcrypt password protection
- **CORS Configuration** - Secure cross-origin requests  
- **Input Validation** - Comprehensive request validation
- **Rate Limiting** - API abuse prevention

### Deployment Notes

- Backend runs on port 8000 by default
- Frontend development server on port 3000/3001
- Production deployment requires reverse proxy (nginx)
- Database migrations handled automatically on startup