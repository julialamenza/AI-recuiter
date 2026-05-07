from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExtractedCandidateProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skills: list[str] = Field(default_factory=list)
    seniority: str = ""
    years_experience: str | float | int | None = None
    location: str | None = None
    salary_expectations: str | None = None
    confidence_notes: str | None = None


class StructuredJobRequirements(BaseModel):
    model_config = ConfigDict(extra="forbid")

    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    seniority_level: str = ""
    location_policy: str | None = None
    comp_band: str | None = None


class CompareScreeningResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: int = Field(ge=0, le=100)
    reasons: list[str] = Field(default_factory=list)
    summary_markdown: str = ""
    model_recommendation: Literal["reject", "shortlist", "manual_review"]
