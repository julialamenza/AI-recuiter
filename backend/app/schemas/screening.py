from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ScreeningCreate(BaseModel):
    candidate_id: UUID
    job_id: UUID


class ScreeningOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID
    job_id: UUID
    score: int
    reasons: list[Any]
    summary_markdown: str
    model_recommendation: str
    human_decision: str | None
    human_decision_at: datetime | None
    rejection_confirmed: bool
    created_at: datetime


class ScreeningDecision(BaseModel):
    decision: Literal["reject", "shortlist", "manual_review"]
    confirm_rejection: bool | None = None
