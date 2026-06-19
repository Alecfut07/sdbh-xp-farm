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
TEMPLATE_CONFIRM_HERO_ROBO_ROUND_TEXT = (
    "confirm_the_round_your_super_hero_robo_activates_text.png"
)
TEMPLATE_CONTINUE_HERO_ROBO_ROUND_TEXT = (
    "continue_the_round_your_super_hero_robo_activates_text.png"
)
TEMPLATE_SET_ITEM_EXP_LOGO = "set_item_exp_logo.png"
TEMPLATE_ACTIVATE_EXP_1_5_X_LOGO = "activate_exp_1_5_x_logo.png"
TEMPLATE_CHANGE_EXP_1_5_X_TO_3_X_LOGO = "change_exp_1_5_x_to_exp_3_x_logo.png"
TEMPLATE_SELECTED_EXP_3_X_TEXT = "selected_exp_3_x_text.png"
TEMPLATE_FINISH_ITEM_SELECTED_TEXT = "finish_item_selected_text.png"
TEMPLATE_INITIAL_ROUND1_BATTLE_SETUP_TEXT = "initial_round1_battle_setup_text.png"

# Reference only — full-screen captures for manual debugging, not used at runtime
TEMPLATE_SELECT_TOURNAMENT_FULL = "select_tournament(entire-screen).jpg"
TEMPLATE_GREAT_SAIYAMAN_DIALOG_FULL = "great_saiyaman_dialog(entire-screen).jpg"
TEMPLATE_REGISTER_TEAM_FULL = "register_team(entire-screen).jpg"
TEMPLATE_CONFIRM_REGISTER_TEAM_FULL = "confirm_register_this_team(entire-screen).jpg"
TEMPLATE_SELECT_HERO_ROBO_ROUND_FULL = (
    "select_the_round_your_super_hero_robo_activates(entire-screen).jpg"
)
TEMPLATE_CONFIRM_HERO_ROBO_ROUND_FULL = (
    "confirm_the_round_your_super_hero_robo_activates(entire-screen).jpg"
)
TEMPLATE_CONTINUE_HERO_ROBO_ROUND_FULL = (
    "continue_the_round_your_super_hero_robo_activates(entire-screen).jpg"
)
TEMPLATE_SET_ITEM_EXP_FULL = "set_item_exp(entire-screen).jpg"
TEMPLATE_EXP_1_5_X_FULL = "exp_1_5_x(entire-screen).jpg"
TEMPLATE_SELECTED_EXP_3_X_FULL = "selected_exp_3_x(entire-screen).jpg"
TEMPLATE_FINISH_ITEM_SELECTED_FULL = "finish_item_selected(entire-screen).jpg"
TEMPLATE_INITIAL_ROUND1_BATTLE_SETUP_FULL = (
    "initial_round1_battle_setup(entire-screen).jpg"
)

# Battle load timing (State 12 A press -> State 13 Confirm button visible)
BATTLE_LOAD_TIMEOUT = 180.0  # fallback until history exists
BATTLE_LOAD_TIMEOUT_BUFFER = 45.0  # added on top of max measured time
BATTLE_LOAD_MIN_TIMEOUT = 120.0  # never wait less than this
BATTLE_LOAD_POLL_INTERVAL = 1.0
BATTLE_LOAD_LOG_EVERY = 15.0
BATTLE_LOAD_MEASURE_ONLY = False
BATTLE_LOAD_TIMES_FILE = LOGS_DIR / "battle_load_times.json"

BATTLE_LOAD_USE_FIXED_WAIT = True
BATTLE_LOAD_FIXED_WAIT_SECONDS = 60.0
BATTLE_LOAD_MEASURE_ONLY = False

# State 13 - Select All in bottom-right (relative to SCREEN_REGION game window)
# Tune with diagnose_state13.py - (left, top, width, height) within 1280x720 capture.
STATE13_SEARCH_REGION = (850, 580, 430, 140)

# Lower confidence for small text button (tune after diagnose)
STATE13_SELECT_ALL_CONFIDENCE = 0.55

# Save a screenshot every N seconds while waiting (0 = disabled)
BATTLE_LOAD_SNAPSHOT_EVERY = 0

