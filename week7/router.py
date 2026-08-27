import os
from fastapi import APIRouter, HTTPException, status
from .schemas import (
    AudienceEnum,
    BookEnrichInput,
    BookEnrichOutput,
    GenreEnum,
    MoodEnum,
)

router = APIRouter()


@router.post(
    "/enrich",
    response_model=BookEnrichOutput,
    status_code=status.HTTP_200_OK,
    summary="Enrich a scraped book record"
)
async def enrich_book(payload: BookEnrichInput):
    # Check if Stub Mode is active (saves quota during development)
    is_stub = os.getenv("LLM_STUB", "0") == "1"

    if is_stub:
        # Return a deterministic, schema-compliant object without calling the model
        return BookEnrichOutput(
            genre=GenreEnum.Fiction,
            target_audience=AudienceEnum.General,
            mood=MoodEnum.Lighthearted,
            one_sentence_summary=f"A stub summary for '{payload.title}'.",
            is_complete_record=payload.description is not None,
            confidence=1.0,
        )

    # Real LLM call will be wired in Stages 2, 3, and 4
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Model integration is not wired yet. Set LLM_STUB=1 in your .env to test."
    )