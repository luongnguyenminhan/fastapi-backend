# SecureScribeBE

A FastAPI project with structured layout.

## Project Structure

```
├── app
│   ├── __init__.py
│   ├── constants
│   │   ├── __init__.py
│   │   └── messages.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── azure_oauth_utils.py
│   │   ├── config.py
│   │   └── vault_loader.py
│   ├── db
│   │   └── __init__.py
│   ├── events
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── domain_events.py
│   │   ├── listeners
│   │   │   ├── __init__.py
│   │   │   ├── notification_listener.py
│   │   │   └── websocket_listener.py
│   │   └── project_events.py
│   ├── exception_handlers
│   │   ├── __init__.py
│   │   └── http_exception.py
│   ├── jobs
│   │   ├── __init__.py
│   │   ├── celery_worker.py
│   │   ├── tasks
│   │   │   ├── __init__.py
│   │   │   ├── audio_tasks.py
│   │   │   ├── chat_tasks.py
│   │   │   ├── common.py
│   │   │   ├── file_tasks.py
│   │   │   ├── meeting_tasks.py
│   │   │   ├── notification_tasks.py
│   │   │   └── webhook_tasks.py
│   │   └── tasks.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── chat.py
│   │   ├── file.py
│   │   ├── meeting.py
│   │   ├── notification.py
│   │   ├── project.py
│   │   ├── tag.py
│   │   ├── task.py
│   │   └── user.py
│   └── modules
│       ├── __init__.py
│       ├── admin
│       │   ├── __init__.py
│       │   ├── crud
│       │   ├── routes
│       │   ├── schemas
│       │   ├── services
│       │   └── utils
│       ├── chat
│       │   ├── __init__.py
│       │   ├── crud
│       │   ├── routes
│       │   ├── schemas
│       │   ├── services
│       │   ├── tools
│       │   └── utils
│       ├── common
│       │   ├── __init__.py
│       │   ├── crud
│       │   ├── routes
│       │   ├── schemas
│       │   ├── services
│       │   └── utils
│       ├── file
│       │   ├── __init__.py
│       │   ├── crud
│       │   ├── routes
│       │   ├── schemas
│       │   └── services
│       ├── meeting_item
│       │   ├── __init__.py
│       │   ├── crud
│       │   ├── routes
│       │   ├── schemas
│       │   └── services
│       ├── meetings
│       │   ├── __init__.py
│       │   ├── crud
│       │   ├── routes
│       │   ├── schemas
│       │   ├── services
│       │   └── utils
│       ├── notification
│       │   ├── __init__.py
│       │   ├── crud
│       │   ├── routes
│       │   ├── schemas
│       │   └── services
│       ├── project
│       │   ├── __init__.py
│       │   ├── crud
│       │   ├── routes
│       │   ├── schemas
│       │   ├── services
│       │   └── utils
│       ├── transcripts
│       │   ├── __init__.py
│       │   ├── crud
│       │   ├── routes
│       │   ├── schemas
│       │   ├── services
│       │   └── utils
│       └── users
│           ├── __init__.py
│           ├── crud
│           ├── routes
│           ├── schemas
│           ├── services
│           └── utils
└── README.md

## Architecture

- `app/constants`: Shared constant values and message templates.
- `app/core`: Configuration and authentication helpers.
- `app/db`: Database engine/session setup.
- `app/events`: Domain events and listeners.
- `app/exception_handlers`: HTTP exception handlers.
- `app/jobs`: Celery worker and task definitions.
- `app/models`: SQLAlchemy data models.
- `app/modules`: Feature modules (admin/chat/common/file/meeting_item/meetings/notification/project/transcripts/users).
- `app/schemas`: Pydantic request/response schemas.
- `app/services`: Business logic and external integrations.
- `app/utils`: Utility helpers.

## Getting Started

### Local Development (Docker Compose)

Use `docker-compose.local.yml` to start both API and worker services in one command:

```bash
# Build and start all local dependencies + api + worker
docker-compose -f docker-compose.local.yml up --build
```

This will run:
- `api` service (FastAPI/Uvicorn)
- `redis`
- `minio`
- `qdrant`
- `db`
- any other local dependencies configured in `docker-compose.local.yml`

Do not run `start.sh` for local development in this setup; the container-compose workflow is the supported approach.

### Docker Development

```bash
# Start the API server
docker-compose up api

# Or start with database
docker-compose up api db
```

## API Documentation

Complete OpenAPI 3.0.3 specifications for all Meeting Agent API modules are available in the `docs/openapi/` directory:

### Core API Endpoints

| Module | Documentation | Description |
|--------|---------------|-------------|
| **Users** | [user-api.yaml](docs/openapi/user-api.yaml) | Authentication, user profiles, avatars, WebSocket status |
| **Meetings** | [meeting-api.yaml](docs/openapi/meeting-api.yaml) | Meeting CRUD, AI notes, agendas, bot integration, PDF export |
| **Transcripts & Audio** | [transcript-api.yaml](docs/openapi/transcript-api.yaml) | Audio processing, ASR transcription, semantic search, chunking |
| **Meeting Items & Tasks** | [meeting-item-api.yaml](docs/openapi/meeting-item-api.yaml) | Task management, assignment, status tracking, bulk operations |
| **Files** | [file-api.yaml](docs/openapi/file-api.yaml) | Document and audio file management, indexing, transcription |
| **Projects** | [project-api.yaml](docs/openapi/project-api.yaml) | Project management, RBAC, member management, role requests |
| **Chat & Conversations** | [chat-api.yaml](docs/openapi/chat-api.yaml) | Real-time messaging, AI assistance, entity mentions, SSE streaming |
| **Notifications** | [notification-api.yaml](docs/openapi/notification-api.yaml) | Notification delivery, WebSocket streaming, task updates |

### OpenAPI Standards

All API specifications follow the **OpenAPI 3.0.3** standard and can be:
- Imported into tools like Postman, Insomnia, or Swagger UI
- Used for API contract testing
- Integrated into documentation portals
- Referenced for client code generation

### Error Handling Reference

See [docs/error_codes.md](docs/error_codes.md) for comprehensive error handling documentation including:
- HTTP status codes and their meanings
- Error categorization and scenarios
- Frontend implementation examples
- Troubleshooting guides
