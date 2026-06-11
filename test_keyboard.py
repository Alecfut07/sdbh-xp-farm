"""Send keyboard confirm + menu keys to verify PyAutoGUI works."""

import time
import config
from input_handler import PyAutoGUIInputHandler


def main() -> None:
    print("=== Keyboard test ===")
    print(f"Layout: {config.KEYBOARD_LAYOUT}")
    print("Focus the game window now...")
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    handler = PyAutoGUIInputHandler()

    print("Sending Continue/Confirm (Enter)...")
    handler.press_button("Continue/Confirm")
    time.sleep(1)

    print("Sending Open Menu (Z)...")
    handler.press_button("Open Menu")

    print("Done. Did the game react?")


if __name__ == "__main__":
    main()
