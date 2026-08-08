"""
ASTRAEA-IX — Resource Management Subsystem: Fuel Manager
Manages fuel budgets, usable propellant, safety reserve limits, and burn consumption efficiency.
"""

from typing import Dict, Any


class FuelManager:
    """
    Manages spacecraft fuel accounting and reserve boundaries.
    """

    def __init__(
        self,
        initial_fuel: float = 1000.0,
        reserve_fuel: float = 100.0,
    ) -> None:
        self.initial_fuel = float(initial_fuel)
        self.reserve_fuel = float(reserve_fuel)
        self.current_fuel = float(initial_fuel)

    def reset(self, initial_fuel: float = 1000.0) -> None:
        """Resets fuel state."""
        self.initial_fuel = float(initial_fuel)
        self.current_fuel = float(initial_fuel)

    def update_fuel(self, current_fuel: float) -> None:
        """Updates fuel level from physical state."""
        self.current_fuel = max(0.0, float(current_fuel))

    @property
    def spent_fuel(self) -> float:
        return max(0.0, self.initial_fuel - self.current_fuel)

    @property
    def usable_fuel(self) -> float:
        return max(0.0, self.current_fuel - self.reserve_fuel)

    @property
    def fuel_percentage(self) -> float:
        if self.initial_fuel <= 0.0:
            return 0.0
        return (self.current_fuel / self.initial_fuel) * 100.0

    def evaluate_burn_feasibility(self, required_fuel: float) -> bool:
        """Checks if a burn is feasible using usable fuel without breaching reserve."""
        return required_fuel <= self.usable_fuel

    def get_summary(self) -> Dict[str, float]:
        """Returns JSON-compatible fuel metrics."""
        return {
            "initial_fuel": self.initial_fuel,
            "current_fuel": self.current_fuel,
            "spent_fuel": self.spent_fuel,
            "usable_fuel": self.usable_fuel,
            "reserve_fuel": self.reserve_fuel,
            "fuel_percentage": self.fuel_percentage,
        }
