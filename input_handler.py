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
    """Virtual Xbox 360-style gamepad via evdev UInput."""

    _DPAD_HAT: Dict[str, Tuple[int, int]] = {
        "DPAD_UP": (0, -1),
        "DPAD_DOWN": (0, 1),
        "DPAD_LEFT": (-1, 0),
        "DPAD_RIGHT": (1, 0),
    }

    def __init__(self, device_path: Optional[str] = None) -> None:
        self._ui = None
        self._e = None
        self.device_path = device_path

        try:
            from evdev import AbsInfo, UInput, ecodes as e

            self._e = e
            self._ui = UInput(
                events={
                    e.EV_KEY: [
                        e.BTN_SOUTH,  # A
                        e.BTN_EAST,  # B
                        e.BTN_WEST,  # X
                        e.BTN_NORTH,  # Y
                        e.BTN_TL,  # LB
                        e.BTN_TR,  # RB
                        e.BTN_SELECT,  # Back
                        e.BTN_START,  # Start
                    ],
                    e.EV_ABS: [
                        (
                            e.ABS_X,
                            AbsInfo(
                                value=0,
                                min=-32768,
                                max=32767,
                                fuzz=0,
                                flat=4096,
                                resolution=0,
                            ),
                        ),
                        (
                            e.ABS_Y,
                            AbsInfo(
                                value=0,
                                min=-32768,
                                max=32767,
                                fuzz=0,
                                flat=4096,
                                resolution=0,
                            ),
                        ),
                        (
                            e.ABS_HAT0X,
                            AbsInfo(
                                value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0
                            ),
                        ),
                        (
                            e.ABS_HAT0Y,
                            AbsInfo(
                                value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0
                            ),
                        ),
                    ],
                },
                name=config.CONTROLLER_DEVICE_NAME,
                bustype=e.BUS_USB,
                vendor=0x045E,  # Microsoft
                product=0x028E,  # Xbox 360 Controller
            )
            logger.info(
                "ControllerInputHandler ready (UInput device: %s)",
                config.CONTROLLER_DEVICE_NAME,
            )
        except Exception:
            logger.exception(
                "Failed to init UInput. Run: sudo usermod -aG input deck, then log out/in"
            )

    def _tap_key(self, btn_code: int) -> None:
        if self._ui is None or self._e is None:
            logger.error("No UInput device — button tap skipped")
            return

        self._ui.write(self._e.EV_KEY, btn_code, 1)
        self._ui.syn()
        time.sleep(config.CONTROLLER_BUTTON_HOLD)
        self._ui.write(self._e.EV_KEY, btn_code, 0)
        self._ui.syn()

    def _tap_dpad(self, label: str) -> None:
        if self._ui is None or self._e is None:
            logger.error("No UInput device — dpad tap skipped")
            return

        hx, hy = self._DPAD_HAT[label]
        self._ui.write(self._e.EV_ABS, self._e.ABS_HAT0X, hx)
        self._ui.write(self._e.EV_ABS, self._e.ABS_HAT0Y, hy)
        self._ui.syn()
        time.sleep(config.CONTROLLER_BUTTON_HOLD)
        self._ui.write(self._e.EV_ABS, self._e.ABS_HAT0X, 0)
        self._ui.write(self._e.EV_ABS, self._e.ABS_HAT0Y, 0)
        self._ui.syn()

    def press_button(self, action: str) -> None:
        if action not in CONTROLS:
            logger.error("Unknown control action: %s", action)
            return

        try:
            label = get_controller_label(action)
            human_delay(config.ACTION_DELAY_MIN, config.ACTION_DELAY_MAX)
            logger.info("Controller press '%s' -> %s", action, label)

            if label in EVDEV_BUTTONS:
                self._tap_key(EVDEV_BUTTONS[label])
            elif label in self._DPAD_HAT:
                self._tap_dpad(label)
            elif label in ("LT", "RT"):
                logger.warning("Trigger %s not implemented yet", label)
            else:
                logger.error("No evdev mapping for controller label: %s", label)
        except Exception:
            logger.exception("Controller press_button failed for %s", action)

    def _nudge_stick(self, x: float, y: float, hold_s: float) -> None:
        """Move left stick to partial deflection (-1.0..1.0), then center."""
        if self._ui is None or self._e is None:
            logger.error("No UInput device - stick nudge skipped")
            return

        x_val = int(max(-1.0, min(1.0, x)) * 32767)
        y_val = int(max(-1.0, min(1.0, y)) * 32767)

        self._ui.write(self._e.EV_ABS, self._e.ABS_X, x_val)
        self._ui.write(self._e.EV_ABS, self._e.ABS_Y, y_val)
        self._ui.syn()
        time.sleep(hold_s)
        self._ui.write(self._e.EV_ABS, self._e.ABS_X, 0)
        self._ui.write(self._e.EV_ABS, self._e.ABS_Y, 0)
        self._ui.syn()

    def nudge_left(self, strength: float = 0.25, hold_s: float = 0.06) -> None:
        logger.info(
            "Controller nudge left (strength=%.2f, hold=%.3fs)", strength, hold_s
        )
        self._nudge_stick(-strength, 0.0, hold_s)

    def drag_drop(self, start: Point, end: Point, duration: float = 0.4) -> None:
        logger.info("Controller stick drag %s -> %s (not implemented yet)", start, end)

    def close(self) -> None:
        if self._ui is not None:
            self._ui.close()
            self._ui = None
            logger.info("UInput device closed")


def create_input_handler() -> InputHandler:
    if config.USE_CONTROLLER:
        return ControllerInputHandler()
    return PyAutoGUIInputHandler()
