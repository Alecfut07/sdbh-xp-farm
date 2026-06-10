"""Game flow state machine."""

from __future__ import annotations

import logging
from enum import Enum, auto

import config
import vision
from input_handler import InputHandler, human_delay

logger = logging.getLogger(__name__)


class GameState(Enum):
    TOURNAMENT_SELECTION = auto()
    CUTSCENE_SKIP = auto()
    DONE = auto()


class StateMachine:
    def __init__(self, inputs: InputHandler) -> None:
        self.inputs = inputs
        self.state = GameState.TOURNAMENT_SELECTION

    def run(self) -> None:
        logger.info("State machine starting at %s", self.state.name)

        while self.state != GameState.DONE:
            if self.state == GameState.TOURNAMENT_SELECTION:
                self._state_tournament_selection()
            elif self.state == GameState.CUTSCENE_SKIP:
                self._state_cutscene_skip()
            else:
                logger.error("Unhandled state: %s", self.state)
                break

        logger.info("State machine finished.")

    # --------------------------------------------------------------
    # State 1: Tournament Selection
    # --------------------------------------------------------------
    def _state_tournament_selection(self) -> None:
        """
        Wait for tournament menu, confirm if Secret Battle is selected, press A.
        """
        logger.info("Entering State 1: Tournament Selection")

        # Optional sanity check - menu header visible
        header = vision.wait_for_element(
            config.TEMPLATE_SECRET_BATTLE_SELECTED,
            timeout=config.DEFAULT_WAIT_TIMEOUT,
            confidence=config.DEFAULT_CONFIDENCE,
        )
        if header is None:
            logger.warning(
                "Could not detect 'Select Tournament' header; continuing anyway"
            )

        # Primary check: highlighted Secret Battle row
        secret_battle = vision.wait_for_element(
            config.TEMPLATE_SECRET_BATTLE_SELECTED,
            timeout=config.DEFAULT_WAIT_TIMEOUT,
            confidence=config.DEFAULT_CONFIDENCE,
        )

        if secret_battle is None:
            logger.error(
                "Secret Battle selection not detected. " "Capture template: %s",
                config.TEMPLATE_SECRET_BATTLE_SELECTED,
            )
            vision.save_debug_screenshot("state1_fail.png")
            self.state = GameState.DONE
            return

        logger.info("Secret Battle selected at %s - pressing A", secret_battle)
        self.inputs.press_button("A")
        human_delay()

        logger.info("Transition: Tournament Selection -> Cutscene Skip")
        self.state = GameState.CUTSCENE_SKIP

    # --------------------------------------------------------------
    # State 2: Cutscene Skip
    # --------------------------------------------------------------
    def _state_cutscene_skip(self) -> None:
        """
        Wait for Great Saiyaman 3 dialog, then press Start to skip.
        Template should include name + dialog text region.
        """
        logger.info("Entering State 2: Cutscene Skip")

        dialog = vision.wait_for_element(
            config.TEMPLATE_GREAT_SAIYAMAN_DIALOG,
            timeout=30.0,  # cutscenes can take a moment to appear
            confidence=config.DEFAULT_CONFIDENCE,
        )

        if dialog is None:
            logger.error(
                "Great Saiyaman dialog not detected. " "Capture template: %s",
                config.TEMPLATE_GREAT_SAIYAMAN_DIALOG,
            )
            vision.save_debug_screenshot("state2_fail.png")
            self.state = GameState.DONE
            return

        logger.info("Dialog confirmed at %s - pressing Start to skip", dialog)
        self.inputs.press_button("Start")
        human_delay()

        logger.info("Cutscene skip complete. Stopping (next state TBD).")
        self.state = GameState.DONE
