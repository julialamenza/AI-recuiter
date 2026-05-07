from typing import Any

from app.agents.client import get_openai_client
from app.agents.models import CompareScreeningResult, ExtractedCandidateProfile, StructuredJobRequirements
from app.config import settings


async def extract_candidate_profile(cv_text: str) -> ExtractedCandidateProfile:
    client = get_openai_client()
    text = cv_text[:120_000]
    completion = await client.beta.chat.completions.parse(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You extract structured recruiting fields from a CV. "
                    "Infer seniority (e.g. junior, mid, senior, staff, principal). "
                    "years_experience may be a number or short text if ambiguous. "
                    "If salary expectations are not stated, leave salary_expectations null. "
                    "Return only structured data matching the schema."
                ),
            },
            {"role": "user", "content": text},
        ],
        response_format=ExtractedCandidateProfile,
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise ValueError("OpenAI returned no parsed candidate profile")
    return parsed


async def structure_job_requirements(job_description: str) -> StructuredJobRequirements:
    client = get_openai_client()
    text = job_description[:120_000]
    completion = await client.beta.chat.completions.parse(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You convert a job description into structured recruiting requirements. "
                    "Separate required vs preferred skills when possible. "
                    "Summarize seniority_level, location_policy, and comp_band if present."
                ),
            },
            {"role": "user", "content": text},
        ],
        response_format=StructuredJobRequirements,
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise ValueError("OpenAI returned no parsed job structure")
    return parsed


async def compare_candidate_to_job(
    *,
    candidate_profile: dict[str, Any],
    job_structured: dict[str, Any] | None,
    cv_excerpt: str,
    jd_excerpt: str,
) -> CompareScreeningResult:
    client = get_openai_client()
    completion = await client.beta.chat.completions.parse(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an assistant for recruiters. Compare the candidate to the job. "
                    "Produce a score 0-100 for overall fit, a list of concise reasons, "
                    "and summary_markdown as recruiter-friendly markdown (headings/bullets). "
                    "model_recommendation is ONLY a suggestion: use reject when clearly a poor match, "
                    "shortlist when strong fit, manual_review when uncertain. "
                    "Never treat reject as final—humans must confirm. Prefer manual_review when ambiguous."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Candidate profile JSON:\n{candidate_profile}\n\n"
                    f"Job structured JSON:\n{job_structured}\n\n"
                    f"CV excerpt:\n{cv_excerpt[:8000]}\n\n"
                    f"JD excerpt:\n{jd_excerpt[:8000]}\n"
                ),
            },
        ],
        response_format=CompareScreeningResult,
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise ValueError("OpenAI returned no parsed comparison")
    return parsed
