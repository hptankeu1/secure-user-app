"""Pydantic schemas for validating input and serializing output."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.security import BCRYPT_MAX_BYTES


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class UserCreate(UserBase):
    """Data accepted when registering a new user."""

    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if len(value.encode("utf-8")) > BCRYPT_MAX_BYTES:
            raise ValueError(f"Password must be at most {BCRYPT_MAX_BYTES} bytes")
        if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one letter and one digit")
        return value


class UserRead(UserBase):
    """Data returned to clients — never includes the password or its hash."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class UserLogin(BaseModel):
    username: str
    password: str
