"""Measure time from state 13 final A to aim_for_enemy mode."""

import config

config.AIM_PHASE_MEASURE_ONLY = True

from main import main

if __name__ == "__main__":
    raise SystemExit(main())
