"""Game flow state machine."""

from __future__ import annotations

import logging
from enum import Enum, auto

import config
import vision
from input_handler import InputHandler, human_delay, ControllerInputHandler

import timing
import time

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
    CHANGE_EXP_TO_3_X = auto()
    SELECTED_EXP_3_X = auto()
    FINISH_ITEM_SELECTED = auto()
    INITIAL_ROUND1_BATTLE_SETUP = auto()
    AIM_FOR_ENEMY = auto()
    DISCARD = auto()
    CONFIRM_DISCARD = auto()
    SKIP_FINAL_CUTSCENE = auto()
    CLAIM_REWARD = auto()
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
            elif self.state == GameState.CHANGE_EXP_TO_3_X:
                self._state_change_exp_to_3_x()
            elif self.state == GameState.SELECTED_EXP_3_X:
                self._state_selected_exp_3_x()
            elif self.state == GameState.FINISH_ITEM_SELECTED:
                self._state_finish_item_selected()
            elif self.state == GameState.INITIAL_ROUND1_BATTLE_SETUP:
                self._state_initial_round1_battle_setup()
            elif self.state == GameState.AIM_FOR_ENEMY:
                self._state_aim_for_enemy()
            elif self.state == GameState.DISCARD:
                self._state_discard()
            elif self.state == GameState.CONFIRM_DISCARD:
                self._state_confirm_discard()
            elif self.state == GameState.SKIP_FINAL_CUTSCENE:
                self._state_skip_final_cutscene()
            elif self.state == GameState.CLAIM_REWARD:
                self._state_claim_reward()
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

        logger.info("EXP 1.5x activated.")
        logger.info("Transition: Activate EXP 1.5x -> Change EXP to 3x")
        self.state = GameState.CHANGE_EXP_TO_3_X

    # --------------------------------------------------------------
    # State 10: Change EXP 1.5x to 3x (Arrow Left Logo -> Press LB)
    # --------------------------------------------------------------
    def _state_change_exp_to_3_x(self) -> None:
        """
        Wait for arrow-left logo, then press LB to switch to 3x.
        Matcher: change_exp_1_5_x_to_exp_3_x_logo.png
        """
        logger.info("Entering State 10: Change EXP to 3x (arrow left logo -> press LB)")

        arrow_logo = vision.wait_for_element(
            config.TEMPLATE_CHANGE_EXP_1_5_X_TO_3_X_LOGO,
            timeout=config.DEFAULT_WAIT_TIMEOUT,
            confidence=config.DEFAULT_CONFIDENCE,
        )

        if arrow_logo is None:
            logger.error(
                "Arrow left logo not detected. Check template: %s",
                config.TEMPLATE_CHANGE_EXP_1_5_X_TO_3_X_LOGO,
            )
            vision.save_debug_screenshot("state10_fail.png")
            logger.info(
                "Compare fail screenshot to reference: %s",
                config.TEMPLATE_EXP_1_5_X_FULL,
            )
            self.state = GameState.DONE
            return

        logger.info(
            "Arrow left logo found at %s - pressing Switch Tab (Left) (LB)",
            arrow_logo,
        )
        self.inputs.press_button("Switch Tab (Left)")
        human_delay()

        logger.info("EXP switched to 3x.")
        logger.info("Transition: Change EXP to 3x -> Selected EXP 3x")
        self.state = GameState.SELECTED_EXP_3_X

    # --------------------------------------------------------------
    # State 11: Selected EXP 3x
    # --------------------------------------------------------------
    def _state_selected_exp_3_x(self) -> None:
        """
        Wait for Selected box on 3x EXP screen, then press A.
        Matcher: selected_exp_3_x_text.png
        """
        logger.info("Entering State 11: Selected EXP 3x")

        selected_box = vision.wait_for_element(
            config.TEMPLATE_SELECTED_EXP_3_X_TEXT,
            timeout=config.DEFAULT_WAIT_TIMEOUT,
            confidence=config.DEFAULT_CONFIDENCE,
        )

        if selected_box is None:
            logger.error(
                "Selected box not detected. Check template: %s",
                config.TEMPLATE_SELECTED_EXP_3_X_TEXT,
            )
            vision.save_debug_screenshot("state11_fail.png")
            logger.info(
                "Compare fail screenshot to reference: %s",
                config.TEMPLATE_SELECTED_EXP_3_X_FULL,
            )
            self.state = GameState.DONE
            return

        logger.info(
            "Selected box found at %s - pressing Continue/Confirm (A)",
            selected_box,
        )
        self.inputs.press_button("Continue/Confirm")
        human_delay()

        logger.info("EXP 3x selection confirmed.")
        logger.info("Transition: Selected EXP 3x -> Finish Item Selected")
        self.state = GameState.FINISH_ITEM_SELECTED

    # ----------------------------------------------------------------
    # State 12: Finish Item Selected (Finished -> D-pad Down, then A)
    # ----------------------------------------------------------------
    def _state_finish_item_selected(self) -> None:
        """
        Wait for "Finished" box, press D-pad Down to highlight, then press A.
        Matcher: finish_item_selected_text.png
        """
        logger.info("Entering State 12: Finish Item Selected (Finished)")

        finished_box = vision.wait_for_element(
            config.TEMPLATE_FINISH_ITEM_SELECTED_TEXT,
            timeout=config.DEFAULT_WAIT_TIMEOUT,
            confidence=config.DEFAULT_CONFIDENCE,
        )

        if finished_box is None:
            logger.error(
                "Finished box not detected. Check template: %s",
                config.TEMPLATE_FINISH_ITEM_SELECTED_TEXT,
            )
            vision.save_debug_screenshot("state12_fail.png")
            logger.info(
                "Compare fail screenshot to reference: %s",
                config.TEMPLATE_FINISH_ITEM_SELECTED_FULL,
            )
            self.state = GameState.DONE
            return

        logger.info(
            "Finished box found at %s - pressing Move Down (D-pad Down)",
            finished_box,
        )
        self.inputs.press_button("Move Down")
        human_delay()

        logger.info("Pressing Continue/Confirm (A)")
        self.inputs.press_button("Continue/Confirm")
        timing.mark_battle_load_start()
        human_delay()

        logger.info("Finish item confirmed.")
        logger.info(
            "Transition -> State 13 (fixed wait %.0fs, then battle setup)",
            config.BATTLE_LOAD_FIXED_WAIT_SECONDS,
        )
        self.state = GameState.INITIAL_ROUND1_BATTLE_SETUP

    def _press_repeated(self, action: str, count: int) -> None:
        """Press the same control action multiple times with human-like delays."""
        for i in range(count):
            logger.info("Repeated press %d/%d: %s", i + 1, count, action)
            self.inputs.press_button(action)
            human_delay()

    # --------------------------------------------------------------
    # State 13: Initial Round 1 Battle Setup
    # --------------------------------------------------------------
    def _state_initial_round1_battle_setup(self) -> None:
        """
        Approach 1: fixed blind wait after State 12 A press.
        Sequence: Y -> Down x6 -> Y -> Up x6 -> RB -> Up x6 -> RB -> Left x2 -> A
        """
        logger.info("Entering State 13: Initial Round 1 Battle Setup")

        wait_s = config.BATTLE_LOAD_FIXED_WAIT_SECONDS
        logger.info(
            "Batle load: fixed blind wait %.0fs (no template detection)", wait_s
        )

        # Optional: log progress every 15s while waiting
        log_every = getattr(config, "BATTLE_LOAD_LOG_EVERY", 15.0)
        elapsed = 0.0
        while elapsed < wait_s:
            chunk = min(log_every, wait_s - elapsed)
            time.sleep(chunk)
            elapsed += chunk
            if elapsed < wait_s:
                logger.info(
                    "Still waiting for battle setup... %.0fs / %.0fs",
                    elapsed,
                    wait_s,
                )

        total_elapsed = timing.mark_battle_load_end(found=True)
        logger.info(
            "Fixed wait complete (%.2fs) - starting battle setup sequence",
            total_elapsed or wait_s,
        )

        if config.BATTLE_LOAD_MEASURE_ONLY:
            logger.info("BATTLE_LOAD_MEASURE_ONLY=True - stopping after wait")
            self.state = GameState.DONE
            return

        # Y button
        logger.info("Step 1: Select all cards (Y)")
        self.inputs.press_button("Search/Sort")
        human_delay()

        # D-pad Down x6
        logger.info(
            "Step 2: Move down all cards x%d", config.BATTLE_SETUP_DPAD_DOWN_COUNT
        )
        self._press_repeated("Move Down", config.BATTLE_SETUP_DPAD_DOWN_COUNT)

        # Y button
        logger.info("Step 3: Select back to Gine (Y)")
        self.inputs.press_button("Search/Sort")
        human_delay()

        # D-pad Up x6
        logger.info(
            "Step 4: Move Gine all the way up x%d", config.BATTLE_SETUP_DPAD_UP_COUNT
        )
        self._press_repeated("Move Up", config.BATTLE_SETUP_DPAD_UP_COUNT)

        # RB button
        logger.info("Step 5: Switch to Gogeta SSJ4 (RB)")
        self.inputs.press_button("Switch Tab (Right)")
        human_delay()

        # D-pad Up x6
        logger.info(
            "Step 6: Move Gogeta SSJ4 all the way up x%d",
            config.BATTLE_SETUP_DPAD_UP_COUNT,
        )
        self._press_repeated("Move Up", config.BATTLE_SETUP_DPAD_UP_COUNT)

        # RB button
        logger.info("Step 7: Switch to Vegeta (RB)")
        self.inputs.press_button("Switch Tab (Right)")
        human_delay()

        # D-pad Left x2
        logger.info(
            "Step 8: Move Vegeta to the left x%d", config.BATTLE_SETUP_DPAD_LEFT_COUNT
        )
        self._press_repeated("Move Left", config.BATTLE_SETUP_DPAD_LEFT_COUNT)

        # A button
        logger.info("Step 9: Continue/Confirm (A)")
        self.inputs.press_button("Continue/Confirm")
        timing.mark_aim_phase_start()
        human_delay()

        logger.info("Battle setup complete.")
        logger.info("Transition: State 13 -> State 14 (Aim for Enemy)")
        self.state = GameState.AIM_FOR_ENEMY

    def _press_aim_left(self, count: int) -> None:
        """State 14 aim: analog nudge or normal d-pad left."""
        use_analog = getattr(config, "AIM_USE_ANALOG_LEFT", False)

        for i in range(count):
            logger.info("Aim left press %d/%d", i + 1, count)

            if use_analog and isinstance(self.inputs, ControllerInputHandler):
                human_delay(
                    config.AIM_ANALOG_LEFT_DELAY_MIN,
                    config.AIM_ANALOG_LEFT_DELAY_MAX,
                )
                self.inputs.nudge_left(
                    strength=config.AIM_ANALOG_LEFT_STRENGTH,
                    hold_s=config.AIM_ANALOG_LEFT_HOLD,
                )
            else:
                self.inputs.press_button("Move Left")
                human_delay()

    # --------------------------------------------------------------
    # State 14: Aim for Enemy
    # --------------------------------------------------------------
    def _state_aim_for_enemy(self) -> None:
        """
        Approach 1: fixed blind wait after State 13 final A press.
        Sequence: D-pad Left x2 -> A
        """
        logger.info("Entering State 14: Aim for Enemy")

        wait_s = config.AIM_PHASE_FIXED_WAIT_SECONDS
        logger.info("Aim phase: fixed blind wait %.0fs (no template detection)", wait_s)

        log_every = getattr(config, "AIM_PHASE_LOG_EVERY", 10.0)
        elapsed = 0.0
        while elapsed < wait_s:
            chunk = min(log_every, wait_s - elapsed)
            time.sleep(chunk)
            elapsed += chunk
            if elapsed < wait_s:
                logger.info(
                    "Still waiting for aim phase... %.0fs / %.0fs",
                    elapsed,
                    wait_s,
                )

        total_elapsed = timing.mark_aim_phase_end(found=True)
        logger.info(
            "Fixed wait complete (%.2fs) - starting aim sequence",
            total_elapsed or wait_s,
        )

        if config.AIM_PHASE_MEASURE_ONLY:
            logger.info("AIM_PHASE_MEASURE_ONLY=True - stopping after wait")
            self.state = GameState.DONE

        # D-pad Left x2
        logger.info(
            "Step 1: Move Left x%d",
            config.AIM_TARGET_DPAD_LEFT_COUNT,
        )
        self._press_aim_left(config.AIM_TARGET_DPAD_LEFT_COUNT)

        # A button
        logger.info("Step 2: Continue/Confirm (A)")
        self.inputs.press_button("Continue/Confirm")
        human_delay()

        logger.info("Aim for enemy complete.")
        logger.info("Transition: State 14 -> State 15 (wait for Discard)")
        self.state = GameState.DISCARD

    def _wait_for_discard_button(self) -> vision.Point | None:
        """Poll until Discard text appears; log progress periodically."""
        template = config.TEMPLATE_DISCARD_BUTTON_TEXT
        timeout = config.DISCARD_WAIT_TIMEOUT
        confidence = config.DISCARD_CONFIDENCE
        poll_interval = config.DISCARD_POLL_INTERVAL
        log_every = getattr(config, "DISCARD_LOG_EVERY", 30.0)
        snapshot_every = getattr(config, "DISCARD_SNAPSHOT_EVERY", 0.0)

        deadline = time.monotonic() + timeout
        next_log = time.monotonic() + log_every
        next_snapshot = (
            time.monotonic() + snapshot_every if snapshot_every > 0 else float("inf")
        )
        start = time.monotonic()

        while time.monotonic() < deadline:
            point = vision.find_on_screen(template, confidence=confidence)
            if point is not None:
                elapsed = time.monotonic() - start
                logger.info(
                    "Found %s at %s after %.1fs",
                    template,
                    point,
                    elapsed,
                )
                return point

            now = time.monotonic()

            if now >= next_log:
                elapsed = now - start
                logger.info(
                    "Still waiting for Discard... %.0fs / %.0fs",
                    elapsed,
                    timeout,
                )
                vision.log_best_match(template, confidence)
                next_log = now + log_every

            if now >= next_snapshot:
                vision.save_debug_screenshot(f"state15_discard_wait_{int(elapsed)}.png")
                next_snapshot = now + snapshot_every

            time.sleep(poll_interval)

        vision.log_best_match(template, confidence)
        return None

    # --------------------------------------------------------------
    # State 15: Discard
    # --------------------------------------------------------------
    def _state_discard(self) -> None:
        """
        Battle runs on its own after State 14.
        Poll until Discard button text appears, then press A.
        Matcher: discard_button_text.png
        """
        logger.info("Entering State 15: Discard")
        logger.info(
            "Waiting for battle to finish - polling for %s (timeout=%.0fs)",
            config.TEMPLATE_DISCARD_BUTTON_TEXT,
            config.DISCARD_WAIT_TIMEOUT,
        )

        discard_button = self._wait_for_discard_button()

        if discard_button is None:
            logger.error(
                "Discard button not detected within %.0fs. Check template: %s",
                config.DISCARD_WAIT_TIMEOUT,
                config.TEMPLATE_DISCARD_BUTTON_TEXT,
            )
            vision.save_debug_screenshot("state15_discard_fail.png")
            logger.info(
                "Compare fail screenshot to reference: %s",
                config.TEMPLATE_DISCARD_BUTTON_FULL,
            )
            self.state = GameState.DONE
            return

        logger.info(
            "Discard button found at %s - pressing Continue/Confirm (A)",
            discard_button,
        )
        self.inputs.press_button("Continue/Confirm")
        human_delay()

        logger.info("Discard confirmed.")
        logger.info("Transition: State 15 -> State 16 (Confirm Discard Yes)")
        self.state = GameState.CONFIRM_DISCARD

    # --------------------------------------------------------------
    # State 16: Confirm Discard (Yes)
    # --------------------------------------------------------------
    def _state_confirm_discard(self) -> None:
        """
        Confirm discard dialog - no wait (human_delay from State 15 is enough)
        Sequence: D-pad Left x1 -> A
        Reference: confirm_discard_button_text.png / confirm_discard_button(entire-screen).jpg
        """
        logger.info("Entering State 16: Confirm Discard (Yes)")

        # D-pad Left x1 0 highlight Yes
        logger.info("Step 1: Move Left x1 (select Yes)")
        self.inputs.press_button("Move Left")
        human_delay()

        # A button - confirm Yes
        logger.info("Step 2: Continue/Confirm (A)")
        self.inputs.press_button("Continue/Confirm")
        human_delay()

        logger.info("Confirm discard complete.")
        logger.info("Transition: State 16 -> State 17 (wait for final cutscene)")
        self.state = GameState.SKIP_FINAL_CUTSCENE

    def _wait_for_final_cutscene_dialog(self) -> vision.Point | None:
        """Poll until final 'Y-Yes! I won!' dialog appears; log progress periodically."""
        template = config.TEMPLATE_SKIP_FINAL_CUTSCENE_TEXT
        timeout = config.FINAL_CUTSCENE_WAIT_TIMEOUT
        confidence = config.FINAL_CUTSCENE_CONFIDENCE
        poll_interval = config.FINAL_CUTSCENE_POLL_INTERVAL
        log_every = getattr(config, "FINAL_CUTSCENE_LOG_EVERY", 30.0)
        snapshot_every = getattr(config, "FINAL_CUTSCENE_SNAPSHOT_EVERY", 0.0)

        deadline = time.monotonic() + timeout
        next_log = time.monotonic() + log_every
        next_snapshot = (
            time.monotonic() + snapshot_every if snapshot_every > 0 else float("inf")
        )
        start = time.monotonic()

        while time.monotonic() < deadline:
            point = vision.find_on_screen(template, confidence=confidence)
            if point is not None:
                elapsed = time.monotonic() - start
                logger.info(
                    "Found %s at %s after %.1fs",
                    template,
                    point,
                    elapsed,
                )
                return point

            now = time.monotonic()

            if now >= next_log:
                elapsed = now - start
                logger.info(
                    "Still waiting for final cutscene... %.0fs / %.0fs",
                    elapsed,
                    timeout,
                )
                vision.log_best_match(template, confidence)
                next_log = now + log_every

            if now >= next_snapshot:
                vision.save_debug_screenshot(
                    f"state17_cutscene_wait_{int(elapsed)}.png"
                )
                next_snapshot = now + snapshot_every

            time.sleep(poll_interval)

        vision.log_best_match(template, confidence)
        return None

    # --------------------------------------------------------------
    # State 17: Skip Final Cutscene
    # --------------------------------------------------------------
    def _state_skip_final_cutscene(self) -> None:
        """
        Poll until final cutscene dialog appears, then skip with Start.
        Matcher: skip_final_cutscene_text.png ("Y-Yes! I won!")
        Action: Open Menu (Start button)
        """
        logger.info("Entering State 17: Skip Final Cutscene")
        logger.info(
            "Waiting for post-battle rewards/loads - polling for %s (timeout=%.0fs)",
            config.TEMPLATE_SKIP_FINAL_CUTSCENE_TEXT,
            config.FINAL_CUTSCENE_WAIT_TIMEOUT,
        )

        dialog = self._wait_for_final_cutscene_dialog()

        if dialog is None:
            logger.error(
                "Final cutscene dialog not detected within %.0fs. Check template: %s",
                config.FINAL_CUTSCENE_WAIT_TIMEOUT,
                config.TEMPLATE_SKIP_FINAL_CUTSCENE_TEXT,
            )
            vision.save_debug_screenshot("state17_cutscene_fail.png")
            logger.info(
                "Compare fail screenshot to reference: %s",
                config.TEMPLATE_SKIP_FINAL_CUTSCENE_FULL,
            )
            self.state = GameState.DONE
            return

        logger.info(
            "Final cutscene dialog found at %s - pressing Open Menu (Start)",
            dialog,
        )
        self.inputs.press_button("Open Menu")
        human_delay()
        human_delay()
        human_delay()
        human_delay()
        human_delay()
        human_delay()
        human_delay()
        human_delay()
        human_delay()
        human_delay()
        human_delay()
        human_delay()
        human_delay()
        human_delay()
        human_delay()
        human_delay()
        human_delay()
        human_delay()

        logger.info("Final cutscene skipped.")
        logger.info("Transition: State 17 -> State 18 (Claim Reward OK)")
        self.state = GameState.CLAIM_REWARD

    # --------------------------------------------------------------
    # State 18: Claim Reward (OK)
    # --------------------------------------------------------------
    def _state_claim_reward(self) -> None:
        """
        Reward screen after final cutscene - no wait (human_delay from State 17 is enough)
        Action: Continue/Confirm (A) on OK button
        Reference: claim_reward_text.png / claim_reward(entire-screen).jpg
        """
        logger.info("Entering State 18: Claim Reward (OK)")

        logger.info("Pressing Continue/Confirm (A)")
        self.inputs.press_button("Continue/Confirm")
        human_delay()

        logger.info("Claim reward complete. Full run finished.")
        self.state = GameState.DONE
