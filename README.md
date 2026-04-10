# ChatApp

`ChatApp` is a simple realtime private chat template built with Django, Django Channels, WebSocket, PostgreSQL, Redis, and Docker.

This project is meant to be a clean starter for a realtime Django app:

- user signup and login
- private one-to-one chat rooms
- realtime message delivery with WebSocket
- REST API with JWT auth
- Docker setup for app, PostgreSQL, and Redis

## What Is Included

- Django app for auth, room management, and chat pages
- Django Channels for realtime messaging
- Redis channel layer for websocket message delivery
- PostgreSQL support for persistent data
- Swagger / ReDoc API docs
- basic tests for room access and message security

## Security Improvements Already Added

This template was cleaned up and fixed before this README was written.

- websocket connections now require authenticated users
- only room members can connect to a room
- sender spoofing is blocked on the server
- unsafe DOM rendering was removed from the frontend
- logout now uses `POST`
- duplicate private rooms are prevented
- Docker now runs ASGI correctly with `daphne`

## Tech Stack

- Python 3.12
- Django 5
- Django Channels
- Django REST Framework
- Simple JWT
- PostgreSQL
- Redis
- Docker Compose

## Quick Start With Docker

### 1. Copy environment file

```bash
cp .env.example .env
```

### 2. Update `.env`

Set real values for:

- `SECRET_KEY`
- `DATABASE_NAME`
- `DATABASE_USER`
- `DATABASE_PASSWORD`

Default service names in Docker are already set for:

- `DATABASE_HOST=db`
- `REDIS_URL=redis://redis:6379/0`
- `CACHE_URL=redis://redis:6379/10`

### 3. Build and run

```bash
docker compose up --build
```

The app will be available at:

- `http://localhost:8000`

Docker startup runs migrations automatically.

## Local Setup Without Docker

### 1. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Copy environment file

```bash
cp .env.example .env
```

### 4. Configure database and Redis

For full realtime behavior, set PostgreSQL and Redis values in `.env`.

If `DATABASE_NAME` is not set, the project falls back to SQLite for simple local development.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start the ASGI server

```bash
daphne -b 0.0.0.0 -p 8000 backend.asgi:application
```

Open:

- `http://127.0.0.1:8000`

## Main Routes

- `/accounts/signup/`
- `/accounts/login/`
- `/user_list/`
- `/swagger/`
- `/redoc/`
- `/api/v1/`

## API Overview

Main API endpoints:

- `POST /api/v1/auth/signup/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/token/refresh/`
- `GET /api/v1/users/`
- `POST /api/v1/rooms/create/<username>/`
- `GET /api/v1/rooms/<room_pk>/`
- `GET /api/v1/rooms/<room_pk>/messages/`
- `POST /api/v1/rooms/<room_pk>/messages/`

JWT is used for API authentication.

## Running Tests

```bash
python manage.py test
```

## Project Structure

```text
backend/         Django settings, ASGI, WSGI, root URLs
chat/            chat app, websocket consumer, API, models, tests
templates/       frontend templates
Dockerfile
docker-compose.yml
requirements.txt
```

## Notes

- This is a template project, not a finished production product.
- For production, set a strong `SECRET_KEY`, proper `ALLOWED_HOSTS`, and secure database credentials.
- `drf-yasg` currently works with the pinned `setuptools` version in `requirements.txt`.

## Next Ideas

- add message timestamps
- add online/offline presence
- add typing indicator
- add profile images
- add chat list with latest message preview
