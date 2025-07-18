from __future__ import annotations

"""Text-to-speech wrapper for Suno's Bark."""

import tempfile
from pathlib import Path

import numpy as np

from .utils import save_wav
from . import fallback_tts
from .voice_evolution import get_voice_params

try:  # pragma: no cover - optional dependency
    from bark import generate_audio, preload_models
    preload_models()
except Exception:  # pragma: no cover - optional dependency
    generate_audio = None  # type: ignore


def synthesize(text: str, emotion: str) -> str:
    """Return a WAV path containing ``text`` spoken in ``emotion`` style."""
    style = get_voice_params(emotion)
    out_path = Path(tempfile.gettempdir()) / f"bark_{abs(hash(text))}.wav"

    if generate_audio is not None:
        try:  # pragma: no cover - external library
            wave = generate_audio(text)
            save_wav(wave.astype(np.float32), str(out_path), sr=22050)
        except Exception:  # pragma: no cover - fallback
            out_path = Path(fallback_tts.speak(text, style.get("pitch", 0.0), style.get("speed", 1.0)))
    else:  # pragma: no cover - optional dependency missing
        out_path = Path(fallback_tts.speak(text, style.get("pitch", 0.0), style.get("speed", 1.0)))

    return str(out_path)


__all__ = ["synthesize"]
