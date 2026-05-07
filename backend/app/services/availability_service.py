import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview import RecruiterAvailability


async def upsert_availability(
    session: AsyncSession,
    *,
    user_id: str,
    weekly_rules: list[dict],
    timezone: str,
) -> RecruiterAvailability:
    result = await session.execute(
        select(RecruiterAvailability).where(RecruiterAvailability.user_id == user_id)
    )
    row = result.scalar_one_or_none()
    if row:
        row.weekly_rules = weekly_rules
        row.timezone = timezone
        row.updated_at = datetime.now(UTC)
        await session.flush()
        return row
    row = RecruiterAvailability(
        user_id=user_id,
        weekly_rules=weekly_rules,
        timezone=timezone,
    )
    session.add(row)
    await session.flush()
    return row


async def get_availability(session: AsyncSession, user_id: str = "default") -> RecruiterAvailability | None:
    result = await session.execute(
        select(RecruiterAvailability).where(RecruiterAvailability.user_id == user_id)
    )
    return result.scalar_one_or_none()
