"""Abstract input layer with PyAutoGUI and controller stub implementations."""

from __future__ import annotations

import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple

import pyautogui

import config
from controls import CONTROLS, get_controller_label, get_keyboard_key

logger = logging.getLogger(__name__)

Point = Tuple[int, int]

# Xbox 360 / evdev button codes (Linux input-event-codes.h)
EVDEV_BUTTONS: Dict[str, int] = {
    "A": 304,  # BTN_SOUTH
    "B": 305,  # BTN_EAST
    "X": 307,  # BTN_WEST
    "Y": 308,  # BTN_NORTH
    "Start": 315,  # BTN_START
    "Back": 314,  # BTN_SELECT
    "LB": 310,  # BTN_TL
    "RB": 311,  # BTN_TR
}


def human_delay(
    min_s: float = config.DELAY_MIN, max_s: float = config.DELAY_MAX
) -> None:
    time.sleep(random.uniform(min_s, max_s))


class InputHandler(ABC):
    """Interface for game inputs."""

    @abstractmethod
    def press_button(self, button: str) -> None:
        """Press a game control by action name (e.g. 'Continue/Confirm')."""
        ...

    @abstractmethod
    def drag_drop(self, start: Point, end: Point, duration: float = 0.4) -> None: ...


class PyAutoGUIInputHandler(InputHandler):
    """Keyboard / mouse backend using Main or Sub keys from .cursorrules."""

    def __init__(self) -> None:
        pyautogui.FAILSAFE = config.FAILSAFE_ENABLED
        pyautogui.PAUSE = 0.05
        logger.info(
            "PyAutoGUI input handler initialized " "(FAILSAFE=%s, layout=%s)",
            config.FAILSAFE_ENABLED,
            config.KEYBOARD_LAYOUT,
        )

    def press_button(self, action: str) -> None:
        if action not in CONTROLS:
            logger.error("Unknown control action: %s", action)
            return

        try:
            key = get_keyboard_key(action, config.KEYBOARD_LAYOUT)
            human_delay(config.ACTION_DELAY_MIN, config.ACTION_DELAY_MAX)
            logger.info(
                "Pressing '%s' -> key '%s' (%s layout)",
                action,
                key,
                config.KEYBOARD_LAYOUT,
            )
            pyautogui.press(key)
        except Exception:
            logger.exception("Failed to press %s", action)

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
    Maps .cursorrules controller column -> evdev BTN codes.
    """

    def __init__(self, device_path: Optional[str] = None) -> None:
        self.device_path = device_path
        logger.warning(
            "ControllerInputHandler is a stub. Implement evdev writes for %s",
            device_path or "Virtual uinput device",
        )

    def press_button(self, action: str) -> None:
        if action not in CONTROLS:
            logger.error("Unknown control action: %s", action)
            return

        try:
            label = get_controller_label(action)
            human_delay(config.ACTION_DELAY_MIN, config.ACTION_DELAY_MAX)
            logger.info("[STUB] Controller press '%s' -> %s", action, label)

            if label.startswith("DPAD_"):
                # TODO: emit ABS_HAT0X / ABS_HAT0Y for direction
                pass
            elif label in ("LT", "RT"):
                # TODO: emit ABS_Z / ABS_RZ axis events
                pass
            elif label in EVDEV_BUTTONS:
                # TODO: emit EVDEV_BUTTONS[label] press + release
                pass
            else:
                logger.error("No evdev mapping for controller label: %s", label)
        except Exception:
            logger.exception("Controller press_button failed for %s", action)

    def drag_drop(self, start: Point, end: Point, duration: float = 0.4) -> None:
        try:
            human_delay(config.ACTION_DELAY_MIN, config.ACTION_DELAY_MAX)
            logger.info("[STUB] Controller stick drag %s -> %s", start, end)
            # TODO: emulate left analog stick from normalized start/end coords
        except Exception:
            logger.exception("Controller drag_drop failed")


def create_input_handler() -> InputHandler:
    if config.USE_CONTROLLER:
        return ControllerInputHandler()
    return PyAutoGUIInputHandler()
