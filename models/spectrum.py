"""
Frequency-domain analysis results.
"""

from dataclasses import dataclass
import numpy as np


@dataclass(slots=True)
class Spectrum:
    dominant_frequency: float
    spectral_centroid: float

    frequencies: np.ndarray
    magnitudes: np.ndarray
