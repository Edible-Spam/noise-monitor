"""
Global configuration for NoiseMonitor.
"""

from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parent

# Audio
SAMPLE_FILE = BASE_DIR / "sample.wav"

# Output
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)
