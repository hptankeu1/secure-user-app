# Secure User API — FastAPI, SQLAlchemy, Pydantic

A FastAPI service with a secure user model: bcrypt password hashing, unique
`username`/`email` constraints, Pydantic validation, unit and integration tests,
and a GitHub Actions pipeline that tests, scans and publishes a Docker image to
Docker Hub.

**Docker Hub image:** https://hub.docker.com/r/<your-dockerhub-username>/secure-user-app

```bash
docker pull <your-dockerhub-username>/secure-user-app:latest
```

## Project structure

```
app/
  database.py   # engine, session factory, Base, get_db dependency
  models.py     # SQLAlchemy User model (unique username/email, created_at)
  schemas.py    # Pydantic UserCreate / UserRead / UserLogin
  security.py   # hash_password / verify_password (bcrypt)
  main.py       # FastAPI routes: /health, /users/register, /users/login, /users/{id}
tests/
  unit/         # hashing + schema validation (no database needed)
  integration/  # real Postgres: uniqueness, invalid emails, API endpoints
.github/workflows/ci-cd.yml
Dockerfile
docker-compose.yml
```

## User model

| Column          | Type                     | Notes                         |
|-----------------|--------------------------|-------------------------------|
| `id`            | integer                  | primary key                   |
| `username`      | varchar(50)              | **unique**, indexed           |
| `email`         | varchar(255)             | **unique**, indexed, lowercased |
| `password_hash` | varchar(255)             | bcrypt hash, never returned   |
| `created_at`    | timestamp with time zone | set by the database           |

`UserCreate` accepts `username`, `email`, `password` (8+ chars, at least one
letter and one digit, max 72 bytes — bcrypt's limit). `UserRead` returns `id`,
`username`, `email`, `created_at` and never exposes the password hash.

## Running tests locally

### 1. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

### 2. Unit tests (no database needed)

```bash
pytest tests/unit -v
```

### 3. Integration tests (need Postgres)

Start Postgres with Docker:

```bash
docker compose up -d db
```

Then run the tests (the default `DATABASE_URL` already points at this container):

```bash
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_db
pytest tests/integration -v
```

### 4. Everything, with coverage

```bash
pytest --cov=app --cov-report=term-missing
```

Stop the database with `docker compose down`.

## Running the app

```bash
docker compose up --build
```

Open http://localhost:8000/docs for the interactive API.

Or run the published image against your own database:

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+psycopg://user:pass@host:5432/dbname \
  <your-dockerhub-username>/secure-user-app:latest
```

## CI/CD pipeline

`.github/workflows/ci-cd.yml` runs on every push and pull request to `main`:

1. **test** — spins up a Postgres 16 service container, runs unit tests, integration tests, then the full suite with coverage.
2. **build-scan-deploy** (pushes to `main` only, after tests pass) — builds the image, scans it with Trivy (fails on fixable HIGH/CRITICAL vulnerabilities), smoke-tests `/health`, then pushes `latest` and the commit SHA tag to Docker Hub.

### Required repository secrets

In GitHub: **Settings → Secrets and variables → Actions → New repository secret**

| Secret               | Value                                                   |
|----------------------|---------------------------------------------------------|
| `DOCKERHUB_USERNAME` | your Docker Hub username                                |
| `DOCKERHUB_TOKEN`    | a Docker Hub access token (Account Settings → Personal access tokens, Read & Write) |

## Screenshots

See the `screenshots/` folder for the successful GitHub Actions run and the image on Docker Hub.
