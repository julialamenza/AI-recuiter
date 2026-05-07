import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services import screening_service


@pytest.mark.asyncio
async def test_reject_requires_confirmation() -> None:
    screening_id = uuid.uuid4()
    mock_session = MagicMock()
    screening = MagicMock()
    screening.id = screening_id

    with patch.object(screening_service, "get_screening", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = screening
        with pytest.raises(HTTPException) as exc:
            await screening_service.apply_human_decision(
                mock_session,
                screening_id=screening_id,
                decision="reject",
                confirm_rejection=None,
            )
        assert exc.value.status_code == 400

    with patch.object(screening_service, "get_screening", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = screening
        with pytest.raises(HTTPException) as exc:
            await screening_service.apply_human_decision(
                mock_session,
                screening_id=screening_id,
                decision="reject",
                confirm_rejection=False,
            )
        assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_reject_with_confirmation_succeeds() -> None:
    screening_id = uuid.uuid4()
    mock_session = MagicMock()
    mock_session.flush = AsyncMock()
    screening = MagicMock()
    screening.id = screening_id

    with patch.object(screening_service, "get_screening", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = screening
        out = await screening_service.apply_human_decision(
            mock_session,
            screening_id=screening_id,
            decision="reject",
            confirm_rejection=True,
        )
        assert out is screening
        assert screening.human_decision == "reject"
        assert screening.rejection_confirmed is True


@pytest.mark.asyncio
async def test_shortlist_no_confirmation_required() -> None:
    screening_id = uuid.uuid4()
    mock_session = MagicMock()
    mock_session.flush = AsyncMock()
    screening = MagicMock()

    with patch.object(screening_service, "get_screening", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = screening
        await screening_service.apply_human_decision(
            mock_session,
            screening_id=screening_id,
            decision="shortlist",
            confirm_rejection=None,
        )
        assert screening.human_decision == "shortlist"
        assert screening.rejection_confirmed is False
