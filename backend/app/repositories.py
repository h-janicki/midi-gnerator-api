from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Generation
from app.schemas import GenerateRequest


class GenerationRepository:
    """Database operations for generations. Keeps SQL out of endpoints."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        request: GenerateRequest,
        note_count: int,
        s3_key: str,
    ) -> Generation:
        generation = Generation(
            description=request.description,
            track_type=request.track_type.value,
            key=request.key.value,
            bpm=request.bpm,
            bars=request.bars,
            note_count=note_count,
            s3_key=s3_key,
        )
        self.session.add(generation)
        await self.session.commit()
        await self.session.refresh(generation)
        return generation

    async def get(self, generation_id: UUID) -> Generation | None:
        result = await self.session.execute(
            select(Generation).where(Generation.id == generation_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        limit: int,
        offset: int,
        favorites_only: bool = False,
    ) -> tuple[Sequence[Any], int]:
        query = select(Generation).order_by(Generation.created_at.desc())
        count_query = select(func.count()).select_from(Generation)

        if favorites_only:
            query = query.where(Generation.is_favorite.is_(True))
            count_query = count_query.where(Generation.is_favorite.is_(True))

        query = query.limit(limit).offset(offset)

        items_result = await self.session.execute(query)
        total_result = await self.session.execute(count_query)

        return items_result.scalars().all(), total_result.scalar_one()

    async def set_favorite(self, generation_id: UUID, is_favorite: bool) -> Generation | None:
        generation = await self.get(generation_id)
        if generation is None:
            return None
        generation.is_favorite = is_favorite
        await self.session.commit()
        await self.session.refresh(generation)
        return generation

    async def delete(self, generation_id: UUID) -> Generation | None:
        generation = await self.get(generation_id)
        if generation is None:
            return None
        await self.session.delete(generation)
        await self.session.commit()
        return generation
