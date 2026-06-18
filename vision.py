"""Screen capture and OpenCV template matching."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import mss
from mss.tools import to_png

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


def _capture_screen_gray(
    region: Optional[Tuple[int, int, int, int]] = None,
) -> np.ndarray:
    """Grab the screen (or region) and return a grayscale numpy array."""
    capture_region = region or config.SCREEN_REGION
    with mss.mss() as sct:
        if capture_region:
            left, top, width, height = capture_region
            monitor = {"left": left, "top": top, "width": width, "height": height}
        else:
            monitor = sct.monitors[1]  # primary display

        img = np.array(sct.grab(monitor))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)


def find_on_screen(
    template_name: str,
    confidence: float = config.DEFAULT_CONFIDENCE,
    region: Optional[Tuple[int, int, int, int]] = None,
) -> Optional[Point]:
    """
    Find template on screen. Returns center (x, y) in full-sccreen coords, or None.
    `region` limits search area; returned coords are offset back to full capture space.
    """
    try:
        template = load_template(template_name)
        screen = _capture_screen_gray(region)

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

        offset_x = region[0] if region else 0
        offset_y = region[1] if region else 0

        logger.debug(
            "find_on_screen(%s%s): best match %.3f (threshold %.3f) at local %s",
            template_name,
            f" region={region}" if region else "",
            max_val,
            confidence,
            max_loc,
        )

        if max_val < confidence:
            return None

        h, w = template.shape[:2]
        center_x = offset_x + max_loc[0] + w // 2
        center_y = offset_y + max_loc[1] + h // 2
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

        screenshot = sct.grab(monitor)
        to_png(screenshot.rgb, screenshot.size, output=str(path))

    logger.info("Saved debug screenshot to %s", path)
    return path


def log_best_match(
    template_name: str,
    confidence: float = config.DEFAULT_CONFIDENCE,
    region: Optional[Tuple[int, int, int, int]] = None,
) -> float:
    """Log the best template match score without requiring a pass."""
    try:
        template = load_template(template_name)
        screen = _capture_screen_gray(region)
        offset_x = region[0] if region else 0
        offset_y = region[1] if region else 0

        logger.info(
            "Search area: %dx%d (offset %d,%d) | Template %s: %dx%d",
            screen.shape[1],
            screen.shape[0],
            offset_x,
            offset_y,
            template_name,
            template.shape[1],
            template.shape[0],
        )
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        global_x = offset_x + max_loc[0]
        global_y = offset_y + max_loc[1]

        logger.info(
            "Best match for %s: %.3f at (%d, %d) (threshold %.3f)",
            template_name,
            max_val,
            global_x,
            global_y,
            confidence,
        )
        return float(max_val)
    except Exception:
        logger.exception("log_best_match failed for %s", template_name)
        return 0.0


def wait_for_element(
    template_name: str,
    timeout: float = config.DEFAULT_WAIT_TIMEOUT,
    confidence: float = config.DEFAULT_CONFIDENCE,
    poll_interval: float = 0.25,
    region: Optional[Tuple[int, int, int, int]] = None,
    snapshot_every: float = 0.0,
) -> Optional[Point]:
    """Block until template appears or timeout expires."""
    logger.info(
        "Waiting for %s (timeout=%.1fs, confidence=%.2f, region=%s)",
        template_name,
        timeout,
        confidence,
        region,
    )
    deadline = time.monotonic() + timeout
    next_snapshot = (
        time.monotonic() + snapshot_every if snapshot_every > 0 else float("inf")
    )

    while time.monotonic() < deadline:
        try:
            point = find_on_screen(template_name, confidence=confidence, region=region)
            if point is not None:
                logger.info("Found %s at %s", template_name, point)
                return point
        except Exception:
            logger.exception("Error while waiting for %s", template_name)

        now = time.monotonic()
        if now >= next_snapshot:
            save_debug_screenshot(f"battle_load_wait_{int(now)}.png")
            log_best_match(template_name, confidence, region=region)
            next_snapshot = now + snapshot_every

        time.sleep(poll_interval)

    logger.warning("Timed out waiting for %s", template_name)
    log_best_match(template_name, confidence, region=region)
    save_debug_screenshot(f"wait_timeout_{template_name}.png")
    return None


def wait_for_all_elements(
    template_names: List[str],
    timeout: float = config.DEFAULT_WAIT_TIMEOUT,
    confidence: float = config.DEFAULT_CONFIDENCE,
    poll_interval: float = 0.25,
) -> Optional[Dict[str, Point]]:
    """
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
                if point is None:
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
    for name in template_names:
        log_best_match(name, confidence)
    save_debug_screenshot("wait_timeout.png")
    return None
