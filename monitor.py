"""Continuous microphone monitoring orchestration."""

from __future__ import annotations

from datetime import datetime, timezone
import time

import numpy as np

from config import DATABASE_FILE, EVENT_COOLDOWN_SECONDS, EVENT_DIRECTORY, EVENT_RMS_THRESHOLD, FRAME_SECONDS, SAMPLE_RATE
from database.database import NoiseDatabase
from processing.analyse import analyse_audio
from processing.recording import save_event_recording
from sensors.microphone import Microphone


def run_monitor(*, threshold: float = EVENT_RMS_THRESHOLD) -> None:
    """Capture, analyse, persist and optionally record one-second noise events.

    Stop cleanly with Ctrl+C.  This command must be run on the Raspberry Pi
    with FFmpeg and its ALSA microphone configured.
    """
    microphone = Microphone()
    chunks: list[np.ndarray] = []
    samples_needed = int(SAMPLE_RATE * FRAME_SECONDS)
    last_event = 0.0

    print(f"Monitoring started (event RMS threshold: {threshold:.3f}). Ctrl+C to stop.")
    try:
        with microphone, NoiseDatabase(DATABASE_FILE) as database:
            while True:
                chunk = microphone.read()
                if not len(chunk):
                    continue
                chunks.append(chunk)
                available = sum(len(part) for part in chunks)
                if available < samples_needed:
                    continue

                block = np.concatenate(chunks)
                current, remainder = block[:samples_needed], block[samples_needed:]
                chunks = [remainder] if len(remainder) else []
                frame = analyse_audio(current, SAMPLE_RATE, start_time=datetime.now(timezone.utc))[0]
                database.add_frame(frame)
                print(f"RMS {frame.rms:.4f} | peak {frame.peak:.4f} | {frame.dominant_frequency:.0f} Hz")

                if frame.rms >= threshold and time.monotonic() - last_event >= EVENT_COOLDOWN_SECONDS:
                    recording = save_event_recording(current, SAMPLE_RATE, EVENT_DIRECTORY)
                    database.add_event(frame.rms, recording)
                    last_event = time.monotonic()
                    print(f"Event recording saved: {recording}")
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
