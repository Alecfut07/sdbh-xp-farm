"""One-shot vision diagnostic - run with the game visible on screen."""

import config
import vision


def main() -> None:
    print("=== Vision Diagnostics ===")
    print(f"SCREEN_REGION: {config.SCREEN_REGION}")
    print(f"DEFAULT_CONFIDENCE: {config.DEFAULT_CONFIDENCE}")
    print()

    path = vision.save_debug_screenshot("diagnose_capture.png")
    print(f"Saved capture: {path}")
    print()

    templates = [
        config.TEMPLATE_SELECT_TOURNAMENT_TEXT,
        config.TEMPLATE_SECRET_BATTLE_TEXT,
        config.TEMPLATE_GREAT_SAIYAMAN_DIALOG_TEXT,
    ]

    for name in templates:
        score = vision.log_best_match(name)
        status = "PASS" if score >= config.DEFAULT_CONFIDENCE else "FAIL"
        print(f"  [{status}] {name}: {score:.3f}")

    print()
    print("Compare logs/diagnose_capture.png side-by-side with templates.")
    print(
        "If scores are 0.3-0.6, lower DEFAULT_CONFIDENCE or re-capture templates on Deck."
    )


if __name__ == "__main__":
    main()
