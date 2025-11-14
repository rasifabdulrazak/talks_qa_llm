# 🤖 PDF Questionear

- A production-ready FastAPI application for PDF document question-answering using Large Language Models (LLMs). Upload a PDF, ask questions, and get intelligent answers based on the document content.

✨ Features
===================
- 🔐 JWT Authentication - Secure user registration and login
- 📄 PDF Processing - Extract text from PDF documents
- 🤖 LLM Integration - Support for OpenAI GPT and Anthropic Claude
- ⚡ Smart Caching - Fast responses for repeated questions
- 🔄 Streaming Support - Real-time streaming responses
- 🐳 Docker Ready - Containerized deployment with Docker Compose
- 🗄️ PostgreSQL - Reliable database with Alembic migrations
- 📊 API Documentation - Auto-generated Swagger UI

🏗️ Architecture
===================
```bash
talks_qa_llm
├──alembic
│   ├──versions
│   │   └──417a23b64bf9_create_users_table.py
│   ├──env.py
│   ├──README
│   └──script.py.mako
├──app
│   ├──api
│   │   ├──__init__.py
│   │   ├──auth.py
│   │   ├──bot.py
│   │   └──deps.py
│   ├──core
│   │   ├──__init__.py
│   │   ├──config.py
│   │   ├──redis.py
│   │   ├──security.py
│   │   └──utils.py
│   ├──db
│   │   ├──__init__.py
│   │   ├──base.py
│   │   └──session.py
│   ├──models
│   │   ├──__init__.py
│   │   └──user.py
│   ├──schema
│   │   ├──__init__.py
│   │   ├──bot.py
│   │   └──user.py
│   ├──__init__.py
│   └──main.py
├──alembic.ini
├──docker-compose.yml
├──Dockerfile
├──README.md
├──requirements.txt
├──sample.env
├──.dockerignore
└──.gitignore
```


🚀 Quick Start
==================

Docker & Docker Compose (recommended)
Python 3.11+ (for local development)
PostgreSQL 15+ (for local development)
OpenAI API Key for llm apis

Option 1: Docker Setup (Recommended) ⭐

1. Clone the Repository

```console
git clone https://github.com/rasifabdulrazak/talks_qa_llm
cd talks_qa_llm
```

2. Create Environment File

```bash
cp sample.env

```
Edit .env with your configuration

4. Build and Start Services
```bash
# Build and start all services
docker-compose up --build -d

# Check logs
docker-compose logs -f app

# Check if services are running
docker-compose ps
```

5. Run Database Migrations
```bash
# Create initial migration
docker-compose exec app alembic revision --autogenerate -m "Initial migration"

# Apply migrations
docker-compose exec app alembic upgrade head
```

6. Access the API

- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/system-check


Option 2: Local Development Setup

1. Create Virtual Environment
```bash
python -m venv venv

# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

2. Install Dependencies
```bash
pip install -r requirements.txt
```

3. Install and Setup PostgreSQL URL in .env
```bash
DATABASE_URL=postgresql://your_username:your_password@your_host:your_port/db_name
```

4. Run Migrations
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

5. Start the Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

📖 API Usage
================
1. Register a New User
```bash
curl -X POST "http://localhost:8000/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "securepassword123"
  }'
```
Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-11-14T10:30:00",
  "updated_at": null
}
```
2. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d "email=user@example.com&password=securepassword123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

3. Ask a Question About a PDF
```bash
curl -X POST "http://localhost:8000/api/bot/ask/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "question=What is this document about?" \
```

Response:
```json
{
  "question": "What is this document about?",
  "answer": "This document is a Resume of mohammed Rasif ...",
  "pdf_filename": "document.pdf",
  "extracted_text_length": 15420,
  "processing_time": 2.35,
  "timestamp": "2024-11-14T10:35:00"
}
```

4. Return Stream data ,Ask a Question About a PDF Mainly for frontend apps and best User Experience
```bash
curl -X POST "http://localhost:8000/api/bot/ask-stream/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "question=What is this document about?" \
```

Response:
```bash
data: Moh

data: ammed

data:  Ras

data: if

data:  C

data:  has
etc....
```

5. Logout

```bash
curl -X POST "http://localhost:8000/api/auth/logout/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
```

Response:
```json
{
  "message": "Successfully logged out. Token has been blacklisted."
}
```