"""WAV event-recording support."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import wave

import numpy as np


def save_event_recording(samples: np.ndarray, sample_rate: int, directory: Path) -> Path:
    """Write a mono 32-bit PCM WAV file and return its path."""
    directory.mkdir(parents=True, exist_ok=True)
    name = datetime.now(timezone.utc).strftime("event-%Y%m%dT%H%M%SZ.wav")
    filename = directory / name
    pcm = (np.clip(samples, -1, 1) * 2147483647).astype("<i4")
    with wave.open(str(filename), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(4)
        output.setframerate(sample_rate)
        output.writeframes(pcm.tobytes())
    return filename
