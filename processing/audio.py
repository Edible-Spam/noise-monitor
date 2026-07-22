"""
Basic audio utilities.
"""

from __future__ import annotations

import numpy as np
import soundfile as sf


def load_audio(filename):
    """
    Load a WAV file.

    Returns
    -------
    sample_rate
    samples
    """

    samples, sample_rate = sf.read(filename)

    return sample_rate, samples


def select_microphone_channel(samples):

    if samples.ndim == 1:
        print("Mono recording detected.")
        return samples

    left = samples[:, 0]
    right = samples[:, 1]

    left_energy = np.mean(left ** 2)
    right_energy = np.mean(right ** 2)

    if right_energy > left_energy:
        print("Using RIGHT channel.")
        return right

    print("Using LEFT channel.")
    return left


def remove_dc(samples):

    return samples - np.mean(samples)


def rms(samples):

    return float(np.sqrt(np.mean(samples ** 2)))


def peak(samples):

    return float(np.max(np.abs(samples)))
