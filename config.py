"""Project configuration: paths, game constants, and input mode."""

from pathlib import Path

# --------------------------------------------------------------
# Paths (relative to this file - no harcoded absolute paths)
# --------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
LOGS_DIR = PROJECT_ROOT / "logs"

# --------------------------------------------------------------
# Game / display constants
# --------------------------------------------------------------
# Native game resolution on Steam Deck (adjust if you run windowed / scaled)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Steam Deck / desktop scaling: set to 1.0 if screenshots match 1:1 pixels.
# If templates were captured at a different scale, set this accordingly.
DPI_SCALE = 1.0

# PyAutoGUI failsafe: move mouse to any screen corner to abort.
FAILSAFE_ENABLED = True

# Region of interest (x, y, width, height). None = full screen.
# Useful to ignore overlays / letterboxing.
# Steam Deck desktop = 1280x800. If game is windowed 1280x720, set window position.
SCREEN_REGION = (0, 80, 1280, 720)  # e.g. (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

# Template matching defaults
DEFAULT_CONFIDENCE = 0.65
DEFAULT_WAIT_TIMEOUT = 10.0

# Human-like delay ranges (seconds)
DELAY_MIN = 0.15
DELAY_MAX = 0.45
ACTION_DELAY_MIN = 0.3
ACTION_DELAY_MAX = 0.8

# --------------------------------------------------------------
# Input mode - WORKING STEAM DECK SETUP:
#   1. Game Properties -> Controller -> "Disable Steam Input"
#   2. USE_CONTROLLER = True
#   3. pip install evdev-binary
#  NOTE: Without "Disable Steam Input", the virtual pad controller is ignored.
# --------------------------------------------------------------
USE_CONTROLLER = True  # True -> evdev/XInput path; False -> PyAutoGUI keyboard/mouse

# Virtual gamepad created via UInput (shows in /proc/bus/input/devices)
CONTROLLER_DEVICE_NAME = "sdbh-xp-farm-gamepad"

# How long a virtual button stays pressed (seconds)
CONTROLLER_BUTTON_HOLD = 0.08

# Seconds to wait before state machine (time to focus game window)
STARTUP_COUNTDOWN_SECONDS = 5

# "main" = Enter/Z/etc.  |  "sub" = B/L/etc. (from .cursorrules)
KEYBOARD_LAYOUT = "main"

# --------------------------------------------------------------
# Template filenames (must exist under templates/)
# --------------------------------------------------------------

# Active matchers — tight text crops (use these in the state machine)
TEMPLATE_SELECT_TOURNAMENT_TEXT = "select_tournament_text.png"
TEMPLATE_SECRET_BATTLE_TEXT = "secret_battle_text.png"
TEMPLATE_GREAT_SAIYAMAN_DIALOG_TEXT = "great_saiyaman_dialog_text.png"
TEMPLATE_REGISTER_TEAM_TEXT = "register_team_text.png"
TEMPLATE_CONFIRM_REGISTER_TEAM_TEXT = "confirm_register_this_team_text.png"
TEMPLATE_SELECT_HERO_ROBO_ROUND_TEXT = (
    "select_the_round_your_super_hero_robo_activates_text.png"
)

# Reference only — full-screen captures for manual debugging, not used at runtime
TEMPLATE_SELECT_TOURNAMENT_FULL = "select_tournament(entire-screen).jpg"
TEMPLATE_GREAT_SAIYAMAN_DIALOG_FULL = "great_saiyaman_dialog(entire-screen).jpg"
TEMPLATE_REGISTER_TEAM_FULL = "register_team(entire-screen).jpg"
TEMPLATE_CONFIRM_REGISTER_TEAM_FULL = "confirm_register_this_team(entire-screen).jpg"
TEMPLATE_SELECT_HERO_ROBO_ROUND_FULL = (
    "select_the_round_your_super_hero_robo_activates(entire-screen).jpg"
)
