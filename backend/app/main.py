from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAIError,
    RateLimitError,
)

from app.api.router import api_router
from app.config import settings

app = FastAPI(title="AI Recruiting API", version="0.1.0")


@app.exception_handler(OpenAIError)
async def openai_exception_handler(_request: Request, exc: OpenAIError) -> JSONResponse:
    """Map OpenAI SDK errors to HTTP responses so clients get JSON instead of a generic 500."""
    if isinstance(exc, AuthenticationError):
        return JSONResponse(
            status_code=503,
            content={
                "detail": "OpenAI rejected the API key. Check OPENAI_API_KEY in backend/.env.",
            },
        )
    if isinstance(exc, RateLimitError):
        return JSONResponse(
            status_code=503,
            content={
                "detail": exc.message
                or "OpenAI rate limit or quota exceeded. Check billing and plan limits.",
            },
        )
    if isinstance(exc, APIStatusError):
        return JSONResponse(
            status_code=502,
            content={"detail": f"OpenAI API error ({exc.status_code}): {exc.message}"},
        )
    if isinstance(exc, (APIConnectionError, APITimeoutError)):
        return JSONResponse(
            status_code=503,
            content={"detail": f"Could not reach OpenAI: {exc.message}"},
        )
    return JSONResponse(status_code=502, content={"detail": str(exc)})

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.on_event("startup")
async def startup() -> None:
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
