FROM python:3.14-slim AS builder

# Build tools for packages with C extensions (asyncpg, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Virtual environment in a fixed location
# — makes it easy to copy into the next stage
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip

# Install shared separately to cache its dependencies
COPY shared/pyproject.toml /tmp/shared/pyproject.toml
COPY shared/shared /tmp/shared/shared
RUN pip install --no-cache-dir /tmp/shared

# Install backend dependencies
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt


FROM python:3.14-slim AS runtime

# Non-root user
RUN groupadd --system --gid 1000 app \
    && useradd --system --uid 1000 --gid app --create-home app

# Copy the prepared virtualenv from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Application code — copied last, as it changes most frequently
COPY --chown=app:app backend/app /app/app
COPY --chown=app:app backend/alembic /app/alembic
COPY --chown=app:app backend/alembic.ini /app/alembic.ini
COPY --chown=app:app settings.toml /app/settings.toml

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]