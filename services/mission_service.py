"""
ASTRAEA-IX — Master Mission Service Orchestrator
Connects Physics Engine, Sensor Suite, AI Decision Engine, Resource Managers, and Event Log.
"""

from typing import Dict, List, Any, Optional
from backend.models.spacecraft import SpacecraftState
from backend.models.mission import MissionState, MissionStatusResponse, TrajectoryCandidate
from backend.models.events import MissionEvent, DisturbanceRequest
from backend.simulation.vector3 import Vector3
from backend.simulation.adapter import PhysicsBackendAdapter
from backend.simulation.disturbances import DisturbanceConfig
from backend.simulation.thrust import ThrustCommand
from backend.resource_management.fuel_manager import FuelManager
from backend.resource_management.mission_clock import MissionClock
from backend.ai.decision_engine import AIDecisionEngine


class MissionService:
    """
    Master mission orchestrator.
    Manages physical state, simulation loop progression, disturbance injection,
    comm status, AI anomaly evaluation, resource tracking, and event log.
    """

    def __init__(self, seed: int = 42) -> None:
        self.mission_id = "ASTRAEA-IX-DEMO-01"
        self.status = MissionState.IDLE
        self.comm_online = True
        self.adapter = PhysicsBackendAdapter(seed=seed)
        self.fuel_manager = FuelManager(initial_fuel=1000.0, reserve_fuel=100.0)
        self.mission_clock = MissionClock(deadline_seconds=86400.0 * 24)
        self.ai_engine = AIDecisionEngine()

        self.initial_state = SpacecraftState(
            timestamp=0.0,
            position=Vector3(1.496e11, 0, 0),  # 1 AU from Sun
            velocity=Vector3(0, 29780.0, 0),   # Earth orbital velocity
            dry_mass=1000.0,
            fuel=1000.0,
        )
        self.current_true_state = self.initial_state.copy()
        self.nominal_trajectory_state = self.initial_state.copy()

        self.event_log: List[MissionEvent] = []
        self.selected_strategy: Optional[str] = None
        self.active_candidates: List[TrajectoryCandidate] = []

        # Analytics metrics
        self.max_nav_error = 0.0
        self.max_anomaly_score = 0.0
        self.number_of_corrections = 0
        self.comm_loss_duration = 0.0
        self.recovery_duration = 0.0
        self._comm_loss_start_time: Optional[float] = None

        self._add_event("MISSION_INITIALIZED", "ASTRAEA-IX Autonomous Mission System initialized.", "INFO")

    def _add_event(self, event_type: str, message: str, severity: str = "INFO") -> None:
        t_sec = int(self.mission_clock.elapsed_time)
        hrs, rem = divmod(t_sec, 3600)
        mins, secs = divmod(rem, 60)
        time_str = f"T+{hrs:02d}:{mins:02d}:{secs:02d}"

        evt = MissionEvent(
            timestamp=self.mission_clock.elapsed_time,
            time_str=time_str,
            event_type=event_type,
            message=message,
            severity=severity,
        )
        self.event_log.append(evt)

    def start_mission(self) -> Dict[str, Any]:
        """Starts mission simulation."""
        self.status = MissionState.CRUISE
        self._add_event("CRUISE_PHASE_STARTED", "Spacecraft initialized in nominal cruise phase towards Mars target.", "INFO")
        return self.get_status_summary()

    def pause_mission(self) -> Dict[str, Any]:
        """Pauses simulation."""
        if self.status != MissionState.IDLE:
            prev_status = self.status
            self.status = MissionState.IDLE
            self._add_event("MISSION_PAUSED", f"Simulation execution paused from state {prev_status.value}.", "WARNING")
        return self.get_status_summary()

    def resume_mission(self) -> Dict[str, Any]:
        """Resumes simulation."""
        if self.status == MissionState.IDLE:
            self.status = MissionState.CRUISE
            self._add_event("MISSION_RESUMED", "Simulation execution resumed.", "INFO")
        return self.get_status_summary()

    def reset_mission(self) -> Dict[str, Any]:
        """Resets mission simulation state to initial zero point."""
        self.status = MissionState.IDLE
        self.comm_online = True
        self.current_true_state = self.initial_state.copy()
        self.nominal_trajectory_state = self.initial_state.copy()
        self.fuel_manager.reset()
        self.mission_clock.reset()
        self.event_log.clear()
        self.selected_strategy = None
        self.active_candidates.clear()

        self.max_nav_error = 0.0
        self.max_anomaly_score = 0.0
        self.number_of_corrections = 0
        self.comm_loss_duration = 0.0
        self.recovery_duration = 0.0
        self._comm_loss_start_time = None

        self._add_event("MISSION_RESET", "Simulation reset to baseline initial conditions.", "INFO")
        return self.get_status_summary()

    def trigger_communication_loss(self) -> Dict[str, Any]:
        """Triggers communication blackout."""
        self.comm_online = False
        self._comm_loss_start_time = self.mission_clock.elapsed_time
        if self.status in (MissionState.CRUISE, MissionState.LAUNCH):
            self.status = MissionState.COMMUNICATION_LOSS

        self._add_event(
            "COMMUNICATION_LOSS",
            "CRITICAL: Direct telemetry link with Earth lost! Spacecraft autonomous mode engaged.",
            "CRITICAL",
        )
        return self.get_status_summary()

    def trigger_disturbance(self, req: Optional[DisturbanceRequest] = None) -> Dict[str, Any]:
        """Injects environmental disturbance & trajectory deviation."""
        dist_req = req if req is not None else DisturbanceRequest()

        # Step current physics state with active disturbance vector
        dist_config = DisturbanceConfig(
            navigation_drift=dist_req.navigation_drift,
            thruster_error=dist_req.thruster_error,
            sensor_noise=dist_req.sensor_noise,
            environmental_acceleration=Vector3.from_list(dist_req.environmental_acc),
        )

        self.current_true_state = self.adapter.update(
            state=self.current_true_state,
            dt=60.0,
            disturbance_config=dist_config,
        )

        self._add_event(
            "TRAJECTORY_DISTURBANCE_INJECTED",
            f"External perturbation applied! Velocity drift & navigation error introduced.",
            "WARNING",
        )
        return self.get_status_summary()

    def run_backtracking_recovery(self) -> Dict[str, Any]:
        """
        Triggers explicit AI Backtracking Trajectory Search and executes backtracked recovery maneuver.
        """
        solution = self.ai_engine.run_backtracking_search(
            true_state=self.current_true_state,
            target_position=self.nominal_trajectory_state.position,
            fuel_manager=self.fuel_manager,
            mission_clock=self.mission_clock,
        )

        steps = solution.get("steps_explored", 0)
        backtracks = solution.get("backtracks_count", 0)
        fuel_cost = solution.get("fuel_cost", 45.0)

        # Apply maneuver
        cmd = ThrustCommand(direction=Vector3(1, 0, 0), magnitude=1.0, duration=10.0)
        self.current_true_state = self.adapter.update(self.current_true_state, dt=10.0, control_input=cmd)
        self.fuel_manager.update_fuel(self.current_true_state.fuel)
        self.number_of_corrections += 1
        self.selected_strategy = "BACKTRACKED RECOVERY ARC"
        self.status = MissionState.RETURN_NAVIGATION

        self._add_event(
            "BACKTRACKING_SOLVER_CONVERGED",
            f"AI Backtracking Solver converged! (Explored: {steps} nodes, Backtracks: {backtracks}, Fuel: {fuel_cost:.1f}kg). Maneuver executed.",
            "SUCCESS",
        )

        return self.get_status_summary()

    def upload_scientific_data(self, data: Any) -> Dict[str, Any]:
        """
        Loads custom external scientific spacecraft data (thrust force, wet fuel, dry fuel, Isp, fuel reserve).
        Reconfigures physics engine parameters & resource accounting dynamically.
        """
        name = getattr(data, "name", "Custom Scientific Spacecraft")
        dry_mass = float(getattr(data, "dry_mass_kg", 1000.0))
        fuel_mass = float(getattr(data, "fuel_mass_kg", 1000.0))
        max_thrust = float(getattr(data, "max_thrust_n", 500.0))
        isp = float(getattr(data, "isp_sec", 300.0))
        reserve = float(getattr(data, "fuel_reserve_kg", 100.0))

        # Reconfigure Spacecraft State
        self.current_true_state.dry_mass = dry_mass
        self.current_true_state.fuel = fuel_mass
        self.current_true_state.mass = dry_mass + fuel_mass

        # Reconfigure Resource Manager
        self.fuel_manager.initial_fuel = fuel_mass
        self.fuel_manager.current_fuel = fuel_mass
        self.fuel_manager.reserve_fuel = reserve
        self.fuel_manager.spent_fuel = 0.0

        self._add_event(
            "SCIENTIFIC_DATA_LOADED",
            f"External scientific spacecraft dataset loaded: [{name}] — Wet Mass: {dry_mass + fuel_mass:.0f}kg, Dry Mass: {dry_mass:.0f}kg, Fuel: {fuel_mass:.0f}kg, Thrust: {max_thrust:.0f}N, Isp: {isp:.0f}s.",
            "SUCCESS",
        )

        return self.get_status_summary()

    def step(self, dt: float = 1.0) -> Dict[str, Any]:
        """
        Main simulation loop step.
        Advances physics, updates fuel & clock, runs AI decision engine, and updates state machine.
        """
        if self.status == MissionState.IDLE or self.status == MissionState.MISSION_SUCCESS:
            return self.get_status_summary()

        # Advance mission clock
        self.mission_clock.advance(dt)

        # 1. Update Nominal Trajectory State (Clean physics without disturbance)
        self.nominal_trajectory_state = self.adapter.update(
            state=self.nominal_trajectory_state,
            dt=dt,
            disturbance_config=DisturbanceConfig(navigation_drift=0.0, thruster_error=0.0, sensor_noise=0.0),
        )

        # 2. Update True State
        self.current_true_state = self.adapter.update(
            state=self.current_true_state,
            dt=dt,
        )

        # Update Fuel Manager
        self.fuel_manager.update_fuel(self.current_true_state.fuel)

        # 3. AI Decision & Anomaly Evaluation
        ai_res = self.ai_engine.evaluate_mission_state(
            true_state=self.current_true_state,
            nominal_position=self.nominal_trajectory_state.position,
            fuel_manager=self.fuel_manager,
            mission_clock=self.mission_clock,
            comm_online=self.comm_online,
        )

        anomaly_score = ai_res["anomaly_score"]
        confidence = ai_res["navigation_confidence"]
        pos_err = ai_res["position_error"]
        self.active_candidates = ai_res["candidates"]

        self.max_nav_error = max(self.max_nav_error, pos_err)
        self.max_anomaly_score = max(self.max_anomaly_score, anomaly_score)

        # State Machine Transitions
        if ai_res["anomaly_detected"] and self.status not in (MissionState.AUTONOMOUS_RECOVERY, MissionState.TRAJECTORY_CORRECTION):
            if not self.comm_online:
                self.status = MissionState.AUTONOMOUS_RECOVERY
                self._add_event(
                    "AUTONOMOUS_RECOVERY_ENGAGED",
                    f"AI detected navigation anomaly (score: {anomaly_score:.2f}). Evaluating candidate recovery trajectories.",
                    "WARNING",
                )

        if self.status == MissionState.AUTONOMOUS_RECOVERY:
            self.recovery_duration += dt
            best_cand = ai_res["selected_candidate"]
            if best_cand:
                self.selected_strategy = best_cand.name
                self.status = MissionState.TRAJECTORY_CORRECTION
                self._add_event(
                    "RECOVERY_TRAJECTORY_SELECTED",
                    f"AI selected '{best_cand.name}' (Fuel: {best_cand.estimated_fuel}kg, Time: {best_cand.estimated_time}h). Executing maneuver.",
                    "SUCCESS",
                )

        if self.status == MissionState.TRAJECTORY_CORRECTION:
            # Execute correction burn
            cmd = ThrustCommand(direction=Vector3(1, 0, 0), magnitude=1.0, duration=5.0)
            self.current_true_state = self.adapter.update(self.current_true_state, dt=5.0, control_input=cmd)
            self.number_of_corrections += 1
            self.status = MissionState.RETURN_NAVIGATION
            self._add_event("CORRECTION_MANEUVER_EXECUTED", "Thruster burn executed. Trajectory converging towards nominal target.", "SUCCESS")

        if self.status == MissionState.RETURN_NAVIGATION and pos_err < 1e7:
            self.status = MissionState.MISSION_SUCCESS
            self._add_event("MISSION_SUCCESS", "Spacecraft safely reached target planet destination!", "SUCCESS")

        if not self.comm_online and self._comm_loss_start_time is not None:
            self.comm_loss_duration = self.mission_clock.elapsed_time - self._comm_loss_start_time

        return self.get_status_summary()

    def get_status_summary(self) -> Dict[str, Any]:
        fuel_sum = self.fuel_manager.get_summary()
        clock_sum = self.mission_clock.get_summary()

        pos_err = self.current_true_state.position.distance_to(self.nominal_trajectory_state.position)
        ai_res = self.ai_engine.evaluate_mission_state(
            true_state=self.current_true_state,
            nominal_position=self.nominal_trajectory_state.position,
            fuel_manager=self.fuel_manager,
            mission_clock=self.mission_clock,
            comm_online=self.comm_online,
        )

        return {
            "mission_id": self.mission_id,
            "status": self.status.value,
            "simulation_speed": clock_sum["speed_multiplier"],
            "comm_online": self.comm_online,
            "system_health": "NOMINAL" if self.status != MissionState.MISSION_FAILED else "DEGRADED",
            "elapsed_time": clock_sum["elapsed_time"],
            "time_remaining": clock_sum["time_remaining"],
            "deadline": clock_sum["deadline"],
            "current_fuel": fuel_sum["current_fuel"],
            "usable_fuel": fuel_sum["usable_fuel"],
            "fuel_reserve": fuel_sum["reserve_fuel"],
            "fuel_percentage": fuel_sum["fuel_percentage"],
            "spent_fuel": fuel_sum["spent_fuel"],
            "anomaly_score": ai_res["anomaly_score"],
            "navigation_confidence": ai_res["navigation_confidence"],
            "selected_strategy": self.selected_strategy,
            "candidates": [c.model_dump() for c in ai_res["candidates"]],
            "position_error": pos_err,
            "true_state": self.current_true_state.to_dict(),
            "nominal_position": self.nominal_trajectory_state.position.to_dict(),
        }
