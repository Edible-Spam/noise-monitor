"""
Microphone interface for the ICS-43434.

Uses FFmpeg to capture raw PCM from ALSA and returns
mono NumPy arrays.
"""

from __future__ import annotations

import subprocess
import numpy as np


class Microphone:
    """Capture audio from the ICS-43434."""

    def __init__(self) -> None:

        self.sample_rate = 48000
        self.channels = 2
        self.bytes_per_sample = 4          # S32_LE
        self.frames_per_read = 1024

        self.process: subprocess.Popen | None = None

    def start(self) -> None:

        command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",

            "-f", "alsa",
            "-ac", "2",
            "-ar", "48000",
            "-i", "hw:CARD=ICS43434,DEV=0",

            "-f", "s32le",
            "-"
        ]

        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )

        print("Microphone started.\n")

    def read(self) -> np.ndarray:

        if self.process is None or self.process.stdout is None:
            raise RuntimeError("Microphone has not been started.")

        bytes_to_read = (
            self.frames_per_read *
            self.channels *
            self.bytes_per_sample
        )

        data = self.process.stdout.read(bytes_to_read)

        if len(data) != bytes_to_read:
            return np.array([], dtype=np.float32)

        samples = np.frombuffer(
            data,
            dtype=np.int32,
        ).reshape(-1, 2)

        # Left channel only
        mono = samples[:, 0]

        return mono.astype(np.float32) / 2147483648.0

    def stop(self) -> None:

        if self.process is not None:

            self.process.terminate()

            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()

            self.process = None
