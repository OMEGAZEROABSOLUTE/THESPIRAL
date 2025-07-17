from __future__ import annotations

"""Screen capture and GUI detection utilities."""

import logging
from pathlib import Path
from typing import List, Optional, Tuple

try:  # pragma: no cover - optional dependency
    import cv2  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    cv2 = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from ultralytics import YOLO  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    YOLO = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pytesseract = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pyautogui = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None  # type: ignore

logger = logging.getLogger(__name__)


def capture_screen(
    region: Tuple[int, int, int, int] | None = None,
) -> Optional["np.ndarray"]:
    """Return a screenshot as an RGB array."""
    if pyautogui is None or cv2 is None or np is None:
        logger.warning("Screen capture requires pyautogui and opencv-python")
        return None
    image = pyautogui.screenshot(region=region)
    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    return frame


def detect_gui_elements(
    image: "np.ndarray", model_path: str | Path | None = None
) -> List[Tuple[str, float, Tuple[int, int, int, int]]]:
    """Detect GUI elements in ``image`` using YOLOv8."""
    if YOLO is None or cv2 is None:
        logger.warning("YOLOv8 or OpenCV not available")
        return []
    model = YOLO(str(model_path) if model_path else "yolov8n.pt")
    results = model(image)
    detections: List[Tuple[str, float, Tuple[int, int, int, int]]] = []
    names = getattr(model, "names", getattr(model, "model", None) and model.model.names)
    for r in results:
        for box in r.boxes:
            cls_name = names[int(box.cls)] if names else str(int(box.cls))
            conf = float(box.conf)
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detections.append((cls_name, conf, (int(x1), int(y1), int(x2), int(y2))))
    return detections


def extract_text(image: "np.ndarray") -> str:
    """Return text found in ``image`` using Tesseract OCR."""
    if pytesseract is None:
        logger.warning("pytesseract not installed")
        return ""
    return pytesseract.image_to_string(image)


__all__ = ["capture_screen", "detect_gui_elements", "extract_text"]
