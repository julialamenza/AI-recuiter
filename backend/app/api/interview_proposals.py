from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.interview import InterviewProposalOut, InterviewProposalPatch
from app.services import slot_service

router = APIRouter()


@router.post("/{screening_id}/interview-proposals", response_model=InterviewProposalOut, status_code=201)
async def create_proposal(
    screening_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> InterviewProposalOut:
    try:
        proposal = await slot_service.create_interview_proposal_for_screening(
            session, screening_id=screening_id
        )
        await session.commit()
    except HTTPException:
        await session.rollback()
        raise
    await session.refresh(proposal)
    return InterviewProposalOut.model_validate(proposal)


@router.patch(
    "/{screening_id}/interview-proposals/{proposal_id}",
    response_model=InterviewProposalOut,
)
async def patch_proposal(
    screening_id: UUID,
    proposal_id: UUID,
    body: InterviewProposalPatch,
    session: AsyncSession = Depends(get_db),
) -> InterviewProposalOut:
    proposal = await slot_service.patch_interview_proposal(
        session,
        proposal_id=proposal_id,
        candidate_selected_slot=body.candidate_selected_slot,
        status=body.status,
    )
    if not proposal or proposal.screening_id != screening_id:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    await session.commit()
    await session.refresh(proposal)
    return InterviewProposalOut.model_validate(proposal)
