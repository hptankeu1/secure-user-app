"""End-to-end API tests through FastAPI with a real Postgres database."""
import pytest
from sqlalchemy import select

from app.models import User

pytestmark = pytest.mark.integration

PAYLOAD = {"username": "alice", "email": "alice@example.com", "password": "Secret123"}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_register_returns_user_without_password(client, db_session):
    response = client.post("/users/register", json=PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert body["email"] == "alice@example.com"
    assert "id" in body and "created_at" in body
    assert "password" not in body and "password_hash" not in body

    stored = db_session.scalar(select(User).where(User.username == "alice"))
    assert stored.password_hash != PAYLOAD["password"]


def test_register_duplicate_username(client):
    client.post("/users/register", json=PAYLOAD)
    response = client.post("/users/register", json={**PAYLOAD, "email": "new@example.com"})
    assert response.status_code == 409


def test_register_duplicate_email_case_insensitive(client):
    client.post("/users/register", json=PAYLOAD)
    response = client.post("/users/register", json={**PAYLOAD, "username": "bob", "email": "ALICE@example.com"})
    assert response.status_code == 409


def test_register_invalid_email(client):
    response = client.post("/users/register", json={**PAYLOAD, "email": "not-an-email"})
    assert response.status_code == 422


def test_register_weak_password(client):
    response = client.post("/users/register", json={**PAYLOAD, "password": "short"})
    assert response.status_code == 422


def test_login_success(client):
    client.post("/users/register", json=PAYLOAD)
    response = client.post("/users/login", json={"username": "alice", "password": "Secret123"})
    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_login_wrong_password(client):
    client.post("/users/register", json=PAYLOAD)
    response = client.post("/users/login", json={"username": "alice", "password": "Wrong1234"})
    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post("/users/login", json={"username": "ghost", "password": "Secret123"})
    assert response.status_code == 401


def test_get_user(client):
    created = client.post("/users/register", json=PAYLOAD).json()
    response = client.get(f"/users/{created['id']}")
    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


def test_get_missing_user(client):
    assert client.get("/users/9999").status_code == 404
