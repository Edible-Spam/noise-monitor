"""
Analyse audio in one-second windows.
"""

from __future__ import annotations

from models.audio_frame import AudioFrame

from processing.audio import rms, peak
from processing.fft import analyse_spectrum

def analyse_audio(samples, sample_rate):

    results = []

    block_size = sample_rate

    total_blocks = len(samples) // block_size

    for second in range(total_blocks):

        start = second * block_size
        end = start + block_size

        block = samples[start:end]

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
		)
        )

    return results
