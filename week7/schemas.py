from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# Closed lists for strict categorization
class GenreEnum(str, Enum):
    Fiction = "Fiction"
    Nonfiction = "Nonfiction"
    Mystery = "Mystery"
    SciFi_Fantasy = "SciFi_Fantasy"
    Romance = "Romance"
    Childrens = "Childrens"
    Poetry = "Poetry"
    Other = "Other"


class AudienceEnum(str, Enum):
    Children = "Children"
    Young_Adult = "Young_Adult"
    Adult = "Adult"
    General = "General"


class MoodEnum(str, Enum):
    Inspiring = "Inspiring"
    Dark = "Dark"
    Lighthearted = "Lighthearted"
    Informative = "Informative"
    Whimsical = "Whimsical"
    Other = "Other"


# 1. Input Contract: Validates incoming request before spending an LLM call
class BookEnrichInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=300, description="Book title")
    price_gbp: float = Field(..., ge=0.0, description="Book price in GBP")
    rating_text: str = Field(..., min_length=1, max_length=20, description="Rating string")
    description: Optional[str] = Field(default=None, max_length=4000, description="Book description or null")


# 2. Output Contract: Guarantees the exact JSON shape returned to callers
class BookEnrichOutput(BaseModel):
    genre: GenreEnum
    target_audience: AudienceEnum
    mood: MoodEnum
    one_sentence_summary: str = Field(..., min_length=1, max_length=200)
    is_complete_record: bool
    confidence: float = Field(..., ge=0.0, le=1.0)