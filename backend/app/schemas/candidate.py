from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str | None
    cv_mime_type: str
    extracted_profile: dict[str, Any] | None
    created_at: datetime


class CandidateCreateResponse(CandidateOut):
    pass
