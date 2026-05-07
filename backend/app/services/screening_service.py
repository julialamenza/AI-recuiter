import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.recruiting import compare_candidate_to_job
from app.models.screening import Screening
from app.services.candidate_service import get_candidate
from app.services.job_service import get_job


async def run_screening(
    session: AsyncSession,
    *,
    candidate_id: uuid.UUID,
    job_id: uuid.UUID,
) -> Screening:
    candidate = await get_candidate(session, candidate_id)
    if not candidate or not candidate.extracted_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate not found or profile not extracted yet.",
        )
    job = await get_job(session, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    cv_excerpt = (candidate.cv_extracted_text or "")[:12_000]
    jd_excerpt = job.raw_description[:12_000]

    result = await compare_candidate_to_job(
        candidate_profile=candidate.extracted_profile,
        job_structured=job.structured_requirements,
        cv_excerpt=cv_excerpt,
        jd_excerpt=jd_excerpt,
    )

    screening = Screening(
        candidate_id=candidate_id,
        job_id=job_id,
        score=result.score,
        reasons=result.reasons,
        summary_markdown=result.summary_markdown,
        model_recommendation=result.model_recommendation,
    )
    session.add(screening)
    await session.flush()
    return screening


async def get_screening(session: AsyncSession, screening_id: uuid.UUID) -> Screening | None:
    return await session.get(Screening, screening_id)


async def apply_human_decision(
    session: AsyncSession,
    *,
    screening_id: uuid.UUID,
    decision: str,
    confirm_rejection: bool | None,
) -> Screening:
    screening = await get_screening(session, screening_id)
    if not screening:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening not found.")

    if decision == "reject":
        if not confirm_rejection:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="confirm_rejection must be true to record a reject decision.",
            )
        screening.human_decision = "reject"
        screening.rejection_confirmed = True
    else:
        screening.human_decision = decision
        screening.rejection_confirmed = False

    screening.human_decision_at = datetime.now(UTC)
    await session.flush()
    return screening
