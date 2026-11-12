"""Integration tests against a real Postgres database."""
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import User

pytestmark = pytest.mark.integration


def make_user(username="alice", email="alice@example.com", password="Secret123"):
    user = User(username=username, email=email)
    user.set_password(password)
    return user


def test_create_user_persists_hash_and_timestamp(db_session):
    db_session.add(make_user())
    db_session.commit()

    stored = db_session.scalar(select(User).where(User.username == "alice"))
    assert stored is not None
    assert stored.password_hash != "Secret123"
    assert stored.check_password("Secret123")
    assert isinstance(stored.created_at, datetime)
    assert stored.created_at.tzinfo is not None


def test_duplicate_username_rejected_by_db(db_session):
    db_session.add(make_user())
    db_session.commit()
    db_session.add(make_user(email="other@example.com"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_duplicate_email_rejected_by_db(db_session):
    db_session.add(make_user())
    db_session.commit()
    db_session.add(make_user(username="bob"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_password_hash_is_required(db_session):
    db_session.add(User(username="nohash", email="nohash@example.com"))
    with pytest.raises(IntegrityError):
        db_session.commit()
