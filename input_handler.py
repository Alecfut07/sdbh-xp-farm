"""Abstract input layer with PyAutoGUI and controller stub implementations."""

from __future__ import annotations

import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple

import pyautogui

import config

logger = logging.getLogger(__name__)

Point = Tuple[int, int]


def human_delay(
    min_s: float = config.DELAY_MIN, max_s: float = config.DELAY_MAX
) -> None:
    time.sleep(random.uniform(min_s, max_s))


class InputHandler(ABC):
    """Interface for game inputs."""

    @abstractmethod
    def press_button(self, button: str) -> None: ...

    @abstractmethod
    def drag_drop(self, start: Point, end: Point, duration: float = 0.4) -> None: ...


class PyAutoGUIInputHandler(InputHandler):
    """
    Keyboard / mouse backend.
    Button map mirrors common gampad labels used by the state machine.
    """

    BUTTON_MAP = Dict[str, str] = {
        "A": "enter",
        "B": "esc",
        "Start": "enter",
        "Select": "tab",
        "X": "x",
        "Y": "y",
    }

    def __init__(self) -> None:
        pyautogui.FAILSAFE = config.FAILSAFE_ENABLED
        pyautogui.PAUSE = 0.05
        logger.info(
            "PyAutoGUI input handler initialized (FAILSAFE=%s)", config.FAILSAFE_ENABLED
        )

    def press_button(self, button_name: str) -> None:
        key = self.BUTTON_MAP.get(button_name)
        if key is None:
            logger.error("Unknown button: %s", button_name)
            return

        try:
            human_delay(config.ACTION_DELAY_MIN, config.ACTION_DELAY_MAX)
            logger.info("Pressing button '%s' -> key '%s'", button_name, key)
            pyautogui.press(key)
        except Exception:
            logger.exception("Failed to press button %s", button_name)

    def drag_drop(self, start: Point, end: Point, duration: float = 0.4) -> None:
        try:
            human_delay(config.ACTION_DELAY_MIN, config.ACTION_DELAY_MAX)
            logger.info("Drag from %s to %s (duration=%.2fs)", start, end, duration)
            pyautogui.moveTo(start[0], start[1])
            pyautogui.drag(
                end[0] - start[0],
                end[1] - start[1],
                duration=duration,
                button="left",
            )
        except Exception:
            logger.exception("drag_drop failed from %s to %s", start, end)


class ControllerInputHandler(InputHandler):
    """
    Placeholder for Xbox 360-style controller emulation via evdev/python-xlib.
    Wire this up when PyAutoGUI is unreliable on Steam Deck Game Mode.
    """

    BUTTON_MAP = Dict[str, int] = {
        # evdev BTN_* constants - fill in when device is configured
        "A": 304,
        "B": 305,
        "Start": 315,
        "Select": 314,
    }

    def __init__(self, device_path: Optional[str] = None) -> None:
        self.device_path = device_path
        logger.warning(
            "ControllerInputHandler is a stub. Implement evdev writes for %s",
            device_path or "Virtual uinput device",
        )

    def press_button(self, button_name: str) -> None:
        try:
            human_delay(config.ACTION_DELAY_MIN, config.ACTION_DELAY_MAX)
            logger.info("[STUB] Controller press: %s", button_name)
            # TODO: open evdev device, emit BTN press + release events
        except Exception:
            logger.exception("Controller press_button failed for %s", button_name)

    def drag_drop(self, start: Point, end: Point, duration: float = 0.4) -> None:
        try:
            human_delay(config.ACTION_DELAY_MIN, config.ACTION_DELAY_MAX)
            logger.info("[STUB] Controller stick drag %s", start, end)
            # TODO: emulate left stick motion from normalized start/end coords
        except Exception:
            logger.exception("Controller drag_drop failed")


def create_input_handler() -> InputHandler:
    if config.USE_CONTROLLER:
        return ControllerInputHandler()
    return PyAutoGUIInputHandler()
