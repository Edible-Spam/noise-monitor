"""
Represents one second of analysed audio.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class AudioFrame:
    second: int

    rms: float
    peak: float

    dominant_frequency: float
    spectral_centroid: float
    recorded_at: datetime | None = None
