from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models import User
from app.schemas import UserCreate, UserRead

VALID = {"username": "alice", "email": "alice@example.com", "password": "Secret123"}


def test_user_create_valid():
    user = UserCreate(**VALID)
    assert user.username == "alice"
    assert user.email == "alice@example.com"


def test_email_is_lowercased():
    user = UserCreate(**{**VALID, "email": "Alice@Example.COM"})
    assert user.email == "alice@example.com"


@pytest.mark.parametrize("email", ["not-an-email", "missing@tld", "@example.com", "a b@example.com", ""])
def test_invalid_email_rejected(email):
    with pytest.raises(ValidationError):
        UserCreate(**{**VALID, "email": email})


@pytest.mark.parametrize("password", ["short1", "allletters", "12345678", "a" * 70 + "1" * 3])
def test_weak_or_too_long_password_rejected(password):
    with pytest.raises(ValidationError):
        UserCreate(**{**VALID, "password": password})


@pytest.mark.parametrize("username", ["ab", "a" * 51, "has space", "bad!char"])
def test_invalid_username_rejected(username):
    with pytest.raises(ValidationError):
        UserCreate(**{**VALID, "username": username})


@pytest.mark.parametrize("missing", ["username", "email", "password"])
def test_required_fields(missing):
    data = {k: v for k, v in VALID.items() if k != missing}
    with pytest.raises(ValidationError):
        UserCreate(**data)


def test_user_read_from_orm_omits_password_hash():
    orm_user = User(
        id=1,
        username="alice",
        email="alice@example.com",
        password_hash="$2b$12$fakehash",
        created_at=datetime.now(timezone.utc),
    )
    data = UserRead.model_validate(orm_user).model_dump()
    assert set(data) == {"id", "username", "email", "created_at"}
    assert "password_hash" not in data
    assert "password" not in data
