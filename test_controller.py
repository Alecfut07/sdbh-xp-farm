"""Send a single A button press to verify UInput works."""

import time

import config
from input_handler import ControllerInputHandler


def main() -> None:
    print("=== Controller Test ===")
    print(f"Device name: {config.CONTROLLER_DEVICE_NAME}")
    print("Focus the game window now...")
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    handler = ControllerInputHandler()
    print("Sending Continue/Confirm (A button)...")
    handler.press_button("Continue/Confirm")
    handler.close()
    print("Done. Did the game react?")


if __name__ == "__main__":
    main()
