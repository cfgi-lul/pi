# FastAPI Backend

A simple FastAPI application for the Patent Management System.

## Setup

1. Activate the virtual environment:
```bash
cd backend
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Using FastAPI CLI (Recommended)

Start the development server with auto-reload:
```bash
fastapi dev src/main.py
```

### Alternative: Using Uvicorn directly

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive API docs (Swagger)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## Endpoints

- `GET /` - Root endpoint (returns "Hello World")

