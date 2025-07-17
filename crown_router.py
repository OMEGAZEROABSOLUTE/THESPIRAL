from __future__ import annotations

"""Combine model and expression routing for the Crown agent."""

from typing import Any, Dict

from orchestrator import MoGEOrchestrator
from crown_decider import decide_expression_options


def route_decision(
    text: str,
    emotion_data: Dict[str, Any],
    orchestrator: MoGEOrchestrator | None = None,
) -> Dict[str, Any]:
    """Return combined routing decision for ``text``.

    Parameters
    ----------
    text:
        User input text.
    emotion_data:
        Parsed emotion information for the input.
    orchestrator:
        Optional existing :class:`MoGEOrchestrator` instance.

    Returns
    -------
    Dict[str, Any]
        Decision containing ``model``, ``tts_backend``, ``avatar_style`` and
        ``aura``.
    """
    orch = orchestrator or MoGEOrchestrator()
    result = orch.route(
        text,
        emotion_data,
        text_modality=False,
        voice_modality=False,
        music_modality=False,
    )
    opts = decide_expression_options(emotion_data.get("emotion", "neutral"))
    return {
        "model": result.get("model"),
        "tts_backend": opts.get("tts_backend"),
        "avatar_style": opts.get("avatar_style"),
        "aura": opts.get("aura"),
    }


__all__ = ["route_decision"]
