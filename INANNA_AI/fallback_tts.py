from __future__ import annotations

"""Minimal text-to-speech helper using :mod:`pyttsx3`."""

import logging
import tempfile
from pathlib import Path

import numpy as np

from .utils import save_wav

try:  # pragma: no cover - optional dependency
    import pyttsx3  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pyttsx3 = None

logger = logging.getLogger(__name__)


def _sine_wave(text: str, path: Path, pitch: float) -> None:
    """Fallback sine wave when :mod:`pyttsx3` is unavailable."""
    duration = max(1.0, len(text) / 20)
    sr = 22050
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    freq = 220 * (1 + pitch * 0.1)
    wave = 0.1 * np.sin(2 * np.pi * freq * t)
    save_wav(wave.astype(np.float32), str(path), sr=sr)


def speak(text: str, pitch: float = 0.0, speed: float = 1.0) -> str:
    """Synthesize ``text`` to a temporary WAV file and return its path."""
    out_path = Path(tempfile.gettempdir()) / f"fallback_{abs(hash(text))}.wav"

    if pyttsx3 is None:
        logger.warning("pyttsx3 not installed; using sine fallback")
        _sine_wave(text, out_path, pitch)
        return str(out_path)

    try:  # pragma: no cover - external library
        engine = pyttsx3.init()
        try:
            base_rate = engine.getProperty("rate")
            engine.setProperty("rate", int(base_rate * speed))
        except Exception:
            pass
        try:
            engine.setProperty("pitch", int(50 + pitch * 10))
        except Exception:
            pass
        engine.save_to_file(text, str(out_path))
        engine.runAndWait()
    except Exception as exc:  # pragma: no cover - fallback
        logger.warning("pyttsx3 synthesis failed: %s", exc)
        _sine_wave(text, out_path, pitch)

    return str(out_path)


__all__ = ["speak"]
