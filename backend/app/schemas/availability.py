from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WeeklyRule(BaseModel):
    """weekday: 0=Monday .. 6=Sunday (Python isoweekday: Mon=1..Sun=7 — we use 0-6 Mon-first)."""

    weekday: int = Field(..., ge=0, le=6)
    start: str = Field(..., description="HH:MM 24h")
    end: str = Field(..., description="HH:MM 24h")


class AvailabilityUpsert(BaseModel):
    user_id: str = Field(default="default", max_length=64)
    weekly_rules: list[WeeklyRule]
    timezone: str = Field(default="UTC", max_length=64)


class AvailabilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str
    weekly_rules: list[dict[str, Any]]
    timezone: str
    updated_at: datetime
