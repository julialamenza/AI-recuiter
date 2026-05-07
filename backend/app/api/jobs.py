from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.job import JobCreate, JobOut
from app.services import job_service

router = APIRouter()


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
async def create_job(body: JobCreate, session: AsyncSession = Depends(get_db)) -> JobOut:
    try:
        job = await job_service.create_job(session, title=body.title, raw_description=body.raw_description)
        await session.commit()
    except RuntimeError as e:
        await session.rollback()
        raise HTTPException(status_code=503, detail=str(e)) from e
    await session.refresh(job)
    return JobOut.model_validate(job)


@router.get("", response_model=list[JobOut])
async def list_jobs(session: AsyncSession = Depends(get_db)) -> list[JobOut]:
    rows = await job_service.list_jobs(session)
    return [JobOut.model_validate(r) for r in rows]


@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: UUID, session: AsyncSession = Depends(get_db)) -> JobOut:
    row = await job_service.get_job(session, job_id)
    if not row:
        raise HTTPException(status_code=404, detail="Job not found.")
    return JobOut.model_validate(row)
