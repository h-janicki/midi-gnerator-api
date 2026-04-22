from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Key(str, Enum):
    C_MAJOR = "C major"
    C_MINOR = "C minor"
    C_SHARP_MAJOR = "C# major"
    C_SHARP_MINOR = "C# minor"
    D_MAJOR = "D major"
    D_MINOR = "D minor"
    D_SHARP_MAJOR = "D# major"
    D_SHARP_MINOR = "D# minor"
    E_MAJOR = "E major"
    E_MINOR = "E minor"
    F_MAJOR = "F major"
    F_MINOR = "F minor"
    F_SHARP_MAJOR = "F# major"
    F_SHARP_MINOR = "F# minor"
    G_MAJOR = "G major"
    G_MINOR = "G minor"
    G_SHARP_MAJOR = "G# major"
    G_SHARP_MINOR = "G# minor"
    A_MAJOR = "A major"
    A_MINOR = "A minor"
    A_SHARP_MAJOR = "A# major"
    A_SHARP_MINOR = "A# minor"
    B_MAJOR = "B major"
    B_MINOR = "B minor"


class TrackType(str, Enum):
    MELODY = "melody"
    BASSLINE = "bassline"
    CHORDS = "chords"
    DRUMS = "drums"


class GenerateRequest(BaseModel):
    description: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Free-text description, e.g. 'melancholic, lo-fi, slight swing feel'",
    )
    track_type: TrackType
    key: Key = Key.A_MINOR
    bpm: int = Field(default=120, ge=60, le=200)
    bars: int = Field(default=4, ge=1, le=16)


class Note(BaseModel):
    pitch: int = Field(..., ge=0, le=127)
    start: float = Field(..., ge=0)
    duration: float = Field(..., gt=0)
    velocity: int = Field(default=80, ge=1, le=127)


class GenerationResponse(BaseModel):
    """Returned after /generate - client uses id to download the MIDI file."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    description: str
    track_type: TrackType
    key: Key
    bpm: int
    bars: int
    note_count: int
    is_favorite: bool


class HistoryResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[GenerationResponse]
