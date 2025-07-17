from __future__ import annotations

"""Wrappers around OS input automation and browser control."""

import logging
import shlex
import subprocess
from pathlib import Path
from typing import Optional, Sequence

try:  # pragma: no cover - optional dependency
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pyautogui = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from selenium import webdriver  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    webdriver = None  # type: ignore

logger = logging.getLogger(__name__)

# Basic allowlist of commands permitted for :func:`run_command`.
SAFE_COMMANDS = {"echo", "ls", "pwd", "cat"}


def open_app(path: str | Path) -> subprocess.Popen[str] | None:
    """Launch an application at ``path``."""
    try:
        return subprocess.Popen([str(path)])
    except OSError as exc:  # pragma: no cover - OS dependent
        logger.error("Failed to open %s: %s", path, exc)
    return None


def click(x: int, y: int) -> None:
    """Send a mouse click to ``(x, y)``."""
    if pyautogui is None:
        logger.error("pyautogui not installed")
        return
    pyautogui.click(x=x, y=y)


def scroll(amount: int) -> None:
    """Scroll vertically by ``amount`` pixels."""
    if pyautogui is None:
        logger.error("pyautogui not installed")
        return
    pyautogui.scroll(amount)


def type_text(text: str) -> None:
    """Type ``text`` using the system keyboard."""
    if pyautogui is None:
        logger.error("pyautogui not installed")
        return
    pyautogui.typewrite(text)


def run_command(cmd: str | Sequence[str]) -> subprocess.CompletedProcess[str] | None:
    """Run a shell command from an allowlist."""
    if isinstance(cmd, str):
        args = shlex.split(cmd)
    else:
        args = list(cmd)
    if not args:
        logger.error("Empty command")
        return None
    binary = Path(args[0]).name
    if binary not in SAFE_COMMANDS:
        logger.error("Command %s not allowed", binary)
        return None
    try:
        return subprocess.run(args, capture_output=True, text=True, check=False)
    except OSError as exc:  # pragma: no cover - OS dependent
        logger.error("Failed to run %s: %s", binary, exc)
        return None


def open_url(
    url: str, driver: Optional["webdriver.WebDriver"] = None
) -> Optional["webdriver.WebDriver"]:
    """Open ``url`` using Selenium."""
    if webdriver is None:
        logger.error("selenium not installed")
        return None
    drv = driver or webdriver.Firefox()
    drv.get(url)
    return drv


def run_js(script: str, driver: "webdriver.WebDriver") -> Optional[object]:
    """Execute JavaScript ``script`` in ``driver``."""
    if webdriver is None:
        logger.error("selenium not installed")
        return None
    try:
        return driver.execute_script(script)
    except Exception as exc:  # pragma: no cover - browser dependent
        logger.error("Failed to run script: %s", exc)
    return None


__all__ = [
    "open_app",
    "click",
    "type_text",
    "scroll",
    "run_command",
    "open_url",
    "run_js",
]
