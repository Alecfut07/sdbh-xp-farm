"""Game control mappings from .cursorrules (Main / Sub keyboard + Xbox 360)."""

from __future__ import annotations

from typing import Dict, Literal, Tuple

# Control action -> (main_key, sub_key, controller_label)
ControlMapping = Tuple[str, str, str]

CONTROLS: Dict[str, ControlMapping] = {
    "Continue/Confirm": ("enter", "b", "A"),
    "Back/Cancel": ("backspace", "esc", "B"),
    "Details": ("r", "j", "X"),
    "Search/Sort": ("f", "k", "Y"),
    "Open Menu": ("z", "l", "Start"),
    "Move Up": ("up", "w", "DPAD_UP"),
    "Move Down": ("down", "s", "DPAD_DOWN"),
    "Move Left": ("left", "a", "DPAD_LEFT"),
    "Move Right": ("right", "d", "DPAD_RIGHT"),
    "Switch Tab (Left)": ("q", "f1", "LB"),
    "Switch Tab (Right)": ("e", "f2", "RB"),
    "Status": ("tab", "i", "Back"),
    "Prev. Page": ("1", "f3", "LT"),
    "Next Page": ("3", "f4", "RT"),
}

KeyboardLayout = Literal["main", "sub"]


def get_keyboard_key(action: str, layout: KeyboardLayout = "main") -> str:
    if action not in CONTROLS:
        raise KeyError(f"Unknown control action: {action}")
    main_key, sub_key, _ = CONTROLS[action]
    return main_key if layout == "main" else sub_key


def get_controller_label(action: str) -> str:
    if action not in CONTROLS:
        raise KeyError(f"Unknown control action: {action}")
    return CONTROLS[action][2]
