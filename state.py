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
    REGISTER_TEAM = auto()
    CONFIRM_REGISTER_TEAM = auto()
    SELECT_HERO_ROBO_ROUND = auto()
    CONFIRM_HERO_ROBO_ROUND = auto()
    CONTINUE_HERO_ROBO_ROUND = auto()
    SET_ITEM_EXP = auto()
    ACTIVATE_EXP_1_5_X = auto()
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
            elif self.state == GameState.REGISTER_TEAM:
                self._state_register_team()
            elif self.state == GameState.CONFIRM_REGISTER_TEAM:
                self._state_confirm_register_team()
            elif self.state == GameState.SELECT_HERO_ROBO_ROUND:
                self._state_select_hero_robo_round()
            elif self.state == GameState.CONFIRM_HERO_ROBO_ROUND:
                self._state_confirm_hero_robo_round()
            elif self.state == GameState.CONTINUE_HERO_ROBO_ROUND:
                self._state_continue_hero_robo_round()
            elif self.state == GameState.SET_ITEM_EXP:
                self._state_set_item_exp()
            elif self.state == GameState.ACTIVATE_EXP_1_5_X:
                self._state_activate_exp_1_5_x()
            else:
                logger.error("Unhandled state: %s", self.state)
                break

        logger.info("State machine finished.")

    # --------------------------------------------------------------
    # State 1: Tournament Selection
    # --------------------------------------------------------------
    def _state_tournament_selection(self) -> None:
        """
        Wait for Secret Battle text on screen, then confirm.
        Primary matcher: secret_battle_text.png
        (select_tournament_text is unreliable on Deck - optional check only)
        """
        logger.info("Entering State 1: Tournament Selection")

        # Optional non-blocking check - log score but don't require it
        vision.log_best_match(config.TEMPLATE_SELECT_TOURNAMENT_TEXT)

        secret_battle = vision.wait_for_element(
            config.TEMPLATE_SECRET_BATTLE_TEXT,
            timeout=config.DEFAULT_WAIT_TIMEOUT,
            confidence=config.DEFAULT_CONFIDENCE,
        )

        if secret_battle is None:
            logger.error(
                "Secret Battle not detected. Check template: %s",
                config.TEMPLATE_SECRET_BATTLE_TEXT,
            )
            vision.save_debug_screenshot("state1_fail.png")
            logger.info(
                "Compare fail screenshot to reference: %s",
                config.TEMPLATE_SELECT_TOURNAMENT_FULL,
            )
            self.state = GameState.DONE
            return

        logger.info(
            "Secret Battle found at %s - pressing Continue/Confirm",
            secret_battle,
        )
        self.inputs.press_button("Continue/Confirm")
        human_delay()

        logger.info("Transition: Tournament Selection -> Cutscene Skip")
        self.state = GameState.CUTSCENE_SKIP

    # --------------------------------------------------------------
    # State 2: Cutscene Skip
    # --------------------------------------------------------------
    def _state_cutscene_skip(self) -> None:
        """
        Wait for Great Saiyaman 3 dialog text, then skip cutscene.
        Matcher: great_saiyaman_dialog_text.png
        """
        logger.info("Entering State 2: Cutscene Skip")

        dialog = vision.wait_for_element(
            config.TEMPLATE_GREAT_SAIYAMAN_DIALOG_TEXT,
            timeout=30.0,  # cutscenes can take a moment to appear
            confidence=config.DEFAULT_CONFIDENCE,
        )

        if dialog is None:
            logger.error(
                "Great Saiyaman dialog not detected. Check template: %s",
                config.TEMPLATE_GREAT_SAIYAMAN_DIALOG_TEXT,
            )
            vision.save_debug_screenshot("state2_fail.png")
            logger.info(
                "Compare fail screenshot to reference: %s",
                config.TEMPLATE_GREAT_SAIYAMAN_DIALOG_FULL,
            )
            self.state = GameState.DONE
            return

        logger.info("Dialog confirmed at %s - pressing Open Menu to skip", dialog)
        self.inputs.press_button("Open Menu")
        human_delay()

        logger.info("Cutscene skip complete.")
        logger.info("Transition: Cutscene Skip -> Register Team")
        self.state = GameState.REGISTER_TEAM

    # --------------------------------------------------------------
    # State 3: Register Team
    # --------------------------------------------------------------
    def _state_register_team(self) -> None:
        """
        Wait for Register Team button text, then press A to confirm.
        Matcher: register_team_text.png
        """
        logger.info("Entering State 3: Register Team")

        register_team = vision.wait_for_element(
            config.TEMPLATE_REGISTER_TEAM_TEXT,
            timeout=config.DEFAULT_WAIT_TIMEOUT,
            confidence=config.DEFAULT_CONFIDENCE,
        )

        if register_team is None:
            logger.error(
                "Register Team button not detected. Check template: %s",
                config.TEMPLATE_REGISTER_TEAM_TEXT,
            )
            vision.save_debug_screenshot("state3_fail.png")
            logger.info(
                "Compare fail screenshot to reference: %s",
                config.TEMPLATE_REGISTER_TEAM_FULL,
            )
            self.state = GameState.DONE
            return

        logger.info(
            "Register Team found at %s - pressing Continue/Confirm (A)",
            register_team,
        )
        self.inputs.press_button("Continue/Confirm")
        human_delay()

        logger.info("Register Team confirmed.")
        logger.info("Transition: Register Team -> Confirm Register Team")
        self.state = GameState.CONFIRM_REGISTER_TEAM

    # --------------------------------------------------------------
    # State 4: Confirm Register Team (Yes)
    # --------------------------------------------------------------
    def _state_confirm_register_team(self) -> None:
        """
        Wait for Yes confirmation button, then press A.
        Matcher: confirm_register_this_team_text.png
        """
        logger.info("Entering State 4: Confirm Register Team (Yes)")

        yes_button = vision.wait_for_element(
            config.TEMPLATE_CONFIRM_REGISTER_TEAM_TEXT,
            timeout=config.DEFAULT_WAIT_TIMEOUT,
            confidence=config.DEFAULT_CONFIDENCE,
        )

        if yes_button is None:
            logger.error(
                "Yes button not detected. Check template: %s",
                config.TEMPLATE_CONFIRM_REGISTER_TEAM_TEXT,
            )
            vision.save_debug_screenshot("state4_fail.png")
            logger.info(
                "Compare fail screenshot to reference: %s",
                config.TEMPLATE_CONFIRM_REGISTER_TEAM_FULL,
            )
            self.state = GameState.DONE
            return
        logger.info(
            "Yes button found at %s - pressing Continue/Confirm (A)",
            yes_button,
        )
        self.inputs.press_button("Continue/Confirm")
        human_delay()

        logger.info("Team registration confirmed.")
        logger.info("Transition: Confirm Register Team -> Select Hero Robo Round")
        self.state = GameState.SELECT_HERO_ROBO_ROUND

    # --------------------------------------------------------------
    # State 5: Select Hero Robo Round
    # --------------------------------------------------------------
    def _state_select_hero_robo_round(self) -> None:
        """
        Wait for OK button on Super Hero Robo round selection screen, then press A.
        Matcher: select_the_round_your_super_hero_robo_activates_text.png
        """
        logger.info("Entering State 5: Select Hero Robo Round (OK)")

        ok_button = vision.wait_for_element(
            config.TEMPLATE_SELECT_HERO_ROBO_ROUND_TEXT,
            timeout=config.DEFAULT_WAIT_TIMEOUT,
            confidence=config.DEFAULT_CONFIDENCE,
        )

        if ok_button is None:
            logger.error(
                "OK button not detected. Check template: %s",
                config.TEMPLATE_SELECT_HERO_ROBO_ROUND_TEXT,
            )
            vision.save_debug_screenshot("state5_fail.png")
            logger.info(
                "Compare fail screenshot to reference: %s",
                config.TEMPLATE_SELECT_HERO_ROBO_ROUND_FULL,
            )
            self.state = GameState.DONE
            return

        logger.info(
            "OK button found at %s - pressing Continue/Confirm (A)",
            ok_button,
        )
        self.inputs.press_button("Continue/Confirm")
        human_delay()

        logger.info("Hero Robo round confirmed.")
        logger.info("Transition: Select Hero Robo Round -> Confirm Hero Robo Round")
        self.state = GameState.CONFIRM_HERO_ROBO_ROUND

    # --------------------------------------------------------------
    # State 6: Confirm Hero Robo Round (Yes)
    # --------------------------------------------------------------
    def _state_confirm_hero_robo_round(self) -> None:
        """
        Wait for Yes confirmation on Hero Robo round screen, then press A.
        Matcher: confirm_the_round_your_super_hero_robo_activates_text.png
        """
        logger.info("Entering State 6: Confirm Hero Robo Round (Yes)")

        yes_button = vision.wait_for_element(
            config.TEMPLATE_CONFIRM_HERO_ROBO_ROUND_TEXT,
            timeout=config.DEFAULT_WAIT_TIMEOUT,
            confidence=config.DEFAULT_CONFIDENCE,
        )

        if yes_button is None:
            logger.error(
                "Yes button not detected. Check template: %s",
                config.TEMPLATE_CONFIRM_HERO_ROBO_ROUND_TEXT,
            )
            vision.save_debug_screenshot("state6_fail.png")
            logger.info(
                "Compare fail screenshot to reference: %s",
                config.TEMPLATE_CONFIRM_HERO_ROBO_ROUND_FULL,
            )
            self.state = GameState.DONE
            return

        logger.info(
            "Yes button found at %s - pressing Continue/Confirm (A)",
            yes_button,
        )
        self.inputs.press_button("Continue/Confirm")
        human_delay()

        logger.info("Hero Robo round registration confirmed.")
        logger.info("Transition: Confirm Hero Robo Round -> Continue Hero Robo Round")
        self.state = GameState.CONTINUE_HERO_ROBO_ROUND

    # --------------------------------------------------------------
    # State 7: Continue Hero Robo Round
    # --------------------------------------------------------------
    def _state_continue_hero_robo_round(self) -> None:
        """
        Wait for Continue button, then press A.
        Matcher: continue_the_round_your_super_hero_robo_activates_text.png
        """
        logger.info("Entering State 7: Continue Hero Robo Round")

        continue_button = vision.wait_for_element(
            config.TEMPLATE_CONTINUE_HERO_ROBO_ROUND_TEXT,
            timeout=config.DEFAULT_WAIT_TIMEOUT,
            confidence=config.DEFAULT_CONFIDENCE,
        )

        if continue_button is None:
            logger.error(
                "Continue button not detected. Check template: %s",
                config.TEMPLATE_CONTINUE_HERO_ROBO_ROUND_TEXT,
            )
            vision.save_debug_screenshot("state7_fail.png")
            logger.info(
                "Compare fail screenshot to reference: %s",
                config.TEMPLATE_CONTINUE_HERO_ROBO_ROUND_FULL,
            )
            self.state = GameState.DONE
            return

        logger.info(
            "Continue button found at %s - pressing Continue/Confirm (A)",
            continue_button,
        )
        self.inputs.press_button("Continue/Confirm")
        human_delay()

        logger.info("Continue confirmed.")
        logger.info("Transition: Continue Hero Robo Round -> Set Item EXP")
        self.state = GameState.SET_ITEM_EXP

    # --------------------------------------------------------------
    # State 8: Set Item EXP (1.5x logo)
    # --------------------------------------------------------------
    def _state_set_item_exp(self) -> None:
        """
        Wait for exp 1.5x logo on Set Item EXP screen, then press A to select.
        Matcher: set_item_exp_logo.png
        """
        logger.info("Entering State 8: Set Item EXP (1.5x logo)")

        exp_logo = vision.wait_for_element(
            config.TEMPLATE_SET_ITEM_EXP_LOGO,
            timeout=config.DEFAULT_WAIT_TIMEOUT,
            confidence=config.DEFAULT_CONFIDENCE,
        )

        if exp_logo is None:
            logger.error(
                "exp 1.5x logo not detected. Check template: %s",
                config.TEMPLATE_SET_ITEM_EXP_LOGO,
            )
            vision.save_debug_screenshot("state8_fail.png")
            logger.info(
                "Compare fail screenshot to reference: %s",
                config.TEMPLATE_SET_ITEM_EXP_FULL,
            )
            self.state = GameState.DONE
            return

        logger.info(
            "exp 1.5x logo found at %s - pressing Continue/Confirm (A)",
            exp_logo,
        )
        self.inputs.press_button("Continue/Confirm")
        human_delay()

        logger.info("exp 1.5x item selected.")
        logger.info("Transition: Set Item EXP -> Activate EXP 1.5x")
        self.state = GameState.ACTIVATE_EXP_1_5_X

    # --------------------------------------------------------------
    # State 9: Activate EXP 1.5x (arrow right)
    # --------------------------------------------------------------
    def _state_activate_exp_1_5_x(self) -> None:
        """
        Wait for arrow-right logo on exp 1.5x screen, then press D-pad Right.
        Matcher: activate_exp_1_5_x_logo.png
        """
        logger.info("Entering State 9: Activate EXP 1.5x (arrow right)")

        arrow_logo = vision.wait_for_element(
            config.TEMPLATE_ACTIVATE_EXP_1_5_X_LOGO,
            timeout=config.DEFAULT_WAIT_TIMEOUT,
            confidence=config.DEFAULT_CONFIDENCE,
        )

        if arrow_logo is None:
            logger.error(
                "Arrow right logo not detected. Check template: %s",
                config.TEMPLATE_ACTIVATE_EXP_1_5_X_LOGO,
            )
            vision.save_debug_screenshot("state9_fail.png")
            logger.info(
                "Compare fail screenshot to reference: %s",
                config.TEMPLATE_EXP_1_5_X_FULL,
            )
            self.state = GameState.DONE
            return

        logger.info(
            "Arrow right logo found at %s - pressing Move Right (D-pad Right)",
            arrow_logo,
        )
        self.inputs.press_button("Move Right")
        human_delay()

        logger.info("EXP 1.5x activated. Stopping (next state TBD).")
        self.state = GameState.DONE
