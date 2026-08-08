"""
ASTRAEA-IX — Resource Management Subsystem: Trajectory Efficiency Evaluator
Evaluates candidate recovery trajectories against fuel and time constraints.
"""

from typing import List, Dict, Any, Tuple, Optional
from backend.models.mission import TrajectoryCandidate
from backend.resource_management.fuel_manager import FuelManager
from backend.resource_management.mission_clock import MissionClock


class TrajectoryEfficiencyEvaluator:
    """
    Resource-aware trajectory selection evaluator.
    Evaluates candidate maneuvers against usable fuel and mission deadlines.
    """

    @staticmethod
    def generate_candidates(
        deviation_distance: float,
        fuel_manager: FuelManager,
        mission_clock: MissionClock,
    ) -> List[TrajectoryCandidate]:
        """
        Generates and evaluates candidate recovery trajectories.
        """
        usable = fuel_manager.usable_fuel
        time_rem_hours = mission_clock.time_remaining / 3600.0

        # Base fuel/time scaling derived from deviation magnitude
        scale = max(1.0, deviation_distance / 1e8)

        # 1. Direct Correction
        direct_fuel = round(120.0 * scale, 1)
        direct_time = round(6.5 * scale, 1)
        direct_feasible = (direct_fuel <= usable) and (direct_time <= time_rem_hours)
        direct_reason = None
        if direct_fuel > usable:
            direct_reason = f"REJECTED — Exceeds usable fuel ({direct_fuel}kg > {usable:.1f}kg)"
        elif direct_time > time_rem_hours:
            direct_reason = f"REJECTED — Misses deadline ({direct_time}h > {time_rem_hours:.1f}h)"

        candidate_direct = TrajectoryCandidate(
            id="traj_direct",
            name="DIRECT CORRECTION",
            estimated_fuel=direct_fuel,
            estimated_time=direct_time,
            risk_score=0.15,
            feasible=direct_feasible,
            rejection_reason=direct_reason,
            delta_v=round(85.0 * scale, 1),
            burn_duration=12.0,
        )

        # 2. Low Energy Arc
        arc_fuel = round(45.0 * scale, 1)
        arc_time = round(14.0 * scale, 1)
        arc_feasible = (arc_fuel <= usable) and (arc_time <= time_rem_hours)
        arc_reason = None
        if arc_fuel > usable:
            arc_reason = f"REJECTED — Exceeds usable fuel ({arc_fuel}kg > {usable:.1f}kg)"
        elif arc_time > time_rem_hours:
            arc_reason = f"REJECTED — Misses deadline ({arc_time}h > {time_rem_hours:.1f}h)"

        candidate_arc = TrajectoryCandidate(
            id="traj_arc",
            name="LOW ENERGY ARC",
            estimated_fuel=arc_fuel,
            estimated_time=arc_time,
            risk_score=0.20,
            feasible=arc_feasible,
            rejection_reason=arc_reason,
            delta_v=round(35.0 * scale, 1),
            burn_duration=6.0,
        )

        # 3. Emergency Intercept
        intercept_fuel = round(210.0 * scale, 1)
        intercept_time = round(4.0 * scale, 1)
        intercept_feasible = (intercept_fuel <= usable) and (intercept_time <= time_rem_hours)
        intercept_reason = None
        if intercept_fuel > usable:
            intercept_reason = f"REJECTED — Exceeds usable fuel ({intercept_fuel}kg > {usable:.1f}kg)"
        elif intercept_time > time_rem_hours:
            intercept_reason = f"REJECTED — Misses deadline ({intercept_time}h > {time_rem_hours:.1f}h)"

        candidate_intercept = TrajectoryCandidate(
            id="traj_intercept",
            name="EMERGENCY INTERCEPT",
            estimated_fuel=intercept_fuel,
            estimated_time=intercept_time,
            risk_score=0.45,
            feasible=intercept_feasible,
            rejection_reason=intercept_reason,
            delta_v=round(150.0 * scale, 1),
            burn_duration=20.0,
        )

        return [candidate_direct, candidate_arc, candidate_intercept]

    @staticmethod
    def select_best_candidate(candidates: List[TrajectoryCandidate]) -> Tuple[Optional[TrajectoryCandidate], str]:
        """
        Selects optimal candidate from feasible options, prioritizing fuel preservation.
        """
        feasible_candidates = [c for c in candidates if c.feasible]
        if not feasible_candidates:
            return None, "NO_FEASIBLE_TRAJECTORY — Fuel/Time budget exhausted"

        # Sort by fuel consumption first, then risk score
        best = min(feasible_candidates, key=lambda c: (c.estimated_fuel, c.risk_score))
        reason = (
            f"Meets deadline ({best.estimated_time}h), preserves fuel ({best.estimated_fuel}kg burned), "
            f"risk score {best.risk_score:.2f}"
        )
        return best, reason
