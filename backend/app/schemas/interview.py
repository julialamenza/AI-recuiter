from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InterviewProposalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    screening_id: UUID
    proposed_slots: list[dict[str, Any]]
    status: str
    candidate_selected_slot: str | None
    created_at: datetime


class InterviewProposalPatch(BaseModel):
    candidate_selected_slot: str | None = None
    status: str | None = Field(default=None, description="e.g. candidate_responded")
