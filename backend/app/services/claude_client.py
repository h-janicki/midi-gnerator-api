import json
import logging
from anthropic import Anthropic

from app.config.app import settings
from app.schemas import GenerateRequest, Note


logger = logging.getLogger(__name__)

client = Anthropic(api_key=settings.anthropic_api_key)


SYSTEM_PROMPT = """You are an expert music composer. You generate MIDI note sequences based on user descriptions.

Rules:
- Return ONLY valid JSON - no prose, no markdown, no code fences.
- Output format: {"notes": [{"pitch": int, "start": float, "duration": float, "velocity": int}, ...]}
- pitch: MIDI note number (0-127). Middle C = 60.
- start: beat position from the start (e.g., 0.0, 0.5, 1.0, 1.5)
- duration: length in beats (e.g., 0.25 = 16th note, 0.5 = 8th, 1.0 = quarter)
- velocity: 1-127. Use dynamics - accents higher, ghost notes lower.

Music theory:
- Respect the requested key and typical genre conventions.
- For melodies: singable contour, use tension and resolution.
- For basslines: emphasize root and fifth, groove with rhythm.
- For chords: use appropriate voicings (triads, 7ths) matching the mood.
- For drums: use General MIDI drum map (36=kick, 38=snare, 42=closed hat, 46=open hat, 49=crash).

Respond with JSON only."""


def build_user_prompt(req: GenerateRequest) -> str:
    total_beats = req.bars * 4
    return (
        f"Generate a {req.track_type.value} for {req.bars} bars in 4/4 time "
        f"(= {total_beats} beats total).\n"
        f"Key: {req.key.value}\n"
        f"BPM: {req.bpm}\n"
        f"Description: {req.description}\n\n"
        f"Return JSON with notes array."
    )


def generate_notes(req: GenerateRequest) -> list[Note]:
    if not settings.anthropic_api_key or settings.anthropic_api_key.startswith("sk-ant-your"):
        raise ValueError("ANTHROPIC_API_KEY is not set. Add it to .secrets.toml.")

    message = client.messages.create(
        model=settings.claude_model,
        max_tokens=settings.max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(req)}],
    )

    raw = message.content[0].text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error("Claude returned invalid JSON: %s", raw[:200])
        raise ValueError(f"Claude returned invalid JSON: {e}")

    notes_raw = data.get("notes", [])
    if not notes_raw:
        raise ValueError("No notes in response")

    return [Note(**n) for n in notes_raw]
