import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared import build_s3_client, ensure_bucket_exists

from app.api.healthcheck import router as healthcheck_router
from app.api.midi_generate import router as generate_router
from app.config.app import settings


logger = logging.getLogger(__name__)

s3_client = build_s3_client(
    region_name=settings.aws_region,
    endpoint_url=settings.s3_endpoint_url,
    access_key=settings.s3_access_key,
    secret_key=settings.s3_secret_key,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_bucket_exists(s3_client, settings.s3_bucket)
    yield

app = FastAPI(
    title="MIDI Generator",
    description=(
        "REST API that generates MIDI tracks from natural-language descriptions. "
        "Generations are persisted in PostgreSQL and the .mid files are stored in S3-compatible storage."
    ),
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(healthcheck_router)
app.include_router(generate_router)