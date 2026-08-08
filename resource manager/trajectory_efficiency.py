"""
ASTRAEA-IX
Trajectory Efficiency Manager.

Compares planned mission resources against actual
mission resource usage.

Tracks:
    - Planned time
    - Actual time
    - Planned fuel
    - Actual fuel
    - Time efficiency
    - Fuel efficiency
    - Overall trajectory efficiency
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TrajectoryPlan:
    """Pre-measured trajectory resource requirements."""

    planned_distance: float
    planned_time: float
    planned_fuel: float


@dataclass
class TrajectoryUsage:
    """Actual trajectory resource consumption."""

    actual_distance: float = 0.0
    actual_time: float = 0.0
    actual_fuel: float = 0.0


@dataclass
class EfficiencyReport:
    """Calculated trajectory efficiency."""

    time_efficiency: float
    fuel_efficiency: float
    distance_efficiency: float
    overall_efficiency: float


class TrajectoryEfficiency:
    """
    Tracks planned versus actual trajectory performance.

    Example:

        Planned fuel = 1000
        Actual fuel = 850

        Fuel efficiency = 85%

    The same principle is applied to time and distance.
    """

    def __init__(
        self,
        plan: TrajectoryPlan,
    ) -> None:

        if plan.planned_distance < 0:
            raise ValueError(
                "Planned distance cannot be negative."
            )

        if plan.planned_time <= 0:
            raise ValueError(
                "Planned time must be greater than zero."
            )

        if plan.planned_fuel < 0:
            raise ValueError(
                "Planned fuel cannot be negative."
            )

        self.plan = plan

        self.usage = TrajectoryUsage()

    # ========================================================
    # UPDATE ACTUAL USAGE
    # ========================================================

    def update(
        self,
        *,
        actual_distance: float | None = None,
        actual_time: float | None = None,
        actual_fuel: float | None = None,
    ) -> TrajectoryUsage:
        """
        Update actual trajectory usage.

        Only supplied values are changed.
        """

        if actual_distance is not None:
            if actual_distance < 0:
                raise ValueError(
                    "Actual distance cannot be negative."
                )

            self.usage.actual_distance = (
                float(actual_distance)
            )

        if actual_time is not None:
            if actual_time < 0:
                raise ValueError(
                    "Actual time cannot be negative."
                )

            self.usage.actual_time = (
                float(actual_time)
            )

        if actual_fuel is not None:
            if actual_fuel < 0:
                raise ValueError(
                    "Actual fuel cannot be negative."
                )

            self.usage.actual_fuel = (
                float(actual_fuel)
            )

        return self.usage

    # ========================================================
    # INCREMENT USAGE
    # ========================================================

    def add_usage(
        self,
        *,
        distance: float = 0.0,
        time_seconds: float = 0.0,
        fuel: float = 0.0,
    ) -> TrajectoryUsage:
        """Increment actual trajectory usage."""

        if distance < 0:
            raise ValueError(
                "Distance increment cannot be negative."
            )

        if time_seconds < 0:
            raise ValueError(
                "Time increment cannot be negative."
            )

        if fuel < 0:
            raise ValueError(
                "Fuel increment cannot be negative."
            )

        self.usage.actual_distance += (
            float(distance)
        )

        self.usage.actual_time += (
            float(time_seconds)
        )

        self.usage.actual_fuel += (
            float(fuel)
        )

        return self.usage

    # ========================================================
    # EFFICIENCY
    # ========================================================

    def calculate(
        self,
    ) -> EfficiencyReport:
        """
        Calculate trajectory efficiency.

        Efficiency is based on:

            planned / actual

        for resources where lower actual usage is better.

        The result is capped at 100% for reporting.
        """

        time_efficiency = self._resource_efficiency(
            planned=self.plan.planned_time,
            actual=self.usage.actual_time,
        )

        fuel_efficiency = self._resource_efficiency(
            planned=self.plan.planned_fuel,
            actual=self.usage.actual_fuel,
        )

        distance_efficiency = self._resource_efficiency(
            planned=self.plan.planned_distance,
            actual=self.usage.actual_distance,
        )

        values = [
            time_efficiency,
            fuel_efficiency,
            distance_efficiency,
        ]

        overall_efficiency = (
            sum(values) / len(values)
        )

        return EfficiencyReport(
            time_efficiency=time_efficiency,
            fuel_efficiency=fuel_efficiency,
            distance_efficiency=distance_efficiency,
            overall_efficiency=overall_efficiency,
        )

    # ========================================================
    # INDIVIDUAL METRICS
    # ========================================================

    def fuel_efficiency(self) -> float:
        """Return fuel efficiency percentage."""

        return self.calculate().fuel_efficiency

    def time_efficiency(self) -> float:
        """Return time efficiency percentage."""

        return self.calculate().time_efficiency

    def distance_efficiency(self) -> float:
        """Return distance efficiency percentage."""

        return self.calculate().distance_efficiency

    def overall_efficiency(self) -> float:
        """Return overall efficiency percentage."""

        return self.calculate().overall_efficiency

    # ========================================================
    # SAVINGS
    # ========================================================

    def fuel_saved(self) -> float:
        """
        Return fuel saved compared with planned usage.

        Positive = saved fuel.
        Negative = fuel exceeded plan.
        """

        return (
            self.plan.planned_fuel
            - self.usage.actual_fuel
        )

    def time_saved(self) -> float:
        """
        Return time saved compared with planned time.

        Positive = faster than planned.
        Negative = slower than planned.
        """

        return (
            self.plan.planned_time
            - self.usage.actual_time
        )

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> dict:
        """Return telemetry/API-friendly representation."""

        report = self.calculate()

        return {
            "planned": {
                "distance": self.plan.planned_distance,
                "time": self.plan.planned_time,
                "fuel": self.plan.planned_fuel,
            },

            "actual": {
                "distance": self.usage.actual_distance,
                "time": self.usage.actual_time,
                "fuel": self.usage.actual_fuel,
            },

            "efficiency": {
                "distance": report.distance_efficiency,
                "time": report.time_efficiency,
                "fuel": report.fuel_efficiency,
                "overall": report.overall_efficiency,
            },

            "savings": {
                "fuel": self.fuel_saved(),
                "time": self.time_saved(),
            },
        }

    # ========================================================
    # RESET
    # ========================================================

    def reset(self) -> None:
        """Reset actual trajectory usage."""

        self.usage = TrajectoryUsage()

    # ========================================================
    # INTERNAL
    # ========================================================

    @staticmethod
    def _resource_efficiency(
        planned: float,
        actual: float,
    ) -> float:
        """
        Calculate resource efficiency.

        For zero planned values:
            - zero actual -> 100%
            - non-zero actual -> 0%
        """

        if planned == 0:
            return 100.0 if actual == 0 else 0.0

        efficiency = (
            planned / actual
        ) * 100.0 if actual > 0 else 100.0

        return max(
            0.0,
            min(
                efficiency,
                100.0,
            ),
        )