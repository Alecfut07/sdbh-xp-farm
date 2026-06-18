"""Tune State 13 Select All detection - run with battle setup screen visible."""

import config
import vision


def main() -> None:
    template = config.TEMPLATE_INITIAL_ROUND1_BATTLE_SETUP_TEXT
    confidence = getattr(config, "STATE13_SELECT_ALL_CONFIDENCE", 0.65)

    print("=== State 13 diagnose (Select All) ===")
    print(f"SCREEN_REGION: {config.SCREEN_REGION}")
    print(f"STATE13_SEARCH_REGION: {getattr(config, 'STATE13_SEARCH_REGION', None)}")
    print()
    path = vision.save_debug_screenshot("diagnose_state13_full.png")
    print(f"Saved: {path}")
    print()
    print("--- Full screen search ---")
    score_full = vision.log_best_match(template, confidence)
    point_full = vision.find_on_screen(template, confidence=confidence)
    print(f"  Score: {score_full:.3f}  PASS: {score_full >= confidence}")
    print(f"  Point: {point_full}")
    print()
    region = getattr(config, "STATE13_SEARCH_REGION", None)
    if region:
        print("--- Bottom-right region search ---")
        score_reg = vision.log_best_match(template, confidence, region=region)
        point_reg = vision.find_on_screen(
            template, confidence=confidence, region=region
        )
        print(f"  Score: {score_reg:.3f}  PASS: {score_reg >= confidence}")
        print(f"  Point: {point_reg}")
        print()
    print("If both FAIL:")
    print("  1. Open diagnose_state13_full.png")
    print("  2. Re-crop initial_round1_battle_setup_text.png from that image")
    print("  3. Include Select All text + button edge (bottom-right)")
    print("  4. Adjust STATE13_SEARCH_REGION to cover that corner")


if __name__ == "__main__":
    main()
