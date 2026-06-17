"""Calibration: measure State 12 -> 13 load time until Select All button appears."""

import config

# Force measure-only for this script
config.BATTLE_LOAD_MEASURE_ONLY = True

from main import main

if __name__ == "__main__":
    raise SystemExit(main())
