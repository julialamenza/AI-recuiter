import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.recruiting import structure_job_requirements
from app.models.job import Job


async def create_job(session: AsyncSession, *, title: str, raw_description: str) -> Job:
    structured = await structure_job_requirements(raw_description)
    job = Job(
        title=title,
        raw_description=raw_description,
        structured_requirements=structured.model_dump(),
    )
    session.add(job)
    await session.flush()
    return job


async def get_job(session: AsyncSession, job_id: uuid.UUID) -> Job | None:
    return await session.get(Job, job_id)


async def list_jobs(session: AsyncSession) -> list[Job]:
    result = await session.scalars(select(Job).order_by(Job.created_at.desc()))
    return list(result)
