import uuid
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.recruiting import extract_candidate_profile
from app.config import settings
from app.models.candidate import Candidate
from app.services.document_extract import extract_text_from_bytes


async def create_candidate_from_upload(
    session: AsyncSession,
    *,
    file_content: bytes,
    filename: str,
    mime_type: str,
    name: str | None,
) -> Candidate:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(filename).suffix or ".bin"
    file_id = uuid.uuid4()
    rel_path = upload_dir / f"{file_id}{ext}"
    rel_path.write_bytes(file_content)

    try:
        text = extract_text_from_bytes(file_content, mime_type)
    except ValueError as e:
        raise ValueError(str(e)) from e

    profile = None
    if text:
        profile_model = await extract_candidate_profile(text)
        profile = profile_model.model_dump()

    candidate = Candidate(
        name=name,
        cv_storage_path=str(rel_path),
        cv_mime_type=mime_type,
        cv_extracted_text=text or None,
        extracted_profile=profile,
    )
    session.add(candidate)
    await session.flush()
    return candidate


async def get_candidate(session: AsyncSession, candidate_id: uuid.UUID) -> Candidate | None:
    return await session.get(Candidate, candidate_id)


async def list_candidates(session: AsyncSession) -> list[Candidate]:
    result = await session.scalars(select(Candidate).order_by(Candidate.created_at.desc()))
    return list(result)
