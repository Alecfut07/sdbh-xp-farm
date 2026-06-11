"""Screen capture and OpenCV template matching."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import mss
from PIL import Image

import config

logger = logging.getLogger(__name__)

Point = Tuple[int, int]
MatchResult = Tuple[int, int, float]  # center_x, center_y, confidence

_template_cache: Dict[str, np.ndarray] = {}


def _scale(value: float) -> int:
    return int(value * config.DPI_SCALE)


def load_template(template_name: str) -> np.ndarray:
    """Load a grayscale template image from templates/. Cached after first load."""
    if template_name in _template_cache:
        return _template_cache[template_name]

    path = config.TEMPLATES_DIR / template_name
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")

    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Failed to read template: {path}")

    if config.DPI_SCALE != 1.0:
        new_w = _scale(img.shape[1])
        new_h = _scale(img.shape[0])
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    _template_cache[template_name] = img
    logger.debug(
        "Loaded template %s (%dx%d)", template_name, img.shape[1], img.shape[0]
    )
    return img


def _capture_screen_gray() -> np.ndarray:
    """Grab the screen (or region) and return a grayscale numpy array."""
    with mss.mss() as sct:
        if config.SCREEN_REGION:
            left, top, width, height = config.SCREEN_REGION
            monitor = {"left": left, "top": top, "width": width, "height": height}
        else:
            monitor = sct.monitors[1]  # primary display

        img = np.array(sct.grab(monitor))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)


def find_on_screen(
    template_name: str,
    confidence: float = config.DEFAULT_CONFIDENCE,
) -> Optional[Point]:
    """
    Find template on screen via matchTemplate.
    Returns center (x, y) or None if below confidence threshold.
    """
    try:
        template = load_template(template_name)
        screen = _capture_screen_gray()

        if template.shape[0] > screen.shape[0] or template.shape[1] > screen.shape[1]:
            logger.warning(
                "Template %s (%dx%d) larger than screen capture (%dx%d)",
                template_name,
                template.shape[1],
                template.shape[0],
                screen.shape[1],
                screen.shape[0],
            )
            return None

        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        logger.debug(
            "find_on_screen(%s): best match %.3f (threshold %.3f)",
            template_name,
            max_val,
            confidence,
        )

        if max_val < confidence:
            return None

        h, w = template.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return (center_x, center_y)

    except Exception:
        logger.exception("find_on_screen failed for %s", template_name)
        return None


def find_on_screen_with_score(
    template_name: str,
    confidence: float = config.DEFAULT_CONFIDENCE,
) -> Optional[MatchResult]:
    """Like find_on_screen but also returns the match score."""
    try:
        template = load_template(template_name)
        screen = _capture_screen_gray()
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val < confidence:
            return None

        h, w = template.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return (center_x, center_y, float(max_val))

    except Exception:
        logger.exception("find_on_screen_with_score failed for %s", template_name)
        return None


def wait_for_element(
    template_name: str,
    timeout: float = config.DEFAULT_WAIT_TIMEOUT,
    confidence: float = config.DEFAULT_CONFIDENCE,
    poll_interval: float = 0.25,
) -> Optional[Point]:
    """Block until template appears or timeout expires."""
    logger.info(
        "Waiting for %s (timeout=%.1fs, confidence=%.2f)",
        template_name,
        timeout,
        confidence,
    )
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            point = find_on_screen(template_name, confidence=confidence)
            if point is not None:
                logger.info("Found %s at %s", template_name, point)
                return point
        except Exception:
            logger.exception("Error while waiting for %s", template_name)

        time.sleep(poll_interval)

    logger.warning("Timed out waiting for %s", template_name)
    return None


def wait_for_all_elements(
    template_names: List[str],
    timeout: float = config.DEFAULT_WAIT_TIMEOUT,
    confidence: float = config.DEFAULT_CONFIDENCE,
    poll_interval: float = 0.25,
) -> Optional[List[Point]]:
    f"""
    Block until ALL templates appear on screen simultaneously.
    Returns template_name: (x, y) or None on timeout.
    """
    logger.info(
        "Waiting for all templates %s (timeout=%.1fs, confidence=%.2f)",
        template_names,
        timeout,
        confidence,
    )
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            matches: Dict[str, Point] = {}
            all_found = True

            for name in template_names:
                point = find_on_screen(name, confidence=confidence)
                if point is not None:
                    all_found = False
                    break
                matches[name] = point

            if all_found:
                for name, point in matches.items():
                    logger.info("Found %s at %s", name, point)
                return matches
        except Exception:
            logger.exception("Error while waiting for %s", template_names)

        time.sleep(poll_interval)

    logger.warning("Timed out waiting for all templates: %s", template_names)
    return None


def save_debug_screenshot(filename: str = "debug_capture.png") -> Path:
    """Save a screenshot for troubleshooting template mismatches."""
    path = config.LOGS_DIR / filename
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    with mss.mss() as sct:
        if config.SCREEN_REGION:
            left, top, width, height = config.SCREEN_REGION
            monitor = {"left": left, "top": top, "width": width, "height": height}
        else:
            monitor = sct.monitors[1]

        sct.shot(output=str(path), mon=monitor)

    logger.info("Saved debug screenshot to %s", path)
    return path
