# Backend API

FastAPI base repo. Starter template for building backend services.

---

## Features

- Auth: email/password, JWT, refresh tokens
- Admin: admin auth, user CRUD, bulk ops
- Users: profile, avatar, password management
- Common: response wrapping, request tracking, error standardization, timeouts, logging
- Versioning module

---

## Tech Stack

| Component       | Tech                    |
|-----------------|-------------------------|
| Framework       | FastAPI + Uvicorn       |
| ORM             | SQLAlchemy / SQLModel   |
| DB              | MySQL                   |
| Cache           | Redis                   |
| Object storage  | MinIO                   |
| Vector store    | Qdrant                  |
| Workers         | Celery                  |
| Auth            | JWT, argon2/bcrypt      |

---

## Project Structure

```
├── app
│   ├── constants/          # Messages, shared constants
│   ├── core/               # Config, OAuth utils, vault loader
│   ├── db/                 # Engine and session
│   ├── exception_handlers/ # HTTP + error middleware
│   ├── jobs/               # Celery worker and tasks
│   ├── models/             # SQLAlchemy models
│   ├── modules/            # Feature modules
│   │   ├── admin/
│   │   ├── common/
│   │   ├── users/
│   │   └── version/
│   └── scripts/
├── docs/openapi/           # OpenAPI 3.0.3 specs
├── templates/              # Coding/API standards
├── main.py
├── docker-compose.local.yml
├── Dockerfile
└── requirements.txt
```

Module layout: `crud/`, `routes/`, `schemas/`, `services/`, `utils/`.

---

## Getting Started

Requirements: Docker, Docker Compose.

```bash
cp .env.example .env
docker-compose -f docker-compose.local.yml up --build
```

Brings up: `api`, `redis`, `minio`, `qdrant`, `db`.

---

## API Documentation

| Module | Spec                                          |
|--------|-----------------------------------------------|
| Users  | [user-api.yaml](docs/openapi/user-api.yaml)   |
| Admin  | [admin-api.yaml](docs/openapi/admin-api.yaml) |

Error codes: [docs/openapi/error_codes.md](docs/openapi/error_codes.md).

---

## Standards

See `templates/`:

| #  | File                                                                            |
|----|---------------------------------------------------------------------------------|
| 01 | [Coding_Convention](templates/01_Coding_Convention.md)                          |
| 02 | [API_Naming_Convention](templates/02_API_Naming_Convention.md)                  |
| 03 | [API_Response_Guideline](templates/03_API_Response_Guideline.md)                |
| 04 | [Error_Code_Guideline](templates/04_Error_Code_Guideline.md)                    |
| 05 | [API_Timeout_Configuration](templates/05_API_Timeout_Configuration.md)          |
| 06 | [Readme template](templates/06_Readme.md)                                       |
| 07 | [TL_QA_review_checklist](templates/07_TL_QA_review_checklist.md)                |

---

## Testing

```bash
pytest
```

Config: `pytest.ini`.

---

## Commit Convention

Format: `<type>(scope): subject` per [.github/commit_guide.instructions.md](.github/commit_guide.instructions.md).
