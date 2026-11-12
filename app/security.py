"""Password hashing helpers built on bcrypt.

bcrypt only uses the first 72 bytes of a password, so the UserCreate schema
rejects anything longer instead of silently truncating it.
"""
import bcrypt

BCRYPT_MAX_BYTES = 72


def hash_password(plain_password: str) -> str:
    """Return a salted bcrypt hash of ``plain_password``."""
    if not isinstance(plain_password, str) or not plain_password:
        raise ValueError("Password must be a non-empty string")
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > BCRYPT_MAX_BYTES:
        raise ValueError(f"Password must be at most {BCRYPT_MAX_BYTES} bytes")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Return True if ``plain_password`` matches the stored ``password_hash``."""
    if not plain_password or not password_hash:
        return False
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > BCRYPT_MAX_BYTES:
        return False
    try:
        return bcrypt.checkpw(password_bytes, password_hash.encode("utf-8"))
    except ValueError:
        # Malformed hash stored in the database
        return False
