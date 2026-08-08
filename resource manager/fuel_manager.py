"""
ASTRAEA-IX
Fuel Management Service.

Tracks spacecraft fuel consumption, remaining fuel,
fuel efficiency, and fuel expenditure.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class FuelState:
    """Current fuel state of a spacecraft."""

    initial_fuel: float
    remaining_fuel: float
    consumed_fuel: float = 0.0

    @property
    def percentage_remaining(self) -> float:
        """Return remaining fuel as a percentage."""

        if self.initial_fuel <= 0:
            return 0.0

        return (
            self.remaining_fuel
            / self.initial_fuel
        ) * 100.0

    @property
    def percentage_consumed(self) -> float:
        """Return consumed fuel as a percentage."""

        if self.initial_fuel <= 0:
            return 0.0

        return (
            self.consumed_fuel
            / self.initial_fuel
        ) * 100.0


class FuelManager:
    """
    Manages spacecraft fuel resources.

    Responsibilities:
        - Register spacecraft fuel
        - Consume fuel
        - Track remaining fuel
        - Track total consumption
        - Report fuel percentage
        - Prevent negative fuel
    """

    def __init__(self) -> None:
        self._fuel: Dict[str, FuelState] = {}

    # ========================================================
    # REGISTRATION
    # ========================================================

    def register_spacecraft(
        self,
        spacecraft_id: str,
        initial_fuel: float,
    ) -> FuelState:
        """
        Register or reset spacecraft fuel.

        Args:
            spacecraft_id:
                Unique spacecraft identifier.

            initial_fuel:
                Initial fuel quantity.

        Returns:
            FuelState
        """

        if initial_fuel < 0:
            raise ValueError(
                "Initial fuel cannot be negative."
            )

        state = FuelState(
            initial_fuel=float(initial_fuel),
            remaining_fuel=float(initial_fuel),
            consumed_fuel=0.0,
        )

        self._fuel[spacecraft_id] = state

        return state

    # ========================================================
    # CONSUMPTION
    # ========================================================

    def consume(
        self,
        spacecraft_id: str,
        amount: float,
    ) -> FuelState:
        """
        Consume spacecraft fuel.

        Fuel cannot become negative.

        Args:
            spacecraft_id:
                Spacecraft identifier.

            amount:
                Fuel amount to consume.

        Returns:
            Updated FuelState.
        """

        if amount < 0:
            raise ValueError(
                "Fuel consumption cannot be negative."
            )

        state = self._get_state(
            spacecraft_id
        )

        actual_consumption = min(
            float(amount),
            state.remaining_fuel,
        )

        state.remaining_fuel -= (
            actual_consumption
        )

        state.consumed_fuel += (
            actual_consumption
        )

        return state

    # ========================================================
    # REFUEL
    # ========================================================

    def add_fuel(
        self,
        spacecraft_id: str,
        amount: float,
    ) -> FuelState:
        """
        Add fuel to the spacecraft.

        This is primarily useful for simulation
        reset/refueling scenarios.
        """

        if amount < 0:
            raise ValueError(
                "Fuel addition cannot be negative."
            )

        state = self._get_state(
            spacecraft_id
        )

        state.remaining_fuel += float(amount)

        return state

    # ========================================================
    # QUERIES
    # ========================================================

    def get_state(
        self,
        spacecraft_id: str,
    ) -> FuelState:
        """Return current fuel state."""

        return self._get_state(
            spacecraft_id
        )

    def get_remaining(
        self,
        spacecraft_id: str,
    ) -> float:
        """Return remaining fuel quantity."""

        return self._get_state(
            spacecraft_id
        ).remaining_fuel

    def get_percentage(
        self,
        spacecraft_id: str,
    ) -> float:
        """Return remaining fuel percentage."""

        return self._get_state(
            spacecraft_id
        ).percentage_remaining

    def get_consumed(
        self,
        spacecraft_id: str,
    ) -> float:
        """Return total consumed fuel."""

        return self._get_state(
            spacecraft_id
        ).consumed_fuel

    # ========================================================
    # STATUS
    # ========================================================

    def is_depleted(
        self,
        spacecraft_id: str,
    ) -> bool:
        """Return True if fuel has reached zero."""

        return (
            self._get_state(
                spacecraft_id
            ).remaining_fuel
            <= 0.0
        )

    def is_low(
        self,
        spacecraft_id: str,
        threshold: float = 20.0,
    ) -> bool:
        """
        Determine whether fuel is below a
        specified percentage.
        """

        return (
            self.get_percentage(
                spacecraft_id
            )
            <= threshold
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
        spacecraft_id: str,
    ) -> FuelState:
        """Reset fuel to the initial amount."""

        state = self._get_state(
            spacecraft_id
        )

        state.remaining_fuel = (
            state.initial_fuel
        )

        state.consumed_fuel = 0.0

        return state

    # ========================================================
    # INTERNAL
    # ========================================================

    def _get_state(
        self,
        spacecraft_id: str,
    ) -> FuelState:
        if spacecraft_id not in self._fuel:
            raise KeyError(
                f"Spacecraft '{spacecraft_id}' "
                "has not been registered."
            )

        return self._fuel[spacecraft_id]