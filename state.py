"""Game flow state machine."""

from __future__ import annotations

import logging
from enum import Enum, auto

import config
import vision
from input_handler import InputHandler, human_delay

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
        human_delay()

        logger.info("Battle setup complete.")
        logger.info("Transition: State 13 -> State 14 (Aim for Enemy)")
        self.state = GameState.DONE

    def _detect_target_lock_state(self) -> str:
        """
        Returns 'locked' or 'not_locked', or 'unknown'.
        Compares match scores for both target templates.
        """
        lock_conf = config.STATE14_TARGET_LOCK_IN_CONFIDENCE
        not_lock_conf = config.STATE14_TARGET_NOT_LOCK_IN_CONFIDENCE

        lock_result = vision.find_on_screen_with_score(
            config.TEMPLATE_TARGET_LOCK_IN, confidence=0.0
        )
        not_lock_result = vision.find_on_screen_with_score(
            config.TEMPLATE_TARGET_NOT_LOCK_IN, confidence=0.0
        )

        lock_score = lock_result[2] if lock_result else 0.0
        not_lock_score = not_lock_result[2] if not_lock_result else 0.0

        logger.info(
            "Target lock scores - locked: %.3f, not_locked: %.3f",
            lock_score,
            not_lock_score,
        )

        if lock_score >= lock_conf and lock_score >= not_lock_score:
            return "locked"
        if not_lock_score >= not_lock_conf:
            return "not_locked"
        return "unknown"

    # --------------------------------------------------------------
    # State 14: Aim for Enemy
    # --------------------------------------------------------------
    def _state_aim_for_enemy(self) -> None:
        """
        Wait for aim mode, then handle target lock state.
        Detect aim mode: aim_for_enemy_text.png
        Locked:     target_lock_in.png     -> A press
        Not locked: target_not_lock_in.png -> D-pad Left x2 -> A press
        """
        logger.info("Entering State 14: Aim for Enemy")

        # --- Phase 1: wait for aim mode (fixed wait and/or template) ---
        if config.AIM_PHASE_USE_FIXED_WAIT:
            wait_s = timing.get_aim_phase_fixed_wait_seconds()
            logger.info("Aim phase: fixed blind wait %.0fs", wait_s)

            elapsed = 0.0
            while elapsed < wait_s:
                chunk = min(config.AIM_PHASE_LOG_EVERY, wait_s - elapsed)
                time.sleep(chunk)
                elapsed += chunk
                if elapsed < wait_s:
                    logger.info(
                        "Still waiting for aim mode... %.0fs / %.0fs", elapsed, wait_s
                    )
        else:
            logger.info(
                "Aim phase: waiting for %s (timeout=%.0fs)",
                config.TEMPLATE_AIM_FOR_ENEMY_TEXT,
                config.AIM_PHASE_TIMEOUT,
            )
            aim_marker = vision.wait_for_element(
                config.TEMPLATE_AIM_FOR_ENEMY_TEXT,
                timeout=config.AIM_PHASE_TIMEOUT,
                confidence=config.STATE14_AIM_CONFIDENCE,
                poll_interval=config.AIM_PHASE_POLL_INTERVAL,
            )
            if aim_marker is None:
                timing.mark_aim_phase_end(found=False)
                logger.error("Aim for enemy mode not detected")
                vision.save_debug_screenshot("state14_aim_fail.png")
                self.state = GameState.DONE
                return

        # Verify aim mode text is on screen (even after fixed wait)
        aim_point = vision.find_on_screen(
            config.TEMPLATE_AIM_FOR_ENEMY_TEXT,
            confidence=config.STATE14_AIM_CONFIDENCE,
        )
        if aim_point is None:
            elapsed = timing.mark_aim_phase_end(found=False)
            logger.error(
                "aim_for_enemy_text not visible after wait (%.1fs). Check template: %s",
                elapsed or 0,
            )
            vision.save_debug_screenshot("state14_aim_fail.png")
            self.state = GameState.DONE
            return

        elapsed = timing.mark_aim_phase_end(found=True)
        logger.info("Aim mode detected at %s after %.2fs", aim_point, elapsed or 0)

        if config.AIM_PHASE_MEASURE_ONLY:
            logger.info(
                "AIM_PHASE_MEASURE_ONLY=True - stopping after aim mode detected"
            )
            self.state = GameState.DONE
            return

        # --- Phase 2: locked vs not locked ---
        lock_state = self._detect_target_lock_state()

        if lock_state == "locked":
            logger.info("Target already locked in - pressing A")
            self.inputs.press_button("Continue/Confirm")
            human_delay()

        elif lock_state == "not_locked":
            logger.info(
                "Target not locked - pressing D-pad Left x%d then A",
                config.AIM_TARGET_NOT_LOCKED_LEFT_COUNT,
            ),
            self._press_repeated("Move Left", config.AIM_TARGET_NOT_LOCKED_LEFT_COUNT)
            self.inputs.press_button("Continue/Confirm")
            human_delay()

        else:
            logger.error("Could not determine target lock state")
            vision.save_debug_screenshot("state14_lock_fail.png")
            logger.info(
                "Compare to %s / %s",
                config.TEMPLATE_AIM_FOR_ENEMY_LOCK_IN_FULL,
                config.TEMPLATE_AIM_FOR_ENEMY_NOT_LOCK_IN_FULL,
            )
            self.state = GameState.DONE
            return

        logger.info("Aim for enemy complete. Stopping (next state TBD).")
        self.state = GameState.DONE
