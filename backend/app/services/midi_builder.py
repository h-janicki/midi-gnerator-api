import io
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo

from app.schemas import Note

TICKS_PER_BEAT = 480


def notes_to_midi(notes: list[Note], bpm: int) -> bytes:
    """Convert a list of notes into a MIDI file (returns bytes). Single track, channel 0."""
    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage("set_tempo", tempo=bpm2tempo(bpm), time=0))

    events = []
    for n in notes:
        start_tick = int(round(n.start * TICKS_PER_BEAT))
        end_tick = int(round((n.start + n.duration) * TICKS_PER_BEAT))
        events.append((start_tick, "on", n.pitch, n.velocity))
        events.append((end_tick, "off", n.pitch, 0))

    events.sort(key=lambda e: (e[0], 0 if e[1] == "off" else 1))

    last_tick = 0
    for tick, kind, pitch, velocity in events:
        delta = tick - last_tick
        last_tick = tick
        if kind == "on":
            track.append(Message("note_on", note=pitch, velocity=velocity, time=delta))
        else:
            track.append(Message("note_off", note=pitch, velocity=0, time=delta))

    buf = io.BytesIO()
    mid.save(file=buf)
    return buf.getvalue()
