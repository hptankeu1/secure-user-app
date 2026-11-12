# Reflection — Secure User Model and CI/CD Pipeline

## What I built

I extended my FastAPI application with a `User` model in SQLAlchemy, Pydantic
schemas for input and output, bcrypt password hashing, a test suite split into
unit and integration tests, and a GitHub Actions pipeline that tests the code
against a real Postgres database, scans the Docker image, and pushes it to
Docker Hub.

## Key experiences

**Separating input and output schemas.** Having `UserCreate` and `UserRead` as
two distinct schemas made the security boundary explicit. The password only
exists on the way in; on the way out, `UserRead` is built from the ORM object
with `from_attributes=True` and simply has no field for the hash. I added a
unit test that checks the serialized keys so a future change cannot leak the
hash by accident.

**Enforcing uniqueness in two places.** The route checks for an existing
username or email first so the client gets a clear `409 Conflict`. The database
`UNIQUE` constraints are the real guarantee, though: if two requests arrive at
the same moment, both can pass the check, and only the constraint stops the
duplicate. I catch `IntegrityError` and return the same `409` so that race is
handled too. The integration tests hit the constraints directly to prove they
exist in Postgres, not just in Python.

**Unit vs. integration tests.** Unit tests (hashing, schema validation) run in
milliseconds with no setup. Integration tests need a real database, which is
exactly what catches problems a mock would hide — for example, timezone-aware
`created_at` values and constraint errors only behave correctly against
Postgres. Truncating the table after each test kept tests independent.

## Challenges

**bcrypt's 72-byte limit.** Newer versions of `bcrypt` raise an error for
passwords longer than 72 bytes instead of silently truncating them, and the
older `passlib` wrapper is no longer maintained and breaks with recent bcrypt
releases. I used `bcrypt` directly and added validation in `UserCreate` so a
too-long password returns a clean `422` instead of a server error. The limit is
in bytes, not characters, so accented characters count for more than one.

**Case-insensitive emails.** `Alice@Example.com` and `alice@example.com` should
be the same account. I normalize emails to lowercase in the schema and wrote a
test registering both versions to confirm the second gets rejected.

**Database availability in CI.** A service container can still be starting up
when the first test step runs. Adding a `pg_isready` health check to the
Postgres service makes GitHub Actions wait until the database accepts
connections before running any tests.

**Supply-chain security of the pipeline itself.** While setting up the image
scan, I learned that Trivy's own GitHub Action had its version tags hijacked in
March 2026, so pipelines using older tags could leak secrets. I pinned the
action to `0.35.0` and the scanner binary to `v0.69.3`, the versions the Aqua
advisory lists as safe. It was a good reminder that CI tools need the same
scrutiny as application dependencies.

**Keeping the image scan clean.** The scan fails the build on fixable HIGH or
CRITICAL vulnerabilities. Running `apt-get upgrade` in the Dockerfile and using
a slim base image kept the findings low, and running the container as a
non-root user limits damage if something is ever exploited.

## What I would improve next

- Add JWT authentication so login returns a token instead of the user record.
- Use Alembic migrations instead of `create_all` so schema changes are versioned.
- Add rate limiting on the login endpoint to slow down password guessing.
