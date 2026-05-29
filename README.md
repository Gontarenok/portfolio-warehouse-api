# Warehouse Inventory API

REST API for warehouse stock accounting built with **FastAPI**, **SQLAlchemy 2.0 (async)**, **PostgreSQL**, and **JWT** authentication.

## Stack

- Python 3.11, FastAPI, Pydantic v2
- SQLAlchemy 2.0 + asyncpg
- Alembic migrations
- python-jose (JWT), passlib (bcrypt)
- pytest + httpx (tests use SQLite in-memory)
- Poetry for dependencies
- Docker Compose for local PostgreSQL

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

API: http://localhost:8000  
Swagger: http://localhost:8000/docs  
ReDoc: http://localhost:8000/redoc

Migrations run automatically on container start (`alembic upgrade head`).

## Local development (without Docker)

```bash
poetry install
cp .env.example .env
# Start PostgreSQL and set DATABASE_URL in .env
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

## Migrations

```bash
poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "description"
```

## Tests

```bash
poetry run pytest -v
```

Tests use an in-memory SQLite database with pytest fixtures (see `tests/conftest.py`).

## API flow (manual test)

1. `POST /auth/register` — create user (role `viewer`)
2. `POST /auth/login` — get JWT
3. Use `Authorization: Bearer <token>` for protected routes
4. `POST /api/suppliers/` — admin/manager
5. `POST /api/warehouses/` — **admin only**
6. `POST /api/products/` — admin/manager
7. `POST /api/movements/` with `"type": "in"` — updates stock
8. `GET /api/stock/?warehouse_id=1&product_id=1` — verify quantity

For admin/manager actions in development, promote a user in the database:

```sql
UPDATE users SET role = 'admin' WHERE email = 'you@example.com';
```

## Roles

| Role    | Permissions |
|---------|-------------|
| viewer  | Read stock, movements, suppliers, products, warehouses |
| manager | CRUD suppliers/products, create movements |
| admin   | All manager permissions + create warehouses |

## Deploy on Render

1. Push repository to GitHub.
2. Create **Blueprint** from `render.yaml` or add Web Service + PostgreSQL manually.
3. Set env vars (or use generated `JWT_SECRET` from blueprint).
4. Ensure `DATABASE_URL` uses async driver — the app auto-converts `postgres://` to `postgresql+asyncpg://`.

### Render PostgreSQL note

**Free PostgreSQL on Render is limited to 90 days for newly created databases** (Render policy). After expiration you must upgrade or migrate data to another database. Plan accordingly for production demos.

`render.yaml` defines:

- **Web service** (`warehouse-api`): Docker runtime, free plan, `autoDeploy: true`, health check `/health`
- **PostgreSQL** (`warehouse-db`): free plan
- Start command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Environment variables

See `.env.example`:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Async PostgreSQL URL (`postgresql+asyncpg://...`) |
| `JWT_SECRET` | Secret for signing tokens |
| `JWT_ALGORITHM` | Default `HS256` |
| `JWT_EXPIRE_MINUTES` | Token lifetime (default 60) |

## License

MIT
