# Hospital Management System — Story 1: Specialty Catalog Service

## Overview

A production-ready REST API built with **FastAPI** that provides a specialty catalog for the Hospital Management System.

**Epic:** Core Medical Specialties & Clinical Credentials
**Story:** Story 1 — Create and Retrieve Hospital Specialty Catalog

---

## Tech Stack

| Technology | Version | Role |
|---|---|---|
| Python | 3.11+ | Runtime |
| FastAPI | 0.115.6 | Web framework |
| Uvicorn | 0.34.0 | ASGI server |
| SQLAlchemy | 2.0.37 | ORM / database layer |
| Pydantic | 2.10.6 | Data validation |
| SQLite | built-in | Database (development) |

---

## Project Structure

```
Hospital_Project_Story1_PS/
├── app/
│   ├── __init__.py          # Package marker
│   ├── main.py              # FastAPI app entry point, router mounting, CORS
│   ├── database.py          # SQLAlchemy engine, session, Base
│   ├── models.py            # ORM model: Specialty table
│   ├── schemas.py           # Pydantic schemas: SpecialtyCreate, SpecialtyResponse
│   ├── crud.py              # Database operations: create, get, list
│   └── routers/
│       ├── __init__.py      # Package marker
│       └── specialties.py   # HTTP endpoints: POST, GET /specialties
├── Diagrams/                # Architecture diagrams (Mermaid)
├── tests/
│   ├── __init__.py          # Package marker
│   └── test_specialties.py  # pytest integration tests
├── requirements.txt         # Pinned dependencies
├── .env                     # Environment variables (not committed to git)
├── .gitignore
└── README.md
```

---

## Quick Start

### 1. Clone / Enter the project directory
```powershell
cd C:\Users\ASUS\Desktop\Hospital_Project_Story1_PS
```

### 2. Create and activate virtual environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run the development server
```powershell
uvicorn app.main:app --reload
```

### 5. Open the interactive API docs
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:**       [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Endpoints

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `GET` | `/` | Health check | 200 |
| `POST` | `/api/v1/specialties/` | Create a new specialty | 201 |
| `GET` | `/api/v1/specialties/` | List all specialties | 200 |
| `GET` | `/api/v1/specialties/{id}` | Get specialty by ID | 200 / 404 |

### POST /api/v1/specialties/ — Request Body
```json
{
  "name": "Cardiology",
  "description": "Diagnosis and treatment of heart diseases"
}
```

### POST /api/v1/specialties/ — Response (201 Created)
```json
{
  "id": 1,
  "name": "Cardiology",
  "description": "Diagnosis and treatment of heart diseases",
  "created_at": "2026-02-21T15:00:00Z"
}
```

---

## Error Responses

| Status | When |
|---|---|
| `409 Conflict` | Specialty with the same name already exists |
| `422 Unprocessable Entity` | Request body validation failure (e.g., missing `name`) |
| `404 Not Found` | No specialty with the given ID |

---

## Running Tests

```powershell
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app
```

---

## Environment Variables

See `.env` for all configuration variables:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./hospital.db` | Database connection string |
| `APP_NAME` | `Hospital Management API` | Displayed in Swagger UI |
| `APP_VERSION` | `1.0.0` | API version |
| `DEBUG` | `True` | Enable detailed error responses |
| `API_V1_PREFIX` | `/api/v1` | URL prefix for all routes |
| `ALLOWED_ORIGINS` | `http://localhost:3000,...` | CORS allowed origins |

---

## Architecture

The service follows a **layered architecture**:

```
HTTP Request
    ↓
routers/specialties.py   ← HTTP layer (routes, status codes)
    ↓
crud.py                  ← Data access layer (SQL queries)
    ↓
models.py                ← ORM layer (table definition)
    ↓
database.py              ← Infrastructure (engine, session)
    ↓
SQLite (hospital.db)
```

See `/Diagrams/` for full Mermaid architecture diagrams.

