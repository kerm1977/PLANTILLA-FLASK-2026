"""Modelos del sistema de cotización (Cotizador): campos dinámicos y respuestas."""
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class QuoteField(Base):
    """Campo dinámico de una pregunta del formulario de cotización (wizard)."""

    __tablename__ = "quote_fields"

    id: Mapped[int] = mapped_column(primary_key=True)
    step: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    field_key: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    field_type: Mapped[str] = mapped_column(String(20), nullable=False, default="text")
    label: Mapped[str] = mapped_column(Text, nullable=False)
    help_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    options: Mapped[list | None] = mapped_column(JSON, nullable=True)
    max_choices: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<QuoteField {self.field_key}>"


class QuoteSubmission(Base):
    """Respuestas enviadas por un visitante al completar el cotizador."""

    __tablename__ = "quote_submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<QuoteSubmission {self.id}>"
