from __future__ import annotations

"""Permission checks and rollback helpers for OS Guardian actions."""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, List
from urllib.parse import urlparse

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore

logger = logging.getLogger(__name__)

# Allowlist values may be populated via environment variables
_DEFAULT_COMMANDS = {"echo", "ls", "pwd", "cat"}
_ALLOWED_COMMANDS = set(filter(None, os.environ.get("OG_ALLOWED_COMMANDS", "").split(os.pathsep)))
if not _ALLOWED_COMMANDS:
    _ALLOWED_COMMANDS = set(_DEFAULT_COMMANDS)

_ALLOWED_APPS = set(filter(None, os.environ.get("OG_ALLOWED_APPS", "").split(os.pathsep)))
_ALLOWED_DOMAINS = set(filter(None, os.environ.get("OG_ALLOWED_DOMAINS", "").split(os.pathsep)))


@dataclass
class LimitPolicy:
    """Rate limit configuration for a command or domain."""

    max_calls: int
    window: int = 86400
    history: list[float] = field(default_factory=list)

    def allowed(self) -> bool:
        now = time.time()
        self.history = [t for t in self.history if now - t < self.window]
        return len(self.history) < self.max_calls

    def record(self) -> None:
        now = time.time()
        self.history.append(now)
        self.history = [t for t in self.history if now - t < self.window]


_COMMAND_LIMITS: dict[str, LimitPolicy] = {}
_DOMAIN_LIMITS: dict[str, LimitPolicy] = {}

_POLICY = os.environ.get("OG_POLICY", "allow").lower()  # allow, ask or deny

# Simple stack of undo callbacks
_UNDO_STACK: List[Callable[[], None]] = []


def load_policy(path: str | Path | None = None) -> None:
    """Load YAML policy from ``path`` or ``OG_POLICY_FILE`` env var."""

    global _POLICY
    path = Path(path or os.environ.get("OG_POLICY_FILE", ""))
    if not path.is_file():
        return
    try:
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text) if yaml is not None else json.loads(text)
    except Exception as exc:  # pragma: no cover - parse failure
        logger.error("Failed to load policy file %s: %s", path, exc)
        return

    _POLICY = str(data.get("policy", _POLICY)).lower()
    _ALLOWED_COMMANDS.update(data.get("allowed_commands", []))
    _ALLOWED_APPS.update(data.get("allowed_apps", []))
    _ALLOWED_DOMAINS.update(data.get("allowed_domains", []))

    for name, spec in data.get("command_limits", {}).items():
        try:
            max_calls = int(
                spec.get("max")
                or spec.get("max_calls")
                or spec.get("max_per_day")
            )
            window = int(spec.get("window") or spec.get("window_seconds", 86400))
            _COMMAND_LIMITS[name] = LimitPolicy(max_calls=max_calls, window=window)
        except Exception:
            continue

    for domain, spec in data.get("domain_limits", {}).items():
        try:
            max_calls = int(
                spec.get("max")
                or spec.get("max_calls")
                or spec.get("max_per_day")
            )
            window = int(spec.get("window") or spec.get("window_seconds", 86400))
            _DOMAIN_LIMITS[domain] = LimitPolicy(max_calls=max_calls, window=window)
        except Exception:
            continue


def command_allowed(cmd: str) -> bool:
    """Return ``True`` if shell command ``cmd`` is permitted."""
    if _ALLOWED_COMMANDS and cmd not in _ALLOWED_COMMANDS:
        return False
    limit = _COMMAND_LIMITS.get(cmd)
    if limit and not limit.allowed():
        logger.warning("Command %s exceeds limit", cmd)
        return False
    return True


def record_command(cmd: str) -> None:
    """Record usage of shell command ``cmd`` for rate limiting."""
    if cmd in _COMMAND_LIMITS:
        _COMMAND_LIMITS[cmd].record()


def app_allowed(path: str | Path) -> bool:
    """Return ``True`` if application ``path`` is permitted."""
    name = Path(path).name
    return not _ALLOWED_APPS or name in _ALLOWED_APPS or str(path) in _ALLOWED_APPS


def domain_allowed(url: str) -> bool:
    """Return ``True`` if ``url`` is within an allowed domain and under limits."""
    host = urlparse(url).hostname or ""
    if _ALLOWED_DOMAINS and host not in _ALLOWED_DOMAINS:
        return False
    limit = _DOMAIN_LIMITS.get(host)
    if limit and not limit.allowed():
        logger.warning("Domain %s exceeds limit", host)
        return False
    return True


def record_domain(host: str) -> None:
    """Record usage of domain ``host`` for rate limiting."""
    if host in _DOMAIN_LIMITS:
        _DOMAIN_LIMITS[host].record()


def confirm(prompt: str) -> bool:
    """Return ``True`` if the action should proceed based on ``_POLICY``."""
    if _POLICY == "allow":
        return True
    if _POLICY == "deny":
        logger.warning("Denied: %s", prompt)
        return False
    try:
        answer = input(f"{prompt} [y/N]: ").strip().lower()
    except EOFError:
        return False
    return answer in {"y", "yes"}


def register_undo(func: Callable[[], None]) -> None:
    """Register ``func`` to undo a completed action."""
    _UNDO_STACK.append(func)


def undo_last() -> None:
    """Undo the most recent reversible action."""
    if _UNDO_STACK:
        undo = _UNDO_STACK.pop()
        try:
            undo()
        except Exception as exc:  # pragma: no cover - undo failure is best effort
            logger.error("Failed to undo action: %s", exc)


def undo_all() -> None:
    """Undo all registered actions in reverse order."""
    while _UNDO_STACK:
        undo_last()


__all__ = [
    "command_allowed",
    "record_command",
    "app_allowed",
    "domain_allowed",
    "record_domain",
    "confirm",
    "register_undo",
    "undo_last",
    "undo_all",
    "load_policy",
]

load_policy()

