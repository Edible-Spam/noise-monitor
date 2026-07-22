"""
FFT processing.
"""

from __future__ import annotations

import numpy as np


MIN_FREQUENCY = 20.0
MAX_FREQUENCY = 5000.0


def dominant_frequency(samples, sample_rate):

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

    valid_freq = frequency[valid]
    valid_mag = magnitude[valid]

    peak = np.argmax(valid_mag)

    return (
        float(valid_freq[peak]),
        valid_freq,
        valid_mag,
    )
