"""Measure and persist State 12 -> State 13 battle load duration."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger(__name__)

_battle_load_start: Optional[float] = None


def mark_battle_load_start() -> None:
    """Call right after State 12 presses A (starts battle load timer)."""
    global _battle_load_start
    _battle_load_start = time.monotonic()
    logger.info("Battle load timer started (State 12 A pressed)")


def mark_battle_load_end(found: bool) -> Optional[float]:
    """
    Call when State 13 finds (or fails to find) the Select All button.
    Returns elapsed seconds, or None if start was never marked.
    """
    global _battle_load_start
    if _battle_load_start is None:
        logger.warning("Battle load timer was never started")
        return None

    elapsed = time.monotonic() - _battle_load_start
    _battle_load_start = None

    status = "found" if found else "timeout"
    logger.info("Battle load timer ended (%s): %.2f seconds", status, elapsed)

    _append_measurement(elapsed, found)
    return elapsed


def _append_measurement(elapsed: float, found: bool) -> None:
    path = config.BATTLE_LOAD_TIMES_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    history: list = []
    if path.exists():
        try:
            history = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            logger.exception("Could not read %s - starting fresh", path)

    history.append(
        {
            "elapsed_s": round(elapsed, 2),
            "found": found,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    )

    # Keep last 20 runs
    history = history[-20:]
    path.write_text(json.dumps(history, indent=2), encoding="utf-8")
    logger.info("Saved battle load measurement to %s", path)


def get_battle_load_timeout() -> float:
    """
    Use max successful measured time + buffer.
    Falls back to BATTLE_LOAD_TIMEOUT if no history yet.
    """
    path = config.BATTLE_LOAD_TIMES_FILE
    if not path.exists():
        logger.info(
            "No battle load history - using fallback timeout %.0fs",
            config.BATTLE_LOAD_TIMEOUT,
        )
        return config.BATTLE_LOAD_TIMEOUT

    try:
        history = json.loads(path.read_text(encoding="utf-8"))
        successful = [r["elapsed_s"] for r in history if r.get("found")]
        if not successful:
            logger.info(
                "No successful battle load measurements - using fallback timeout %.0fs",
                config.BATTLE_LOAD_TIMEOUT,
            )
            return config.BATTLE_LOAD_TIMEOUT

        max_measured = max(successful)
        timeout = max(
            config.BATTLE_LOAD_MIN_TIMEOUT,
            max_measured + config.BATTLE_LOAD_TIMEOUT_BUFFER,
        )
        logger.info(
            "Adaptive battle load timeout: %.0fs "
            "(max measured %.1fs + %.0fs buffer)",
            timeout,
            max_measured,
            config.BATTLE_LOAD_TIMEOUT_BUFFER,
        )
        return timeout
    except Exception:
        logger.exception("Failed to read battle load history")
        return config.BATTLE_LOAD_TIMEOUT


def print_battle_load_stats() -> None:
    """Print summary from saved measurements."""
    path = config.BATTLE_LOAD_TIMES_FILE
    if not path.exists():
        print("No measurements yet. Run main.py through State 12 -> 13 once.")
        return

    history = json.loads(path.read_text(encoding="utf-8"))
    successful = [r["elapsed_s"] for r in history if r.get("found")]
    failed = [r["elapsed_s"] for r in history if not r.get("found")]

    print(f"=== Battle load stats ({len(history)} runs) ===")
    if successful:
        print(f"  Successful: {len(successful)}")
        print(f"  Min:    {min(successful):.1f}s")
        print(f"  Max:    {max(successful):.1f}s")
        print(f"  Avg:    {sum(successful)/len(successful):.1f}s")
        print(
            f"  Recommended timeout: {max(successful) + config.BATTLE_LOAD_TIMEOUT_BUFFER:.0f}s"
        )
    if failed:
        print(f"  Timeouts: {len(failed)}")
    print(f"  Full log: {path}")


_aim_phase_start: Optional[float] = None


def mark_aim_phase_start() -> None:
    """Call right after State 13 final A press."""
    global _aim_phase_start
    _aim_phase_start = time.monotonic()
    logger.info("Aim phase timer started (State 13 A pressed)")


def mark_aim_phase_end(found: bool) -> Optional[float]:
    """Call when State 14 detects aim mode (or times out)."""
    global _aim_phase_start
    if _aim_phase_start is None:
        logger.warning("Aim phase timer was never started")
        return None

    elapsed = time.monotonic() - _aim_phase_start
    _aim_phase_start = None

    status = "found" if found else "timeout"
    logger.info("Aim phase timer ended (%s): %.2f seconds", status, elapsed)

    _append_measurement(elapsed, found)
    return elapsed


def _append_measurement(elapsed: float, found: bool) -> None:
    path = config.AIM_PHASE_TIMES_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    history: list = []
    if path.exists():
        try:
            history = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            logger.exception("Could not read %s - starting fresh", path)

    history.append(
        {
            "elapsed_s": round(elapsed, 2),
            "found": found,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    history = history[-20:]
    path.write_text(json.dumps(history, indent=2), encoding="utf-8")
    logger.info("Saved aim phase measurement to %s", path)


def get_aim_phase_fixed_wait_seconds() -> float:
    """Adaptive fixed wait from successful measurements."""
    path = config.AIM_PHASE_TIMES_FILE
    if not path.exists():
        return config.AIM_PHASE_FIXED_WAIT_SECONDS

    try:
        history = json.loads(path.read_text(encoding="utf-8"))
        successful = [r["elapsed_s"] for r in history if r.get("found")]
        if not successful:
            return config.AIM_PHASE_FIXED_WAIT_SECONDS

        return max(
            config.AIM_PHASE_MIN_TIMEOUT,
            max(successful) + config.AIM_PHASE_TIMEOUT_BUFFER,
        )
    except Exception:
        logger.exception("Failed to read aim phase history")
        return config.AIM_PHASE_FIXED_WAIT_SECONDS


def print_aim_phase_stats() -> None:
    path = config.AIM_PHASE_TIMES_FILE
    if not path.exists():
        print("No aim phase measurements yet.")
        return

    history = json.loads(path.read_text(encoding="utf-8"))
    successful = [r["elapsed_s"] for r in history if r.get("found")]

    print(f"=== Aim phase stats ({len(history)} runs) ===")
    if successful:
        print(
            f"  Min: {min(successful):.1f}s Max: {max(successful):.1f}s Avg: {sum(successful)/len(successful):.1f}s"
        )
        print(
            f"  Recommended fixed wait: {max(successful) + config.AIM_PHASE_TIMEOUT_BUFFER:.0f}s"
        )
    print(f"  Full log: {path}")
