from __future__ import annotations

"""Text-to-speech wrapper for the XTTS model from Coqui TTS."""

import tempfile
from pathlib import Path

import numpy as np

from .utils import save_wav
from . import fallback_tts
from .voice_evolution import get_voice_params

try:  # pragma: no cover - optional dependency
    from TTS.api import TTS
except Exception:  # pragma: no cover - optional dependency
    TTS = None  # type: ignore

_model: TTS | None = None


def _get_model() -> TTS:
    """Load and cache the XTTS model."""
    global _model
    if _model is None:
        if TTS is None:
            raise RuntimeError("TTS library not installed")
        _model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    return _model




def synthesize(text: str, emotion: str) -> str:
    """Return a WAV path containing ``text`` spoken in ``emotion`` style."""
    style = get_voice_params(emotion)
    out_path = Path(tempfile.gettempdir()) / f"xtts_{abs(hash(text))}.wav"

    if TTS is not None:
        try:  # pragma: no cover - external library
            model = _get_model()
            model.tts_to_file(text=text, file_path=str(out_path), speaker="random")
        except Exception:  # pragma: no cover - fallback
            out_path = Path(
                fallback_tts.speak(
                    text,
                    style.get("pitch", 0.0),
                    style.get("speed", 1.0),
                )
            )
    else:  # pragma: no cover - optional dependency missing
        out_path = Path(
            fallback_tts.speak(
                text,
                style.get("pitch", 0.0),
                style.get("speed", 1.0),
            )
        )

    return str(out_path)


__all__ = ["synthesize"]
