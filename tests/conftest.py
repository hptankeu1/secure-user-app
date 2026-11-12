"""Shared fixtures.

Unit tests need nothing. Integration tests (marked ``integration``) use the real
database pointed to by DATABASE_URL — a Postgres service container in CI.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database import Base, SessionLocal, engine


@pytest.fixture(scope="session")
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database):
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        session.commit()
        session.close()


@pytest.fixture
def client(db_session):
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
