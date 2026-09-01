"""
Global configuration for NoiseMonitor.
"""

from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parent

# Audio
SAMPLE_FILE = BASE_DIR / "sample.wav"
SAMPLE_RATE = 48_000
FRAME_SECONDS = 1.0
# ``plughw`` lets ALSA convert the microphone's native format for FFmpeg.
# Use ``arecord -l`` on the Pi if the card identifier differs.
MICROPHONE_DEVICE = "plughw:CARD=ICS43434,DEV=0"
# ALSA/FFmpeg needs a short period before its first buffer is available.
MICROPHONE_STARTUP_SECONDS = 5.0

# Monitoring
EVENT_RMS_THRESHOLD = 0.10
EVENT_COOLDOWN_SECONDS = 10.0
EVENT_DIRECTORY = BASE_DIR / "recordings"

# Output
OUTPUT_DIR = BASE_DIR / "output"
DATABASE_FILE = BASE_DIR / "noise_monitor.sqlite3"

OUTPUT_DIR.mkdir(exist_ok=True)
EVENT_DIRECTORY.mkdir(exist_ok=True)
