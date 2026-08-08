"""
ASTRAEA-IX — AI Decision Engine & Recovery Maneuver Planner
Orchestrates anomaly evaluation, backtracking trajectory search, candidate trajectory generation,
fuel/time constraint checking, and recovery maneuver selection.
"""

from typing import Dict, List, Any, Optional, Tuple
from backend.models.mission import TrajectoryCandidate
from backend.models.spacecraft import SpacecraftState
from backend.simulation.vector3 import Vector3
from backend.ai.anomaly.detector import AnomalyDetector
from backend.ai.backtracking import BacktrackingTrajectorySolver
from backend.resource_management.fuel_manager import FuelManager
from backend.resource_management.mission_clock import MissionClock
from backend.resource_management.trajectory_efficiency import TrajectoryEfficiencyEvaluator


class AIDecisionEngine:
    """
    Autonomous decision-making engine for deep-space recovery operations using Backtracking Trajectory Search.
    """

    def __init__(self) -> None:
        self.anomaly_detector = AnomalyDetector()

    def run_backtracking_search(
        self,
        true_state: SpacecraftState,
        target_position: Vector3,
        fuel_manager: FuelManager,
        mission_clock: MissionClock,
    ) -> Dict[str, Any]:
        """
        Runs explicit Backtracking Trajectory Search algorithm to find the optimal backtracked recovery arc.
        """
        solver = BacktrackingTrajectorySolver(target_position=target_position)
        solution = solver.solve(
            current_state=true_state,
            usable_fuel=fuel_manager.usable_fuel,
            time_remaining_sec=mission_clock.time_remaining,
        )
        return solution

    def evaluate_mission_state(
        self,
        true_state: SpacecraftState,
        nominal_position: Vector3,
        fuel_manager: FuelManager,
        mission_clock: MissionClock,
        comm_online: bool = True,
    ) -> Dict[str, Any]:
        """
        Evaluates current mission state, detects anomalies, and generates candidate recovery options.
        """
        pos_error = true_state.position.distance_to(nominal_position)
        vel_error = true_state.velocity.norm() * 0.05

        anomaly_score, confidence, anomaly_detected = self.anomaly_detector.evaluate(
            position_error=pos_error,
            velocity_error=vel_error,
            comm_online=comm_online,
        )

        candidates = TrajectoryEfficiencyEvaluator.generate_candidates(
            deviation_distance=pos_error,
            fuel_manager=fuel_manager,
            mission_clock=mission_clock,
        )

        best_candidate, decision_reason = TrajectoryEfficiencyEvaluator.select_best_candidate(candidates)

        # Backtracking trajectory search metrics
        backtrack_res = self.run_backtracking_search(
            true_state=true_state,
            target_position=nominal_position,
            fuel_manager=fuel_manager,
            mission_clock=mission_clock,
        )

        decision_type = "NOMINAL_MONITORING"
        if anomaly_detected:
            if not comm_online:
                decision_type = "AUTONOMOUS_BACKTRACKING_RECOVERY"
            else:
                decision_type = "GROUND_ASSISTED_CORRECTION"

        return {
            "anomaly_score": anomaly_score,
            "navigation_confidence": confidence,
            "anomaly_detected": anomaly_detected,
            "position_error": pos_error,
            "decision_type": decision_type,
            "candidates": candidates,
            "selected_candidate": best_candidate,
            "decision_reason": decision_reason,
            "backtracking_solution": backtrack_res,
        }
