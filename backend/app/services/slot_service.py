from datetime import UTC, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview import InterviewProposal
from app.services.availability_service import get_availability
from app.services.screening_service import get_screening


def _parse_hhmm(s: str) -> tuple[int, int]:
    parts = s.strip().split(":")
    h = int(parts[0])
    m = int(parts[1]) if len(parts) > 1 else 0
    return h, m


def generate_interview_slots(
    *,
    weekly_rules: list[dict],
    timezone: str,
    slot_minutes: int = 60,
    max_slots: int = 3,
    horizon_days: int = 21,
) -> list[dict]:
    """weekly_rules: weekday 0=Monday .. 6=Sunday, start/end HH:MM in local TZ."""
    if not weekly_rules:
        return []

    try:
        tz = ZoneInfo(timezone)
    except Exception as e:
        raise ValueError(f"Invalid timezone: {timezone}") from e

    now_local = datetime.now(tz)
    start_day = now_local.date()
    slots: list[datetime] = []

    for delta in range(horizon_days):
        day = start_day + timedelta(days=delta)
        python_weekday = day.weekday()  # Mon=0
        for rule in weekly_rules:
            if int(rule.get("weekday", -1)) != python_weekday:
                continue
            sh, sm = _parse_hhmm(str(rule["start"]))
            eh, em = _parse_hhmm(str(rule["end"]))
            cursor = datetime.combine(day, datetime.min.time().replace(hour=sh, minute=sm), tzinfo=tz)
            end_dt = datetime.combine(day, datetime.min.time().replace(hour=eh, minute=em), tzinfo=tz)
            while cursor + timedelta(minutes=slot_minutes) <= end_dt and len(slots) < max_slots:
                if cursor > now_local:
                    slots.append(cursor)
                    if len(slots) >= max_slots:
                        break
                cursor += timedelta(minutes=slot_minutes)
            if len(slots) >= max_slots:
                break
        if len(slots) >= max_slots:
            break

    return [
        {
            "start": s.astimezone(UTC).isoformat(),
            "duration_minutes": slot_minutes,
        }
        for s in slots[:max_slots]
    ]


async def create_interview_proposal_for_screening(
    session: AsyncSession,
    *,
    screening_id: UUID,
    user_id: str = "default",
) -> InterviewProposal:
    screening = await get_screening(session, screening_id)
    if not screening:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screening not found.")

    avail = await get_availability(session, user_id)
    if not avail or not avail.weekly_rules:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Set recruiter availability before generating proposals.",
        )

    proposed = generate_interview_slots(
        weekly_rules=list(avail.weekly_rules),
        timezone=avail.timezone,
    )
    if not proposed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No upcoming slots match your availability rules. Adjust weekly hours or timezone.",
        )
    proposal = InterviewProposal(
        screening_id=screening.id,
        proposed_slots=proposed,
        status="draft",
    )
    session.add(proposal)
    await session.flush()
    return proposal


async def patch_interview_proposal(
    session: AsyncSession,
    *,
    proposal_id: UUID,
    candidate_selected_slot: str | None,
    status: str | None,
) -> InterviewProposal | None:
    proposal = await session.get(InterviewProposal, proposal_id)
    if not proposal:
        return None
    if candidate_selected_slot is not None:
        proposal.candidate_selected_slot = candidate_selected_slot
    if status is not None:
        proposal.status = status
    await session.flush()
    return proposal
