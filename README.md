# SDBH XP Farm

Modular automation for **Super Dragon Ball Heroes: World Mission** on Linux / Steam Deck.
Uses OpenCV template matching for UI state detection and a swappable input backend.

### Required: Disable Steam Input

1. Steam → game → **Properties** → **Controller**
2. Set to **Disable Steam Input**
3. Without this, the virtual gamepad is ignored and inputs fail

### Config

```python
USE_CONTROLLER = True
SCREEN_REGION = (0, 80, 1280, 720)   # windowed 1280x720 on 1280x800 desktop
DEFAULT_CONFIDENCE = 0.65
```

## Setup and run from Desktop Mode with the game window focused and unobstructed

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```
