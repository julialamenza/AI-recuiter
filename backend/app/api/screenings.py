from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.screening import ScreeningCreate, ScreeningDecision, ScreeningOut
from app.services import screening_service

router = APIRouter()


@router.post("", response_model=ScreeningOut, status_code=status.HTTP_201_CREATED)
async def create_screening(body: ScreeningCreate, session: AsyncSession = Depends(get_db)) -> ScreeningOut:
    try:
        screening = await screening_service.run_screening(
            session,
            candidate_id=body.candidate_id,
            job_id=body.job_id,
        )
        await session.commit()
    except HTTPException:
        await session.rollback()
        raise
    except RuntimeError as e:
        await session.rollback()
        raise HTTPException(status_code=503, detail=str(e)) from e
    await session.refresh(screening)
    return ScreeningOut.model_validate(screening)


@router.get("/{screening_id}", response_model=ScreeningOut)
async def get_screening(screening_id: UUID, session: AsyncSession = Depends(get_db)) -> ScreeningOut:
    row = await screening_service.get_screening(session, screening_id)
    if not row:
        raise HTTPException(status_code=404, detail="Screening not found.")
    return ScreeningOut.model_validate(row)


@router.patch("/{screening_id}/decision", response_model=ScreeningOut)
async def patch_decision(
    screening_id: UUID,
    body: ScreeningDecision,
    session: AsyncSession = Depends(get_db),
) -> ScreeningOut:
    try:
        screening = await screening_service.apply_human_decision(
            session,
            screening_id=screening_id,
            decision=body.decision,
            confirm_rejection=body.confirm_rejection,
        )
        await session.commit()
    except HTTPException:
        await session.rollback()
        raise
    await session.refresh(screening)
    return ScreeningOut.model_validate(screening)
