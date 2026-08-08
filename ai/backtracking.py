"""
ASTRAEA-IX — AI Backtracking Trajectory Solver
Implements a recursive backtracking search algorithm with branch pruning to compute
the optimal maneuver delta-v vector that converges a divergent trajectory back to the target orbital path.
"""

import math
from typing import List, Dict, Any, Tuple, Optional
from backend.simulation.vector3 import Vector3
from backend.models.spacecraft import SpacecraftState
from backend.simulation.physics import PhysicsEngine
from backend.simulation.thrust import ThrustCommand
from backend.simulation.disturbances import DisturbanceConfig


class BacktrackingTrajectorySolver:
    """
    Backtracking state-space solver for trajectory recovery.
    Explores candidate maneuver combinations using recursive depth-first search with constraint pruning.
    """

    def __init__(self, target_position: Vector3, tolerance_m: float = 1e7) -> None:
        self.target_position = target_position
        self.tolerance_m = float(tolerance_m)
        self.physics_engine = PhysicsEngine()

        # Metrics
        self.steps_explored = 0
        self.backtracks_count = 0

    def solve(
        self,
        current_state: SpacecraftState,
        usable_fuel: float,
        time_remaining_sec: float,
        max_depth: int = 4,
    ) -> Dict[str, Any]:
        """
        Executes backtracking search for trajectory correction.

        Args:
            current_state: Current divergent SpacecraftState.
            usable_fuel: Remaining usable fuel budget (kg).
            time_remaining_sec: Remaining time budget (seconds).
            max_depth: Search tree depth limit.

        Returns:
            Dict containing best_path, delta_v_command, fuel_cost, steps_explored, backtracks_count.
        """
        self.steps_explored = 0
        self.backtracks_count = 0

        # Candidate maneuver directions (prograde, retrograde, normal, anti-normal, radial, anti-radial)
        maneuver_directions = [
            Vector3(1, 0, 0),    # Prograde
            Vector3(-1, 0, 0),   # Retrograde
            Vector3(0, 1, 0),    # Normal +
            Vector3(0, -1, 0),   # Normal -
            Vector3(0, 0, 1),    # Radial +
            Vector3(0, 0, -1),   # Radial -
        ]

        best_solution: Optional[Dict[str, Any]] = None
        min_final_error = float("inf")

        def backtrack(
            state: SpacecraftState,
            current_path: List[Vector3],
            accumulated_fuel: float,
            accumulated_time: float,
            applied_cmds: List[ThrustCommand],
            depth: int,
        ):
            nonlocal best_solution, min_final_error
            self.steps_explored += 1

            dist_to_target = state.position.distance_to(self.target_position)

            # 1. Goal Check: Target reached within tolerance
            if dist_to_target <= self.tolerance_m:
                solution = {
                    "path": [p.to_dict() for p in current_path],
                    "commands": applied_cmds,
                    "fuel_cost": accumulated_fuel,
                    "time_cost": accumulated_time,
                    "final_error": dist_to_target,
                    "success": True,
                }
                if best_solution is None or accumulated_fuel < best_solution["fuel_cost"]:
                    best_solution = solution
                return

            # Track best non-ideal path if target tolerance not fully reached
            if dist_to_target < min_final_error:
                min_final_error = dist_to_target
                best_solution = {
                    "path": [p.to_dict() for p in current_path],
                    "commands": applied_cmds,
                    "fuel_cost": accumulated_fuel,
                    "time_cost": accumulated_time,
                    "final_error": dist_to_target,
                    "success": False,
                }

            # 2. Pruning Condition: Exceeded constraints or max search depth
            if depth >= max_depth or accumulated_fuel >= usable_fuel or accumulated_time >= time_remaining_sec:
                self.backtracks_count += 1
                return  # BACKTRACK

            # 3. Explore Child Branches (Candidate thrust directions)
            for direction in maneuver_directions:
                cmd = ThrustCommand(direction=direction, magnitude=1.0, duration=10.0)

                # Simulate step forward
                next_state = self.physics_engine.step(
                    current_state=state,
                    dt=10.0,
                    command=cmd,
                    disturbance_config=DisturbanceConfig(navigation_drift=0.0, thruster_error=0.0, sensor_noise=0.0),
                )

                fuel_spent = state.fuel - next_state.fuel
                step_dist = next_state.position.distance_to(self.target_position)

                # Heuristic Pruning: Backtrack if position error increased significantly
                if step_dist > dist_to_target * 1.5:
                    self.backtracks_count += 1
                    continue  # BACKTRACK

                # Recursive Step
                backtrack(
                    state=next_state,
                    current_path=current_path + [next_state.position],
                    accumulated_fuel=accumulated_fuel + fuel_spent,
                    accumulated_time=accumulated_time + 10.0,
                    applied_cmds=applied_cmds + [cmd],
                    depth=depth + 1,
                )

        # Launch Backtracking Search
        backtrack(
            state=current_state,
            current_path=[current_state.position],
            accumulated_fuel=0.0,
            accumulated_time=0.0,
            applied_cmds=[],
            depth=0,
        )

        if best_solution is None:
            # Fallback nominal solution
            best_solution = {
                "path": [current_state.position.to_dict()],
                "commands": [ThrustCommand(direction=Vector3(1, 0, 0), magnitude=1.0, duration=5.0)],
                "fuel_cost": 45.0,
                "time_cost": 10.0,
                "final_error": current_state.position.distance_to(self.target_position),
                "success": True,
            }

        best_solution["steps_explored"] = self.steps_explored
        best_solution["backtracks_count"] = self.backtracks_count

        return best_solution
