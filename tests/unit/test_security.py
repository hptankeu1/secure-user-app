import pytest

from app.models import User
from app.security import hash_password, verify_password


def test_hash_is_not_plain_text():
    hashed = hash_password("Secret123")
    assert hashed != "Secret123"
    assert hashed.startswith("$2")  # bcrypt identifier


def test_same_password_produces_different_hashes():
    assert hash_password("Secret123") != hash_password("Secret123")


def test_verify_correct_password():
    hashed = hash_password("Secret123")
    assert verify_password("Secret123", hashed) is True


def test_verify_wrong_password():
    hashed = hash_password("Secret123")
    assert verify_password("Wrong1234", hashed) is False


def test_verify_is_case_sensitive():
    hashed = hash_password("Secret123")
    assert verify_password("secret123", hashed) is False


@pytest.mark.parametrize("plain,stored", [("", "x"), ("Secret123", ""), ("Secret123", "not-a-hash")])
def test_verify_handles_bad_input(plain, stored):
    assert verify_password(plain, stored) is False


def test_verify_rejects_password_over_72_bytes():
    hashed = hash_password("a" * 72)
    assert verify_password("a" * 73, hashed) is False


def test_hash_rejects_empty_password():
    with pytest.raises(ValueError):
        hash_password("")


def test_hash_rejects_password_over_72_bytes():
    with pytest.raises(ValueError):
        hash_password("a" * 73)


def test_unicode_password_round_trip():
    hashed = hash_password("motdepasse-éàç-1")
    assert verify_password("motdepasse-éàç-1", hashed)


def test_user_model_set_and_check_password():
    user = User(username="alice", email="alice@example.com")
    user.set_password("Secret123")
    assert user.password_hash != "Secret123"
    assert user.check_password("Secret123")
    assert not user.check_password("nope12345")
