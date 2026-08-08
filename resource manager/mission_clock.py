"""
ASTRAEA-IX
Mission Clock.

Tracks mission elapsed time, remaining time,
mission duration, and mission progress.
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class MissionTimeState:
    """Current mission timing state."""

    mission_duration: float
    elapsed_time: float = 0.0
    running: bool = False

    @property
    def remaining_time(self) -> float:
        """Return remaining mission time."""

        return max(
            self.mission_duration
            - self.elapsed_time,
            0.0,
        )

    @property
    def progress_percentage(self) -> float:
        """Return mission progress percentage."""

        if self.mission_duration <= 0:
            return 100.0

        return min(
            (
                self.elapsed_time
                / self.mission_duration
            ) * 100.0,
            100.0,
        )

    @property
    def completed(self) -> bool:
        """Return True when mission time is exhausted."""

        return (
            self.elapsed_time
            >= self.mission_duration
        )


class MissionClock:
    """
    Mission time management.

    Supports:
        - Start
        - Pause
        - Resume
        - Stop
        - Reset
        - Elapsed time
        - Remaining time
        - Mission progress
    """

    def __init__(
        self,
        mission_duration: float,
    ) -> None:

        if mission_duration <= 0:
            raise ValueError(
                "Mission duration must be greater than zero."
            )

        self._state = MissionTimeState(
            mission_duration=float(
                mission_duration
            )
        )

        self._last_update: float | None = None

    # ========================================================
    # CONTROL
    # ========================================================

    def start(self) -> None:
        """Start the mission clock."""

        self._state.running = True

        self._last_update = time.monotonic()

    def pause(self) -> None:
        """Pause the mission clock."""

        self.update()

        self._state.running = False

        self._last_update = None

    def resume(self) -> None:
        """Resume the mission clock."""

        if self._state.completed:
            return

        self._state.running = True

        self._last_update = time.monotonic()

    def stop(self) -> None:
        """Stop the mission clock."""

        self.update()

        self._state.running = False

        self._last_update = None

    def reset(self) -> None:
        """Reset mission time."""

        self._state.elapsed_time = 0.0

        self._state.running = False

        self._last_update = None

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self) -> MissionTimeState:
        """
        Update elapsed mission time.

        Returns:
            Current MissionTimeState.
        """

        if not self._state.running:
            return self._state

        now = time.monotonic()

        if self._last_update is None:
            self._last_update = now
            return self._state

        delta = now - self._last_update

        self._last_update = now

        self._state.elapsed_time += delta

        if (
            self._state.elapsed_time
            >= self._state.mission_duration
        ):
            self._state.elapsed_time = (
                self._state.mission_duration
            )

            self._state.running = False

            self._last_update = None

        return self._state

    # ========================================================
    # SIMULATION UPDATE
    # ========================================================

    def advance(
        self,
        delta_seconds: float,
    ) -> MissionTimeState:
        """
        Advance mission time manually.

        Useful for deterministic simulation.

        Args:
            delta_seconds:
                Simulation time increment.
        """

        if delta_seconds < 0:
            raise ValueError(
                "Delta time cannot be negative."
            )

        if not self._state.running:
            return self._state

        self._state.elapsed_time += (
            float(delta_seconds)
        )

        if (
            self._state.elapsed_time
            >= self._state.mission_duration
        ):
            self._state.elapsed_time = (
                self._state.mission_duration
            )

            self._state.running = False

            self._last_update = None

        return self._state

    # ========================================================
    # QUERIES
    # ========================================================

    def get_state(self) -> MissionTimeState:
        """Return current timing state."""

        self.update()

        return self._state

    def get_elapsed_time(self) -> float:
        """Return elapsed mission time."""

        return self.get_state().elapsed_time

    def get_remaining_time(self) -> float:
        """Return remaining mission time."""

        return self.get_state().remaining_time

    def get_progress(self) -> float:
        """Return mission progress percentage."""

        return self.get_state().progress_percentage

    def is_running(self) -> bool:
        """Return whether the clock is running."""

        return self._state.running

    def is_complete(self) -> bool:
        """Return whether mission duration is complete."""

        return self.get_state().completed

    # ========================================================
    # CONFIGURATION
    # ========================================================

    def set_duration(
        self,
        mission_duration: float,
    ) -> None:
        """
        Change mission duration.

        Primarily intended for simulation setup.
        """

        if mission_duration <= 0:
            raise ValueError(
                "Mission duration must be greater than zero."
            )

        self._state.mission_duration = float(
            mission_duration
        )

        if (
            self._state.elapsed_time
            > self._state.mission_duration
        ):
            self._state.elapsed_time = (
                self._state.mission_duration
            )