"""Entry point for SDBH XP farm automation."""

from __future__ import annotations

import time

import logging
import sys
from datetime import datetime

import config
from input_handler import create_input_handler
from state import StateMachine


def setup_logging() -> None:
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = config.LOGS_DIR / f"run_{datetime.now():%Y%m%d_%H%M%S}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )
    logging.info("Logging to %s", log_file)


def main() -> int:
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=== SDBH XP Farm starting ===")
    logger.info(
        "Input mode: %s", "Controller" if config.USE_CONTROLLER else "Keyboard/Mouse"
    )
    logger.info("Templates dir: %s", config.TEMPLATES_DIR)

    if not config.TEMPLATES_DIR.exists():
        logger.error("Templates directory missing: %s", config.TEMPLATES_DIR)
        return 1

    inputs = None
    try:
        inputs = create_input_handler()
        machine = StateMachine(inputs)

        logger.info(
            "Steam Input must be DISABLED for this game. "
            "Focus game window - tournament menu, Secret Battle visible."
        )
        countdown = getattr(config, "STARTUP_COUNTDOWN_SECONDS", 5)
        for i in range(countdown, 0, -1):
            logger.info("Starting in %d...", i)
            time.sleep(1)

        machine.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
        return 130
    except Exception:
        logger.exception("Fatal error - script stopped.")
        return 1
    finally:
        if inputs is not None and hasattr(inputs, "close"):
            inputs.close()

    logger.info("=== SDBH XP Farm finished ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
