from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.availability import AvailabilityOut, AvailabilityUpsert
from app.services import availability_service

router = APIRouter()


@router.put("", response_model=AvailabilityOut)
async def put_availability(body: AvailabilityUpsert, session: AsyncSession = Depends(get_db)) -> AvailabilityOut:
    rules = [r.model_dump() for r in body.weekly_rules]
    row = await availability_service.upsert_availability(
        session,
        user_id=body.user_id,
        weekly_rules=rules,
        timezone=body.timezone,
    )
    await session.commit()
    await session.refresh(row)
    return AvailabilityOut.model_validate(row)


@router.get("", response_model=AvailabilityOut)
async def get_availability(
    user_id: str = "default",
    session: AsyncSession = Depends(get_db),
) -> AvailabilityOut:
    row = await availability_service.get_availability(session, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="Availability not set.")
    return AvailabilityOut.model_validate(row)
