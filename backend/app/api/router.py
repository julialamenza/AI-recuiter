from fastapi import APIRouter

from app.api import availability, candidates, interview_proposals, jobs, screenings

api_router = APIRouter()
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(screenings.router, prefix="/screenings", tags=["screenings"])
api_router.include_router(availability.router, prefix="/availability", tags=["availability"])
api_router.include_router(
    interview_proposals.router, prefix="/screenings", tags=["interview-proposals"]
)
