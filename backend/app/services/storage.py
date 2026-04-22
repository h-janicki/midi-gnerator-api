import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from dynaconf import Dynaconf
from fastapi import Request


logger = logging.getLogger(__name__)


class StorageService:

    def __init__(self, s3_client: Any, settings: Dynaconf) -> None:
        self.s3_client = s3_client
        self.settings = settings

    @staticmethod
    def build_s3_key(generation_id: UUID) -> str:
        """Organize files by year/month to keep bucket browsable."""
        now = datetime.now(timezone.utc)
        return f"generations/{now.year}/{now.month:02d}/{generation_id}.mid"


    def upload_midi(self, s3_key: str, midi_bytes: bytes) -> None:
        self.s3_client.put_object(
            Bucket=self.settings.s3_bucket,
            Key=s3_key,
            Body=midi_bytes,
            ContentType="audio/midi",
        )
        logger.info("Uploaded MIDI to s3://%s/%s", self.settings.s3_bucket, s3_key)


    def download_midi(self, s3_key: str) -> bytes:
        response = self.s3_client.get_object(Bucket=self.settings.s3_bucket, Key=s3_key)
        return response["Body"].read()


    def delete_midi(self, s3_key: str) -> None:
        self.s3_client.delete_object(Bucket=self.settings.s3_bucket, Key=s3_key)
        logger.info("Deleted s3://%s/%s", self.settings.s3_bucket, s3_key)


def get_storage(request: Request) -> StorageService:
    return request.app.state.storage