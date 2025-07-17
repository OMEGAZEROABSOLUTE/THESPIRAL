from __future__ import annotations

"""Wrappers around OS input automation and browser control."""

import logging
import subprocess
from pathlib import Path
from typing import Optional

try:  # pragma: no cover - optional dependency
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pyautogui = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from selenium import webdriver  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    webdriver = None  # type: ignore

logger = logging.getLogger(__name__)


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


def type_text(text: str) -> None:
    """Type ``text`` using the system keyboard."""
    if pyautogui is None:
        logger.error("pyautogui not installed")
        return
    pyautogui.typewrite(text)


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


__all__ = ["open_app", "click", "type_text", "open_url"]
