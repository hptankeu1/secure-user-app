"""SQLAlchemy ORM models."""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.security import hash_password, verify_password


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def set_password(self, plain_password: str) -> None:
        self.password_hash = hash_password(plain_password)

    def check_password(self, plain_password: str) -> bool:
        return verify_password(plain_password, self.password_hash)

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<User id={self.id} username={self.username!r}>"
