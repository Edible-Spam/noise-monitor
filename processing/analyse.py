"""
Analyse audio in one-second windows.
"""

from __future__ import annotations

from models.audio_frame import AudioFrame

from processing.audio import rms, peak
from processing.fft import dominant_frequency


def analyse_audio(samples, sample_rate):

    results = []

    block_size = sample_rate

    total_blocks = len(samples) // block_size

    for second in range(total_blocks):

        start = second * block_size
        end = start + block_size

        block = samples[start:end]

        dominant, _, _ = dominant_frequency(
            block,
            sample_rate,
        )

        results.append(
		AudioFrame(
			second=second,
			rms=rms(block),
			peak=peak(block),
			dominant_frequency=dominant,
		)
        )

    return results
