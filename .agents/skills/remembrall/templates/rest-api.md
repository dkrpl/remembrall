# Project Overview
- **Project:** [Service Name]
- **Core Stack:** Python, FastAPI, SQLAlchemy, PostgreSQL / Redis
- **Purpose:** Scalable RESTful microservice with automated OpenAPI docs and JWT auth

---

## Feature Manifest
| ID | Fitur | Status | File Terkait | Catatan |
|---|---|---|---|---|
| F-001 | Core Engine & Config | DONE | app/main.py, app/core/config.py | FastAPI app lifecycle & settings |
| F-002 | Database Connection Pool | DONE | app/db/session.py, alembic/ | SQLAlchemy async engine |

---

## Technical Findings
- All request/response contracts enforced via Pydantic v2 models.
- Database migrations handled strictly via Alembic (`alembic upgrade head`).
