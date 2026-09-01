"""
Microphone interface for the ICS-43434.

Uses FFmpeg to capture raw PCM from ALSA and returns
mono NumPy arrays.
"""

from __future__ import annotations

import subprocess
import time
import os
import select
import numpy as np

from config import MICROPHONE_DEVICE, MICROPHONE_STARTUP_SECONDS, SAMPLE_RATE


class Microphone:
    """Capture audio from the ICS-43434."""

    def __init__(self, channel: str | int = "auto") -> None:

        self.sample_rate = SAMPLE_RATE
        self.channels = 2
        self.bytes_per_sample = 4          # S32_LE
        self.frames_per_read = 1024

        # channel can be 'auto', 'left', 'right', 'mix', or an int (0 or 1)
        self.channel: str | int = channel

        # internal: selected channel index (0 or 1) when applicable
        self._channel_index: int | None = None
        # prefetched mono samples (float32) from initial detection
        self._prefetched: np.ndarray = np.array([], dtype=np.float32)
        self._prefetch_pos: int = 0

        self.process: subprocess.Popen | None = None

    def start(self) -> None:

        if self.process is not None:
            return

        command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",

            "-f", "alsa",
            "-ac", "2",
            "-ar", str(self.sample_rate),
            "-i", MICROPHONE_DEVICE,

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

        # The I2S/ALSA pipeline may report an empty first buffer while it is
        # still settling.  Wait before channel auto-detection so we preserve
        # and analyse a real initial block.
        time.sleep(MICROPHONE_STARTUP_SECONDS)

        # If auto-detection is requested, read a short burst and pick the
        # channel with higher RMS energy. We store those prefetched samples
        # so the first calls to `read()` return continuous data.
        if isinstance(self.channel, str) and self.channel == "auto":

            detect_frames = self.frames_per_read * 8
            bytes_to_read = detect_frames * self.channels * self.bytes_per_sample

            if self.process.stdout is None:
                return

            data = self._read_raw_bytes(detect_frames, timeout=10.0)

            if len(data) == bytes_to_read:
                samples = np.frombuffer(data, dtype=np.int32).reshape(-1, 2)

                left = samples[:, 0].astype(np.float64)
                right = samples[:, 1].astype(np.float64)

                # RMS energy per channel
                left_rms = np.sqrt(np.mean(left * left))
                right_rms = np.sqrt(np.mean(right * right))

                if left_rms >= right_rms:
                    self._channel_index = 0
                else:
                    self._channel_index = 1

                mono = samples[:, self._channel_index]
                self._prefetched = mono.astype(np.float32) / 2147483648.0
                self._prefetch_pos = 0

                chosen = "left" if self._channel_index == 0 else "right"
                print(f"Auto-detected channel: {chosen}\n")

        # If channel was explicitly set to left/right as a string, set internal index
        elif isinstance(self.channel, str) and self.channel in ("left", "right"):
            self._channel_index = 0 if self.channel == "left" else 1

        # If user provided numeric channel (0/1)
        elif isinstance(self.channel, int) and self.channel in (0, 1):
            self._channel_index = int(self.channel)

    def read(self) -> np.ndarray:

        if self.process is None or self.process.stdout is None:
            raise RuntimeError("Microphone has not been started.")

        bytes_to_read = (
            self.frames_per_read *
            self.channels *
            self.bytes_per_sample
        )

        # If we have prefetched samples from auto-detection, serve them first.
        if self._prefetch_pos < self._prefetched.size:
            remaining = self._prefetched.size - self._prefetch_pos
            need = self.frames_per_read

            if remaining >= need:
                out = self._prefetched[self._prefetch_pos:self._prefetch_pos + need]
                self._prefetch_pos += need
                return out
            else:
                # return what's left and then read the remainder from the stream
                out_parts = [self._prefetched[self._prefetch_pos:]]
                to_read_frames = need - remaining
                to_read_bytes = to_read_frames * self.channels * self.bytes_per_sample

                data = self.process.stdout.read(to_read_bytes)

                if len(data) != to_read_bytes:
                    # return whatever is left
                    self._prefetch_pos = self._prefetched.size
                    return out_parts[0]

                samples = np.frombuffer(data, dtype=np.int32).reshape(-1, 2)
                mono_new = self._select_mono_from_samples(samples)
                out_parts.append(mono_new)

                self._prefetch_pos = self._prefetched.size
                return np.concatenate(out_parts)

        # Normal read path when no prefetched data remains
        data = self._read_raw_bytes(self.frames_per_read)

        if len(data) != bytes_to_read:
            return np.array([], dtype=np.float32)

        samples = np.frombuffer(data, dtype=np.int32).reshape(-1, 2)

        mono = self._select_mono_from_samples(samples)

        return mono

    def _read_raw_bytes(self, frame_count: int, timeout: float = 1.0) -> bytes:
        """Read a complete raw-audio buffer, waiting for FFmpeg to produce it."""
        if self.process is None or self.process.stdout is None:
            return b""

        expected = frame_count * self.channels * self.bytes_per_sample
        data = bytearray()
        deadline = time.monotonic() + timeout

        while len(data) < expected:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            ready, _, _ = select.select([self.process.stdout], [], [], remaining)
            if not ready:
                break
            chunk = os.read(self.process.stdout.fileno(), expected - len(data))
            if chunk:
                data.extend(chunk)
            elif self.process.poll() is not None:
                break
            else:
                time.sleep(0.01)

        return bytes(data)

    def _select_mono_from_samples(self, samples: np.ndarray) -> np.ndarray:
        """Return a float32 mono array (length == frames_per_read) from raw int32 stereo samples."""
        # If user asked for mix, average both channels
        if isinstance(self.channel, str) and self.channel == "mix":
            mono = samples.mean(axis=1)
        else:
            # Use detected/indexed channel if present, otherwise default to left
            idx = 0 if self._channel_index is None else self._channel_index
            mono = samples[:, idx]

        return mono.astype(np.float32) / 2147483648.0

    def stop(self) -> None:

        if self.process is not None:

            self.process.terminate()

            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()

            self.process = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.stop()
