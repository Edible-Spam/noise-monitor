"""
NoiseMonitor v0.2
"""

from config import SAMPLE_FILE

from processing.audio import (
    load_audio,
    select_microphone_channel,
    remove_dc,
    rms,
    peak,
)


def main():

    print()
    print("NoiseMonitor v0.2")
    print()

    sample_rate, samples = load_audio(SAMPLE_FILE)

    print(f"Sample Rate : {sample_rate:,} Hz")
    print(f"Shape       : {samples.shape}")

    print()

    samples = select_microphone_channel(samples)

    samples = remove_dc(samples)

    print()

    print(f"Duration : {len(samples) / sample_rate:.2f} seconds")

    print(f"RMS       : {rms(samples):.6f}")

    print(f"Peak      : {peak(samples):.6f}")


if __name__ == "__main__":
    main()
