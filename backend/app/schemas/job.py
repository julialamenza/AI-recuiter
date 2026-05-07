from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=512)
    raw_description: str = Field(..., min_length=1)


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    raw_description: str
    structured_requirements: dict[str, Any] | None
    created_at: datetime
