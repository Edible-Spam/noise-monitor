"""
NoiseMonitor v0.4
"""

from config import SAMPLE_FILE

from processing.audio import (
    load_audio,
    select_microphone_channel,
    remove_dc,
)

from processing.analyse import analyse_audio


def main():

    print()

    print("NoiseMonitor v0.4")

    print()

    sample_rate, samples = load_audio(SAMPLE_FILE)

    samples = select_microphone_channel(samples)

    samples = remove_dc(samples)

    results = analyse_audio(
        samples,
        sample_rate,
    )

    print()

    print(
        f"{'Time':>6} "
        f"{'RMS':>10} "
        f"{'Peak':>10} "
        f"{'Freq':>10} "
        f"{'Centre':>10}"
    )

    print("-" * 42)

    for frame in results:

        print(
            f"{frame.second:6d} "
            f"{frame.rms:10.6f} "
            f"{frame.peak:10.6f} "
            f"{frame.dominant_frequency:10.1f} "
            f"{frame.spectral_centroid:10.1f}"
        )


if __name__ == "__main__":
    main()
