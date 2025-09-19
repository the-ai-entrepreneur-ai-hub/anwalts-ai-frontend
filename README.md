# Anwalts AI - Rewired Version

This repository contains the **complete full-stack code** for the Anwalts AI legal document generation system, including both frontend and backend components.

## 🚀 Features

### Frontend (Nuxt.js)
- **Document generator** with AI assistance and guided tour
- **Email integration portal** with professional modals  
- **Professional dashboard** with navigation and metrics
- **Template management** system with pre-built legal documents
- **Authentication flow** with JWT integration

### Backend (FastAPI)
- **AI document generation** with Together AI and OpenAI integration
- **RAG system** for legal document retrieval and context enhancement
- **User authentication** with JWT and PostgreSQL
- **File upload processing** and document management
- **RESTful API** with comprehensive endpoints
- **Template system** for legal document generation

## 🏗️ Architecture

**Frontend**: Nuxt.js + Vue 3 + Tailwind CSS  
**Backend**: FastAPI + PostgreSQL + Redis  
**AI Integration**: Together AI + OpenAI + RAG system  
**Authentication**: JWT tokens + bcrypt  
**Deployment**: Nginx reverse proxy

## 📁 Structure

### Frontend
- `/pages` - Vue.js pages (dashboard, documents, email, etc.)
- `/components` - Reusable Vue components
- `/plugins` - Nuxt plugins for UI enhancements
- `/middleware` - Authentication and routing middleware
- `/composables` - Vue 3 composables (auth, tour system)

### Backend
- `backend-main.py` - Main FastAPI server
- `/backend` - Backend utilities and middleware
- `/rag_llamacpp` - RAG system for legal document processing
- `requirements.txt` - Python dependencies

## 🚦 Quick Start

### Frontend Development
```bash
npm install
npm run dev
```

### Backend Development  
```bash
pip install -r requirements.txt
python backend-main.py
```

For detailed backend setup and configuration, see [BACKEND.md](./BACKEND.md).

## 🔄 Auto-Sync

The code automatically syncs between the server and this repository:
- **Server → GitHub**: Every commit automatically pushes to GitHub
- **GitHub → Server**: Run `/root/sync-from-github.sh` to pull updates
