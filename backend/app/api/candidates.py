from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.candidate import CandidateCreateResponse, CandidateOut
from app.services import candidate_service

router = APIRouter()


@router.post("", response_model=CandidateCreateResponse, status_code=status.HTTP_201_CREATED)
async def upload_candidate(
    session: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    name: str | None = Form(None),
) -> CandidateOut:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file.")
    mime = file.content_type or "application/octet-stream"
    try:
        candidate = await candidate_service.create_candidate_from_upload(
            session,
            file_content=content,
            filename=file.filename or "cv",
            mime_type=mime,
            name=name,
        )
        await session.commit()
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        await session.rollback()
        raise HTTPException(status_code=503, detail=str(e)) from e
    await session.refresh(candidate)
    return CandidateOut.model_validate(candidate)


@router.get("", response_model=list[CandidateOut])
async def list_candidates(session: AsyncSession = Depends(get_db)) -> list[CandidateOut]:
    rows = await candidate_service.list_candidates(session)
    return [CandidateOut.model_validate(r) for r in rows]


@router.get("/{candidate_id}", response_model=CandidateOut)
async def get_candidate(candidate_id: UUID, session: AsyncSession = Depends(get_db)) -> CandidateOut:
    row = await candidate_service.get_candidate(session, candidate_id)
    if not row:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return CandidateOut.model_validate(row)
