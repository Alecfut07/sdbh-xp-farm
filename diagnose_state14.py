"""Run with aim_for_enemy screen visible (both lock scenarios)."""

import time

import config
import vision


def startup_countdown() -> None:
    seconds = getattr(config, "STARTUP_COUNTDOWN_SECONDS", 5)
    print("Focus game - aim for enemy screen visible")
    for i in range(seconds, 0, -1):
        print(f"  {i}...")
        time.sleep(1)


def main() -> None:
    print("=== State 14 diagnose ===")
    startup_countdown()

    vision.save_debug_screenshot("diagnose_state14_full.png")

    templates = [
        ("aim mode", config.TEMPLATE_AIM_FOR_ENEMY_TEXT, config.STATE14_AIM_CONFIDENCE),
        (
            "locked",
            config.TEMPLATE_TARGET_LOCK_IN,
            config.STATE14_TARGET_LOCK_IN_CONFIDENCE,
        ),
        (
            "not locked",
            config.TEMPLATE_TARGET_NOT_LOCK_IN,
            config.STATE14_TARGET_NOT_LOCK_IN_CONFIDENCE,
        ),
    ]

    for label, name, conf in templates:
        score = vision.log_best_match(name, conf)
        status = "PASS" if score >= conf else "FAIL"
        print(f"  [{status}] {label} ({name}): {score:.3f}")

    print("\nRun twice: once with target locked, once with target not locked.")


if __name__ == "__main__":
    main()
