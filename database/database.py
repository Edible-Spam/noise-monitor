"""SQLite storage for analysed frames and noise events."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from models.audio_frame import AudioFrame


class NoiseDatabase:
    def __init__(self, filename: Path | str) -> None:
        self.connection = sqlite3.connect(filename)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
        self._create_schema()

    def _create_schema(self) -> None:
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS frames (
                id INTEGER PRIMARY KEY,
                recorded_at TEXT NOT NULL,
                rms REAL NOT NULL,
                peak REAL NOT NULL,
                dominant_frequency REAL NOT NULL,
                spectral_centroid REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS frames_recorded_at ON frames(recorded_at);
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                recorded_at TEXT NOT NULL,
                rms REAL NOT NULL,
                recording_path TEXT
            );
        """)
        self.connection.commit()

    def add_frame(self, frame: AudioFrame) -> None:
        timestamp = frame.recorded_at or datetime.now(timezone.utc)
        self.connection.execute(
            "INSERT INTO frames VALUES (NULL, ?, ?, ?, ?, ?)",
            (timestamp.isoformat(), frame.rms, frame.peak, frame.dominant_frequency, frame.spectral_centroid),
        )
        self.connection.commit()

    def add_event(self, rms: float, recording_path: Path | None = None) -> None:
        self.connection.execute(
            "INSERT INTO events VALUES (NULL, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), rms, str(recording_path) if recording_path else None),
        )
        self.connection.commit()

    def recent_frames(self, limit: int = 60) -> list[dict]:
        rows = self.connection.execute(
            "SELECT recorded_at, rms, peak, dominant_frequency, spectral_centroid "
            "FROM frames ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def close(self) -> None:
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()
