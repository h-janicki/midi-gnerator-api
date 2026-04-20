from enum import Enum
from pydantic import BaseModel, Field


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
        examples=["melancholic minimal techno groove"],
    )
    track_type: TrackType = Field(
        ...,
        description="Type of track to generate",
    )
    key: Key = Field(
        default=Key.A_MINOR,
        description="Musical key",
    )
    bpm: int = Field(
        default=120,
        ge=60,
        le=200,
        description="Tempo in BPM",
    )
    bars: int = Field(
        default=4,
        ge=1,
        le=16,
        description="Length in bars (4/4 time)",
    )


class Note(BaseModel):
    pitch: int = Field(..., ge=0, le=127, description="MIDI pitch (0-127)")
    start: float = Field(..., ge=0, description="Start position in beats")
    duration: float = Field(..., gt=0, description="Length in beats")
    velocity: int = Field(default=80, ge=1, le=127)


class GenerationMetadata(BaseModel):
    description: str
    track_type: TrackType
    key: Key
    bpm: int
    bars: int
    note_count: int
