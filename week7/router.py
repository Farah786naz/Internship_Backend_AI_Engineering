import os
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import PlainTextResponse

from week7.client import call_llm
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
    try:
        raw_model_response = call_llm(payload.model_dump())
        # Return plain text / parsed json so we can inspect raw model adherence
        return PlainTextResponse(content=raw_model_response, status_code=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model call failed: {str(e)}"
        )