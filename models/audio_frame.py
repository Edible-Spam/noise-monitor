"""
Represents one second of analysed audio.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class AudioFrame:
    second: int

    rms: float
    peak: float

    dominant_frequency: float
