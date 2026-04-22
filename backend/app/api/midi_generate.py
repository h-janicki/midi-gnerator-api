import logging
import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_db
from app.repositories import GenerationRepository
from app.schemas import GenerateRequest, GenerationResponse, HistoryResponse
from app.services.claude_client import generate_notes
from app.services.midi_builder import notes_to_midi
from app.services.storage import StorageService, get_storage


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generations", tags=["generations"])


@router.post(
    "/generate",
    response_model=GenerationResponse,
    summary="Generate a new MIDI track",
)
async def generate(
    req: GenerateRequest,
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(get_storage),
) -> GenerationResponse:
    """Generate MIDI, upload to S3, persist metadata, return generation info.

    Use GET /generations/{id}/download to fetch the .mid file itself.
    """
    try:
        notes = generate_notes(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    midi_bytes = notes_to_midi(notes, req.bpm)

    generation_id = uuid.uuid4()
    s3_key = storage.build_s3_key(generation_id)

    try:
        storage.upload_midi(s3_key, midi_bytes)
    except Exception:
        logger.exception("S3 upload failed for key %s", s3_key)
        raise HTTPException(status_code=500, detail="Storage failure")

    repo = GenerationRepository(db)
    try:
        generation = await repo.create(req, len(notes), s3_key)
    except Exception:
        logger.exception("DB insert failed, rolling back S3 upload for %s", s3_key)
        try:
            storage.delete_midi(s3_key)
        except Exception:
            logger.exception("Rollback S3 delete also failed for %s", s3_key)
        raise HTTPException(status_code=500, detail="Database failure")

    return generation


@router.get(
    "",
    response_model=HistoryResponse,
    summary="List past generations (paginated)",
)
async def list_generations(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    favorites_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
) -> HistoryResponse:
    repo = GenerationRepository(db)
    items, total = await repo.list(
        limit=limit, offset=offset, favorites_only=favorites_only
    )
    return HistoryResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=items,
    )


@router.get(
    "/{generation_id}",
    response_model=GenerationResponse,
    summary="Get generation metadata",
)
async def get_generation(
    generation_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> GenerationResponse:
    repo = GenerationRepository(db)
    generation = await repo.get(generation_id)
    if generation is None:
        raise HTTPException(status_code=404, detail="Generation not found")
    return generation


@router.get(
    "/{generation_id}/download",
    summary="Download the .mid file for a generation",
    response_class=Response,
)
async def download_generation(
    generation_id: UUID,
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(get_storage),
) -> Response:
    repo = GenerationRepository(db)
    generation = await repo.get(generation_id)
    if generation is None:
        raise HTTPException(status_code=404, detail="Generation not found")

    try:
        midi_bytes = storage.download_midi(generation.s3_key)
    except Exception:
        logger.exception("S3 download failed for %s", generation.s3_key)
        raise HTTPException(status_code=500, detail="Storage failure")

    key_slug = generation.key.replace(" ", "_").replace("#", "sharp")
    filename = f"{generation.track_type}_{key_slug}_{generation.bpm}bpm.mid"

    return Response(
        content=midi_bytes,
        media_type="audio/midi",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/{generation_id}/favorite",
    response_model=GenerationResponse,
    summary="Mark or unmark as favorite",
)
async def toggle_favorite(
    generation_id: UUID,
    is_favorite: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
) -> GenerationResponse:
    repo = GenerationRepository(db)
    generation = await repo.set_favorite(generation_id, is_favorite)
    if generation is None:
        raise HTTPException(status_code=404, detail="Generation not found")
    return generation


@router.delete(
    "/{generation_id}",
    status_code=204,
    summary="Delete a generation and its .mid file",
)
async def delete_generation(
    generation_id: UUID,
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(get_storage),
) -> None:
    repo = GenerationRepository(db)
    generation = await repo.get(generation_id)
    if generation is None:
        raise HTTPException(status_code=404, detail="Generation not found")

    try:
        storage.delete_midi(generation.s3_key)
    except Exception:
        logger.exception(
            "Failed to delete %s from S3, continuing with DB delete",
            generation.s3_key,
        )

    await repo.delete(generation_id)