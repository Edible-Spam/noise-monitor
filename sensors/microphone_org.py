"""
ICS-43434 microphone interface using ALSA.
"""

from __future__ import annotations

import alsaaudio
import numpy as np


class Microphone:

    def __init__(self):

        self.device = alsaaudio.PCM(
            type=alsaaudio.PCM_CAPTURE,
            mode=alsaaudio.PCM_NORMAL,
            device="hw:CARD=ICS43434,DEV=0",
        )

        self.device.setchannels(2)
        self.device.setrate(48000)
        self.device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
        self.device.setperiodsize(1024)

    def read(self) -> np.ndarray:

        length, data = self.device.read()

        if length == 0:
            return np.array([], dtype=np.float32)

        samples = np.frombuffer(data, dtype=np.int32)

        # Stereo -> (N,2)
        samples = samples.reshape(-1, 2)

        # Left channel only
        left = samples[:, 0]

        # Convert to float
        return left.astype(np.float32) / 2147483648.0
