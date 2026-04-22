import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class Generation(Base):
    __tablename__ = "midi_generations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(String(500), nullable=False)
    track_type: Mapped[str] = mapped_column(String(20), nullable=False)
    key: Mapped[str] = mapped_column(String(20), nullable=False)
    bpm: Mapped[int] = mapped_column(Integer, nullable=False)
    bars: Mapped[int] = mapped_column(Integer, nullable=False)

    note_count: Mapped[int] = mapped_column(Integer, nullable=False)
    s3_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
