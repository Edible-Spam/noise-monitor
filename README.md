# Noise Monitor

Raspberry Pi based environmental noise monitor. It can analyse WAV files on a
development machine or continuously capture an ICS-43434 I2S microphone on the
Pi. Measurements are stored in SQLite and exposed through a small local web
dashboard.

## Hardware

- Raspberry Pi 3B+
- ICS-43434 I2S MEMS Microphone
- MPU-6050 (planned)

## Features

- Continuous monitoring
- RMS
- Peak
- FFT
- SQLite logging
- Event recordings
- Web dashboard

## Installation

On the Raspberry Pi, install the system audio dependency then the Python
packages:

```bash
sudo apt install ffmpeg libsndfile1 python3-pip
python3 -m pip install -r requirements.txt
```

The microphone capture command expects ALSA device
`hw:CARD=ICS43434,DEV=0`. Change that identifier in `sensors/microphone.py` if
your card has another name.

## Usage

```bash
# Analyse an existing WAV
python3 main.py analyse path/to/recording.wav

# Continuous capture; Ctrl+C stops safely
python3 main.py monitor --threshold 0.10

# In another terminal, visit http://raspberrypi.local:8080
python3 main.py dashboard
```

Each one-second frame records RMS, peak, dominant frequency, and spectral
centroid in `noise_monitor.sqlite3`. Frames above the configured RMS threshold
are saved as WAV files in `recordings/`, subject to a ten-second cooldown.
