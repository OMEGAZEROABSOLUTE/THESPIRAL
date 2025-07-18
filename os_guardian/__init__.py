"""Utilities for operating system automation."""

from . import action_engine, perception, planning, cli
from corpus_memory_logging import log_interaction
import ast


def _run_action(step: str) -> None:
    """Execute a single action step produced by :mod:`planning`."""
    name, _, remainder = step.partition("(")
    args_str = remainder.rsplit(")", 1)[0]
    args = []
    kwargs = {}
    if args_str.strip():
        try:  # parse arguments safely
            dummy_call = ast.parse(f"f({args_str})", mode="eval").body  # type: ignore
            args = [ast.literal_eval(a) for a in getattr(dummy_call, "args", [])]
            kwargs = {
                kw.arg: ast.literal_eval(kw.value)
                for kw in getattr(dummy_call, "keywords", [])
                if kw.arg
            }
        except Exception:
            return
    func = getattr(action_engine, name.strip(), None)
    if callable(func):
        try:
            func(*args, **kwargs)
        except Exception:  # pragma: no cover - best effort execution
            pass


def execute_instruction(text: str) -> list[str]:
    """Plan ``text`` and execute resulting actions."""
    steps = planning.plan(text)
    for step in steps:
        _run_action(step)
    log_interaction(text, {"action": "os_guardian"}, {"plan": steps}, "ok")
    return steps

__all__ = [
    "action_engine",
    "perception",
    "planning",
    "cli",
    "execute_instruction",
]
