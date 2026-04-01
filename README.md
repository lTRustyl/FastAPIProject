# FastAPI Project

A RESTful API built with FastAPI, SQLAlchemy, and PostgreSQL. Supports JWT authentication, role-based access control, and full CRUD for users and articles.

---

## Tech Stack

- **Python 3.10**
- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **PostgreSQL 15** — database
- **Docker & Docker Compose** — containerization
- **JWT** — authentication
- **bcrypt** — password hashing
- **pytest + pytest-cov** — testing

---

## Project Structure

```
FastAPIProject/
├── app/
│   ├── controllers/     # HTTP layer — routes only
│   ├── services/        # Business logic
│   ├── repositories/    # Database operations
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic schemas
│   ├── core/            # Config, security, dependencies
│   └── main.py
├── scripts/
│   ├── seed.py          # Populate DB with sample data
│   ├── create_user.py   # Interactive user creation
│   └── init.sql         # SQL for seeding
├── tests/               # pytest test suite
├── manage.py            # CLI entrypoint
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

No other dependencies required — everything runs inside Docker.

---

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd FastAPIProject
```

### 2. Build and start containers

```bash
docker compose up --build
```

The API will be available at **http://localhost:8000**

Interactive API docs (Swagger UI): **http://localhost:8000/docs**

### 3. Stop the application

```bash
docker compose down
```

To also remove the database volume (full reset):

```bash
docker compose down -v
```

---

## Environment Variables

| Variable            | Description              | Default      |
|---------------------|--------------------------|--------------|
| `POSTGRES_HOST`     | Database host            | `db`         |
| `POSTGRES_DB`       | Database name            | `mydb`       |
| `POSTGRES_USER`     | Database user            | `user`       |
| `POSTGRES_PASSWORD` | Database password        | `password`   |
| `SECRET_KEY`        | JWT signing secret       | `changeme`   |

> **Important:** Change `SECRET_KEY` before deploying to production.

---

## Loading Initial Data

Populate the database with sample users and articles:

```bash
docker compose exec web python manage.py seed
```

This creates the following accounts:

| Username      | Password    | Role          |
|---------------|-------------|---------------|
| `admin`       | `admin123`  | Administrator |
| `editor_one`  | `editor123` | Editor        |
| `editor_two`  | `editor123` | Editor        |
| `user_one`    | `user123`   | User          |
| `user_two`    | `user123`   | User          |
| `user_three`  | `user123`   | User          |

The seed script is idempotent — running it multiple times will not create duplicates.

### SQL script

```bash
docker compose exec db psql -U user -d mydb -f /app/scripts/init.sql
```

### Create a single user interactively

```bash
docker compose exec web python manage.py create_user
```

---

## Authentication

The API uses JWT Bearer tokens. To authenticate:

1. Open **http://localhost:8000/docs**
2. Call `POST /auth/login` with your credentials
3. Copy the `access_token` from the response
4. Click **Authorize** (lock icon) and paste the token

Or use curl:

```bash
curl -X POST http://localhost:8000/auth/login \
  -d "username=admin&password=admin123"
```

---

## API Overview

### Auth
| Method | Endpoint      | Auth required |
|--------|---------------|---------------|
| POST   | `/auth/login` | No            |

### Users
| Method | Endpoint                  | Auth required        |
|--------|---------------------------|----------------------|
| GET    | `/users`                  | Any                  |
| GET    | `/users/{id}`             | Any                  |
| GET    | `/users/search?q=`        | Any                  |
| GET    | `/users/{id}/permissions` | Any                  |
| PUT    | `/users/{id}`             | Own user or Admin    |
| DELETE | `/users/{id}`             | Administrator        |
| PUT    | `/users/{id}/roles`       | Administrator        |

### Articles
| Method | Endpoint                   | Auth required               |
|--------|----------------------------|-----------------------------|
| GET    | `/articles`                | Any                         |
| GET    | `/articles/{id}`           | Any                         |
| GET    | `/articles/search?q=`      | Any                         |
| GET    | `/articles/user/{user_id}` | Any                         |
| POST   | `/articles`                | Any (own user only)         |
| PUT    | `/articles/{id}`           | Own article or Editor/Admin |
| DELETE | `/articles/{id}`           | Own article or Admin        |

### Roles & Health
| Method | Endpoint  | Auth required |
|--------|-----------|---------------|
| GET    | `/roles`  | Any           |
| GET    | `/health` | No            |

#### Pagination & filtering (all list endpoints)

| Parameter | Default | Description                                       |
|-----------|---------|---------------------------------------------------|
| `limit`   | 10      | Number of results (1–100)                         |
| `offset`  | 0       | Number of results to skip                         |
| `status`  | —       | Articles only: `true`=published, `false`=draft    |

---

## Role Permissions

| Action                      | User | Editor | Administrator |
|-----------------------------|------|--------|---------------|
| View any articles/users     | ✅   | ✅     | ✅            |
| Create own articles         | ✅   | ✅     | ✅            |
| Create articles for others  | ❌   | ✅     | ✅            |
| Update own articles         | ✅   | ✅     | ✅            |
| Update any article          | ❌   | ✅     | ✅            |
| Delete own articles         | ✅   | ❌     | ✅            |
| Delete any article          | ❌   | ❌     | ✅            |
| Update own profile          | ✅   | ✅     | ✅            |
| Update any user             | ❌   | ❌     | ✅            |
| Delete users / manage roles | ❌   | ❌     | ✅            |

---

## Running Tests

```bash
# Run all tests
docker compose exec web pytest

# With coverage (terminal)
docker compose exec web pytest --cov=app --cov-report=term-missing

# Generate HTML report (opens htmlcov/index.html)
docker compose exec web pytest --cov=app --cov-report=html

Open `htmlcov/index.html` in your browser to view the report.

# Single test file
docker compose exec web pytest tests/test_users.py
```

> Tests use SQLite in-memory — they do not affect your PostgreSQL data.

---

## Health Check

```bash
curl http://localhost:8000/health
```

Response when healthy:

```json
{
  "status": "ok",
  "services": {
    "api": "ok",
    "database": "ok"
  },
  "response_time_ms": 1.23
}
```

---

## Notes

- Live reload is enabled — code changes apply immediately without rebuilding.
- Roles are seeded automatically on every startup.
- There is no public registration endpoint — users are created via `manage.py`.
