"""Modelo de usuario de ejemplo (listo para activarse con auth real)."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    first_last_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    second_last_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(40), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str | None] = mapped_column(
        String(80), unique=True, index=True, nullable=True
    )
    user_number: Mapped[str | None] = mapped_column(
        String(80), unique=True, index=True, nullable=True
    )
    password_hash: Mapped[str] = mapped_column(String(255))
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_top_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        ident = self.username or self.user_number or self.email
        return f"<User {ident}>"
