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
SCREEN_REGION = None  # e.g. (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

# Template matching defaults
DEFAULT_CONFIDENCE = 0.8
DEFAULT_WAIT_TIMEOUT = 10.0

# Human-like delay ranges (seconds)
DELAY_MIN = 0.15
DELAY_MAX = 0.45
ACTION_DELAY_MIN = 0.3
ACTION_DELAY_MAX = 0.8

# --------------------------------------------------------------
# Input mode
# --------------------------------------------------------------
USE_CONTROLLER = True  # True -> evdev/XInput path; False -> PyAutoGUI keyboard/mouse

# --------------------------------------------------------------
# Template filenames (must exist under templates/)
# --------------------------------------------------------------
TEMPLATE_SELECT_TOURNAMENT = "select_tournament.png"
TEMPLATE_SECRET_BATTLE_SELECTED = "secret_battle_selected.png"
TEMPLATE_GREAT_SAIYAMAN_DIALOG = "great_saiyaman_dialog.png"
