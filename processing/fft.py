"""
Spectrum analysis.
"""

from __future__ import annotations

import numpy as np

from models.spectrum import Spectrum


MIN_FREQUENCY = 20.0
MAX_FREQUENCY = 5000.0


def analyse_spectrum(samples, sample_rate) -> Spectrum:

    window = np.hanning(len(samples))

    samples = samples * window

    fft = np.fft.rfft(samples)

    magnitude = np.abs(fft)

    frequency = np.fft.rfftfreq(
        len(samples),
        d=1 / sample_rate,
    )

    valid = (
        (frequency >= MIN_FREQUENCY)
        &
        (frequency <= MAX_FREQUENCY)
    )

    frequency = frequency[valid]
    magnitude = magnitude[valid]

    peak = np.argmax(magnitude)

    dominant = float(frequency[peak])

    # Spectral centroid
    centroid = float(
        np.sum(frequency * magnitude)
        /
        np.sum(magnitude)
    )

    return Spectrum(
        dominant_frequency=dominant,
        spectral_centroid=centroid,
        frequencies=frequency,
        magnitudes=magnitude,
    )