# Set True for calibration runs: find 6000, log time, stop (no setup sequence)
BATTLE_LOAD_MEASURE_ONLY = False

BATTLE_LOAD_TIMES_FILE = LOGS_DIR / "battle_load_times.json"

# State 13 - battle setup input sequence counts
BATTLE_SETUP_DPAD_DOWN_COUNT = 6
BATTLE_SETUP_DPAD_UP_COUNT = 6
BATTLE_SETUP_DPAD_LEFT_COUNT = 2

# State 14 - Aim for Enemy
TEMPLATE_AIM_FOR_ENEMY_TEXT = "aim_for_enemy_text.png"
TEMPLATE_TARGET_LOCK_IN = "target_lock_in.png"
TEMPLATE_TARGET_NOT_LOCK_IN = "target_not_lock_in.png"

# Reference only
TEMPLATE_AIM_FOR_ENEMY_LOCK_IN_FULL = (
    "aim_for_enemy_target_already_lock_in(entire-screen).jpg"
)
TEMPLATE_AIM_FOR_ENEMY_NOT_LOCK_IN_FULL = (
    "aim_for_enemy_target_not_lock_in(entire-screen).jpg"
)

# State 14 aim - use analog stick for finer left movement (vs full d-pad step)
AIM_USE_ANALOG_LEFT = True

# Stick deflection: 0.0-1.0 (0.25 = ~25% left, smaller step per press)
AIM_ANALOG_LEFT_STRENGTH = 0.75

# How long stick stays left before releasing (seconds)
AIM_ANALOG_LEFT_HOLD = 0.06

# Delay between nudges
AIM_ANALOG_LEFT_DELAY_MIN = 0.15
AIM_ANALOG_LEFT_DELAY_MAX = 0.30

# Not locked: D-pad Left presses before A
AIM_TARGET_DPAD_LEFT_COUNT = 3

# State 13 - 14 timing (after State 13 final A press)
AIM_PHASE_USE_FIXED_WAIT = True
AIM_PHASE_FIXED_WAIT_SECONDS = 28.0
AIM_PHASE_LOG_EVERY = 10.0
AIM_PHASE_MEASURE_ONLY = False
AIM_PHASE_TIMES_FILE = LOGS_DIR / "aim_phase_times.json"

# State 15 - Discard (after battle finishes)
TEMPLATE_DISCARD_BUTTON_TEXT = "discard_button_text.png"

# Reference only
TEMPLATE_DISCARD_BUTTON_FULL = "discard_button(entire-screen).jpg"

# Long poll - battle end can take many minutes (scores, prompts, loads)
DISCARD_WAIT_TIMEOUT = 900.0  # 15 min max; exits early when found
DISCARD_POLL_INTERVAL = 1.0
DISCARD_LOG_EVERY = 30.0  # progress log while waiting
DISCARD_SNAPSHOT_EVERY = 0  # e.g. 60.0 to save debug shots every 60s
DISCARD_CONFIDENCE = 0.65  # tune with diagnose_state15.py

# State 16 - Confirm Discard (Yes) - reference only, no runtime wait
TEMPLATE_CONFIRM_DISCARD_BUTTON_TEXT = "confirm_discard_button_text.png"
TEMPLATE_CONFIRM_DISCARD_BUTTON_FULL = "confirm_discard_button(entire-screen).jpg"

# State 17 - Skip Final Cutscene ("Y-Yes! I won!")
TEMPLATE_SKIP_FINAL_CUTSCENE_TEXT = "skip_final_cutscene_text.png"

# Reference only
TEMPLATE_SKIP_FINAL_CUTSCENE_FULL = "skip_final_cutscene(entire-screen).jpg"

# Long poll - exp rewards, prompts, load screens before cutscene
FINAL_CUTSCENE_WAIT_TIMEOUT = 900.0  # 15 min max; exits early when found
FINAL_CUTSCENE_POLL_INTERVAL = 1.0
FINAL_CUTSCENE_LOG_EVERY = 30.0
FINAL_CUTSCENE_SNAPSHOT_EVERY = 0  # e.g. 60.0 for debug screenshots
FINAL_CUTSCENE_CONFIDENCE = 0.65  # tune with diagnose_state17.py
