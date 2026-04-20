# MIDI Generator

REST API that generates MIDI tracks from natural-language descriptions. Built with FastAPI and Claude API.

## Features

- Generate melodies, basslines, chord progressions, and drum patterns
- Describe with words + structured parameters (key, BPM, bars)
- Returns standard `.mid` files ready for Ableton or any DAW
- Interactive Swagger UI at `/docs`

## Stack

Python 3.12 · FastAPI · Anthropic SDK · mido · dynaconf · Docker

## Configuration

Configuration uses **dynaconf** with two TOML files:

- `settings.toml` — committed, non-sensitive defaults per environment
- `.secrets.toml` — **not committed**, holds the API key

Environment is selected via `MIDIGEN_ENV` (default: `development`).

### First-time setup

1. Copy the secrets template and add your Anthropic API key:
   ```bash
   cp .secrets.toml.example .secrets.toml
   ```
   Edit `.secrets.toml` and paste your key from https://console.anthropic.com

2. Start the service:
   ```bash
   docker compose up --build
   ```

3. Open the interactive docs:
   ```
   http://localhost:8000/docs
   ```

## Endpoints

- `GET /health` — health check
- `POST /generate` — generate and download a `.mid` file
- `POST /preview` — return metadata only (useful for prompt testing)

## Example

Request body for `/generate`:

```json
{
  "description": "melancholic minimal techno groove with slight swing",
  "track_type": "bassline",
  "key": "A minor",
  "bpm": 128,
  "bars": 4
}
```

Response: binary `.mid` file attachment.

## Environments

Switch environment via env var:

```bash
ENV=qa docker compose up
```

Values in `[dev]`, `[qa]`, `[prod]` override `[default]` in `settings.toml`.

## Roadmap

- Stage 2: Persistence (RDS + S3) — save and browse generated tracks
- Stage 3: Web UI (React + CloudFront)
- Stage 4: Deploy to AWS ECS with Terraform
