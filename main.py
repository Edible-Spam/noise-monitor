"""Command-line entry point for NoiseMonitor."""

from __future__ import annotations

import argparse
from pathlib import Path

from dashboard import serve
from monitor import run_monitor
from processing.analyse import analyse_audio
from processing.audio import load_audio, remove_dc, select_microphone_channel


def analyse_file(filename: Path) -> None:
    sample_rate, samples = load_audio(filename)
    results = analyse_audio(remove_dc(select_microphone_channel(samples)), sample_rate, include_partial=True)
    print(f"Analysed {filename} at {sample_rate} Hz\n")
    print(f"{'Time':>6} {'RMS':>10} {'Peak':>10} {'Freq':>10} {'Centre':>10}")
    print("-" * 52)
    for frame in results:
        print(f"{frame.second:6d} {frame.rms:10.6f} {frame.peak:10.6f} {frame.dominant_frequency:10.1f} {frame.spectral_centroid:10.1f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Raspberry Pi environmental noise monitor")
    commands = parser.add_subparsers(dest="command")
    analyse = commands.add_parser("analyse", help="analyse a WAV file")
    analyse.add_argument("file", type=Path, help="WAV file to analyse")
    monitor = commands.add_parser("monitor", help="capture continuously from the I2S microphone")
    monitor.add_argument("--threshold", type=float, default=None, help="event RMS threshold")
    web = commands.add_parser("dashboard", help="serve the local dashboard")
    web.add_argument("--host", default="0.0.0.0")
    web.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    if args.command == "analyse":
        analyse_file(args.file)
    elif args.command == "monitor":
        run_monitor(**({"threshold": args.threshold} if args.threshold is not None else {}))
    elif args.command == "dashboard":
        serve(args.host, args.port)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
