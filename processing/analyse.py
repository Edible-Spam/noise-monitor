"""
Analyse audio in one-second windows.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from models.audio_frame import AudioFrame

from processing.audio import rms, peak
from processing.fft import analyse_spectrum

def analyse_audio(samples, sample_rate, *, include_partial=False, start_time=None):
    """Analyse audio in fixed one-second frames.

    ``start_time`` is used for persisted/live frames; offline analysis leaves it
    unset by default so it remains reproducible.
    """

    results = []

    block_size = sample_rate

    total_blocks = len(samples) // block_size
    if include_partial and len(samples) % block_size:
        total_blocks += 1

    for second in range(total_blocks):

        start = second * block_size
        end = start + block_size

        block = samples[start:end]
        if not len(block):
            continue

        spectrum = analyse_spectrum(
            block,
            sample_rate,
        )

        results.append(
            AudioFrame(
                second=second,
                rms=rms(block),
                peak=peak(block),
                dominant_frequency=spectrum.dominant_frequency,
                spectral_centroid=spectrum.spectral_centroid,
                recorded_at=(start_time + timedelta(seconds=second)) if start_time else None,
            )
        )

    return results
