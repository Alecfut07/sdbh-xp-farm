# SDBH XP Farm

**Automated XP farming for Super Dragon Ball Heroes: World Mission on Steam Deck / Linux.**

A modular Python bot that navigates tournament setup, battle prep, and post-battle rewards using OpenCV template matching and a virtual Xbox 360 controller.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black)
![Steam Deck](https://img.shields.io/badge/Steam%20Deck-1A9FFF?logo=steam&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Template%20Matching-5C3EE8?logo=opencv&logoColor=white)

---

## ⚠️ Disclaimer

This project is intended strictly for **single-player automation** and **personal use** on your own hardware.

> **Important Risks:**
>
> - **Terms of Service:** Automating gameplay may violate the game's Terms of Service or platform rules (Steam/Bandai Namco).
> - **No Liability:** Use this tool at your own risk. The authors are **not responsible** for any account actions, suspensions, or bans that may occur.
> - **Technical Scope:** This tool **does not** modify game files, memory, or network traffic. It operates solely by:
>   - Sending standard virtual controller inputs (via `evdev`).
>   - Reading screen pixels (via OpenCV template matching).

Please ensure you understand the risks before running the bot.

---

## Features

- **18-state state machine** - Full tournament → battle → reward loop with clear transitions
- **Multi-cycle farming** - Loop indefinitely; cycle 2+ skips EXP item setup (States 8-11)
- **Virtual Xbox 360 controller** - UInput gamepad via `evdev`
- **OpenCV template matching** - Detects UI text/buttons from cropped PNG templates
- **Hybrid timing** - Template polling where reiable; fixed blind waits for slow load screens
- **Analog stick nudges** - Finer aim control in State 14 vs full d-pad steps
- **Structured logging** - Timestamped logs under `logs/` for debugging runs

---

## Why this approach?

1. **Disable Steam Input** for the game in Steam properties.
2. Create a **virtual UInput gamepad** that the game accepts as a real Xbox 360 controller.
3. Map game actions through semantic names (`Continue/Confirm`, `Open Menu`, etc.) in `controls.py`

Screenshots use **`mss`** instead of PyAutoGUI capture for better reliability on Linux.

---

## Prerequisites & Installation

### Requirements

- Steam Deck (Desktop Mode) or Linux PC
- Python 3.10+
- **Super Dragon Ball Heroes: World Mission** game copy from Steam.
- Game window focused and unobstructed during runs.

### Install

```bash
git clone <your-repo-url>
cd sdbh-xp-farm

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Dependencies

| Package         | Purpose                                       |
| :-------------- | :-------------------------------------------- |
| `evdev-binary`  | Virtual Xbox 360 controller (Linux only)      |
| `opencv-python` | Template matching and vision logic            |
| `mss`           | Fast screenshots on Linux                     |
| `numpy`         | Image array processing for OpenCV             |
| `Pillow`        | General image handling                        |
| `pyautogui`     | Keyboard/mouse fallback (not primary on Deck) |

## Configuration

All tunables live in `config.py`.

### Display & Vision

| Setting                | Default              | Description                                              |
| :--------------------- | :------------------- | :------------------------------------------------------- |
| `SCREEN_REGION`        | `(0, 80, 1280, 720)` | Crop region for captures (windowed 720p on 800p desktop) |
| `DEFAULT_CONFIDENCE`   | `0.65`               | Template match threshold (0.0–1.0)                       |
| `DEFAULT_WAIT_TIMEOUT` | `10.0`               | Short UI waits (seconds)                                 |

### Input

| Setting                     | Default                | Description                                       |
| :-------------------------- | :--------------------- | :------------------------------------------------ |
| `USE_CONTROLLER`            | `True`                 | Use virtual gamepad (`False` = keyboard fallback) |
| `CONTROLLER_DEVICE_NAME`    | `sdbh-xp-farm-gamepad` | UInput device name                                |
| `CONTROLLER_BUTTON_HOLD`    | `0.08`                 | Button press duration (seconds)                   |
| `STARTUP_COUNTDOWN_SECONDS` | `5`                    | Countdown before state machine starts             |

### Cycle Control

| Setting                            | Default | Description                                      |
| :--------------------------------- | :------ | :----------------------------------------------- |
| `RUN_CYCLES`                       | `0`     | `0` = infinite; `1` = single run; `N` = N cycles |
| `CYCLE_DELAY_SECONDS`              | `10.0`  | Pause between cycles (after State 18)            |
| `SKIP_EXP_SETUP_AFTER_FIRST_CYCLE` | `True`  | Cycle 2+ skips States 8–11 (EXP setup)           |

### Fixed Waits (No Template Detection)

| Setting                          | Default | Description                                      |
| :------------------------------- | :------ | :----------------------------------------------- |
| `BATTLE_LOAD_FIXED_WAIT_SECONDS` | `60.0`  | State 12 → State 13 battle setup delay (seconds) |
| `AIM_PHASE_FIXED_WAIT_SECONDS`   | `28.0`  | State 13 → State 14 aim phase delay (seconds)    |

### State 14 — Analog Aim

| Setting                      | Default | Description                                     |
| :--------------------------- | :------ | :---------------------------------------------- |
| `AIM_USE_ANALOG_LEFT`        | `True`  | Use left stick nudge instead of D-pad           |
| `AIM_ANALOG_LEFT_STRENGTH`   | `0.75`  | Stick deflection 0.0–1.0 (lower = smaller step) |
| `AIM_ANALOG_LEFT_HOLD`       | `0.06`  | How long stick stays left (seconds)             |
| `AIM_TARGET_DPAD_LEFT_COUNT` | `3`     | Number of nudges before pressing A              |

### Long Polls (Post-Battle)

| Setting                       | Default | Description                             |
| :---------------------------- | :------ | :-------------------------------------- |
| `DISCARD_WAIT_TIMEOUT`        | `900.0` | Max wait for Discard button (State 15)  |
| `FINAL_CUTSCENE_WAIT_TIMEOUT` | `900.0` | Max wait for cutscene dialog (State 17) |

### Timing History

Timing measurements are automatically logged to JSON files for calibration analysis:

- **`logs/battle_load_times.json`**: Records latency for State 12 → State 13 (Battle Load).
- **`logs/aim_phase_times.json`**: Records latency for State 13 → State 14 (Aim Phase).

### Setup (States 1–11)

- The bot runs States 1–18 per cycle. Cycle 1 runs all states. Cycle 2+ skips States 8–11 (EXP item already configured) and jumps from State 7 → State 12.

| State | Name                               | Detection Template                                           | Action      |
| :---: | :--------------------------------- | :----------------------------------------------------------- | :---------- |
|   1   | Tournament Selection               | `secret_battle_text.png`                                     | `A`         |
|   2   | Cutscene Skip                      | `great_saiyaman_dialog_text.png`                             | `Start`     |
|   3   | Register Team                      | `register_team_text.png`                                     | `A`         |
|   4   | Confirm Register Team              | `confirm_register_this_team_text.png`                        | `A`         |
|   5   | Select Hero Robo Round             | `select_the_round_your_super_hero_robo_activates_text.png`   | `A`         |
|   6   | Confirm Hero Robo Round            | `confirm_the_round_your_super_hero_robo_activates_text.png`  | `A`         |
|   7   | Continue Hero Robo Round           | `continue_the_round_your_super_hero_robo_activates_text.png` | `A`         |
|   8   | Set Item EXP _(Cycle 1 only)_      | `set_item_exp_logo.png`                                      | `A`         |
|   9   | Activate EXP 1.5x _(Cycle 1 only)_ | `activate_exp_1_5_x_logo.png`                                | D-pad Right |
|  10   | Change EXP to 3x _(Cycle 1 only)_  | `change_exp_1_5_x_to_exp_3_x_logo.png`                       | `LB`        |
|  11   | Selected EXP 3x _(Cycle 1 only)_   | `selected_exp_3_x_text.png`                                  | `A`         |

### Battle (States 12–14)

| State | Name                 | Detection Method                              | Action Sequence                                               |
| :---: | :------------------- | :-------------------------------------------- | :------------------------------------------------------------ |
|  12   | Finish Item Selected | `finish_item_selected_text.png`               | `Down`, `A`                                                   |
|  13   | Battle Setup         | Fixed Wait (`BATTLE_LOAD_FIXED_WAIT_SECONDS`) | `Y`, `Down`×6, `Y`, `Up`×6, `RB`, `Up`×6, `RB`, `Left`×2, `A` |
|  14   | Aim for Enemy        | Fixed Wait (`AIM_PHASE_FIXED_WAIT_SECONDS`)   | Analog Left Nudge ×N (or D-pad), `A`                          |

### Post-Battle (States 15–18)

| State | Name                | Detection Method                               | Action Sequence       |
| :---: | :------------------ | :--------------------------------------------- | :-------------------- |
|  15   | Discard             | Poll `discard_button_text.png` (max 900s)      | `A`                   |
|  16   | Confirm Discard     | No Wait (uses `human_delay` from State 15)     | `Left`×1, `A`         |
|  17   | Skip Final Cutscene | Poll `skip_final_cutscene_text.png` (max 900s) | `Start`               |
|  18   | Claim Reward        | No Wait (uses `human_delay` from State 17)     | `A` → Loop to State 1 |

### Detection Methods

The state machine uses four distinct strategies to detect game states:

- **Template**: Polls the screen continuously until a specific PNG crop matches the confidence threshold (e.g., `0.65`). Used for most UI buttons and text.
- **Fixed Wait**: Executes a blind sleep for a calibrated duration. Used exclusively when template matching is unreliable (e.g., during battle loading or aim phases).
- **Poll**: A long-running template search (up to 900s) with progress logging. Exits immediately upon detection; used for unpredictable post-battle screens.
- **No Wait**: Executes input immediately without any new detection, relying on the `human_delay` from the previous state to ensure the game is ready.

## Usage

## Before Starting

Complete the following steps before running the bot:

- [ ] **Disable Steam Input**: Ensure this is turned off for _Super Dragon Ball Heroes: World Mission_ in your Steam Deck settings.
- [ ] **Launch the Game**: Start the game and navigate to the **Tournament Menu** until the **Secret Battle** option is visible.
- [ ] **Focus the Window**: Make sure the game window is active and not covered by any overlays (Steam, Discord, etc.).
- [ ] **Run the Bot**: Execute `main.py`. A **5-second countdown** will begin, giving you time to confirm the window focus.

> [!WARNING]
> If Steam Input is not disabled, the virtual controller inputs will be ignored by the game.

### Option 1: Run the Bot

Activate the virtual environment and start the automation:

```bash
source .venv/bin/activate
python3 main.py
```

Then click on the game window.

### Option 2: Helper Script

For a quicker start without manually activating the environment, make the script executable and run it:

```bash
chmod +x run.sh
./run.sh
```

Then click on the game window.

## Logs

The bot generates detailed logs and debug artifacts in the `logs/` directory:

| Path                           | Contents                                                  |
| :----------------------------- | :-------------------------------------------------------- |
| `logs/run_YYYYMMDD_HHMMSS.log` | Full execution log with state transitions and errors      |
| `logs/battle_load_times.json`  | Timing history for State 12 → State 13 (Battle Load)      |
| `logs/aim_phase_times.json`    | Timing history for State 13 → State 14 (Aim Phase)        |
| `logs/state*_fail.png`         | Debug screenshots captured automatically on state failure |
