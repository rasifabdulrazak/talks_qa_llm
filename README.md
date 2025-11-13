🤖 PDF Questionear
A production-ready FastAPI application for PDF document question-answering using Large Language Models (LLMs). Upload a PDF, ask questions, and get intelligent answers based on the document content.

✨ Features
===================
🔐 JWT Authentication - Secure user registration and login
📄 PDF Processing - Extract text from PDF documents
🤖 LLM Integration - Support for OpenAI GPT and Anthropic Claude
⚡ Smart Caching - Fast responses for repeated questions
🔄 Streaming Support - Real-time streaming responses
🐳 Docker Ready - Containerized deployment with Docker Compose
🗄️ PostgreSQL - Reliable database with Alembic migrations
📊 API Documentation - Auto-generated Swagger UI

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
Prerequisites

Docker & Docker Compose (recommended)
Python 3.11+ (for local development)
PostgreSQL 15+ (for local development)
OpenAI API Key for llm apis

Option 1: Docker Setup (Recommended) ⭐

1. Clone the Repository

```console
git clone https://github.com/yourusername/talks_qa_llm.git
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

