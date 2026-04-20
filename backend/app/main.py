import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import GenerateRequest, GenerationMetadata
from app.services.claude_client import generate_notes
from app.services.midi_builder import notes_to_midi

logging.basicConfig(level=settings.log_level)

app = FastAPI(
    title="MIDI Generator",
    description=(
        "REST API that generates MIDI tracks from natural-language descriptions "
        "and musical parameters. Uses Claude API to produce note sequences, "
        "then converts them into standard .mid files ready for import into Ableton or any DAW."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post(
    "/generate",
    tags=["generation"],
    summary="Generate and download a MIDI file",
    response_class=Response,
    responses={
        200: {
            "content": {"audio/midi": {}},
            "description": "Standard .mid file ready to drop into a DAW",
        }
    },
)
def generate(req: GenerateRequest):
    """Generate a MIDI track based on description and parameters."""
    try:
        notes = generate_notes(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logging.exception("Generation failed")
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")

    midi_bytes = notes_to_midi(notes, req.bpm)

    key_slug = req.key.value.replace(" ", "_").replace("#", "sharp")
    filename = f"{req.track_type.value}_{key_slug}_{req.bpm}bpm.mid"

    return Response(
        content=midi_bytes,
        media_type="audio/midi",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Note-Count": str(len(notes)),
        },
    )


@app.post(
    "/preview",
    tags=["generation"],
    summary="Preview metadata without generating a file",
    response_model=GenerationMetadata,
)
def preview(req: GenerateRequest):
    """Same as /generate, but returns metadata only. Useful for testing prompts."""
    try:
        notes = generate_notes(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return GenerationMetadata(
        description=req.description,
        track_type=req.track_type,
        key=req.key,
        bpm=req.bpm,
        bars=req.bars,
        note_count=len(notes),
    )
