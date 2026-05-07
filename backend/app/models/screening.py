from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
class Screening(Base):
    __tablename__ = "screenings"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    candidate_id: Mapped[UUID] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    reasons: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    summary_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    model_recommendation: Mapped[str] = mapped_column(String(32), nullable=False)
    human_decision: Mapped[str | None] = mapped_column(String(32), nullable=True)
    human_decision_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    candidate = relationship("Candidate", lazy="selectin")
    job = relationship("Job", lazy="selectin")
