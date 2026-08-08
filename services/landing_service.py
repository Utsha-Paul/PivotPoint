"""
ASTRAEA-IX — Planetary Landing Backend Service
Provides high-level descent simulation routines, landing safety evaluations,
descent telemetry packaging, and powered landing control dispatch.
"""

from typing import Dict, Any, Optional, Tuple
from backend.models.spacecraft import SpacecraftState
from backend.simulation.landing import LandingPhysics, LandingStatus
from backend.simulation.thrust import ThrustCommand
from backend.simulation.vector3 import Vector3


class LandingService:
    """
    Backend service orchestrating planetary powered descent and touchdown safety analysis.
    """

    def __init__(self, landing_physics: Optional[LandingPhysics] = None) -> None:
        self.landing_physics = landing_physics if landing_physics is not None else LandingPhysics()

    def step_landing_descent(
        self,
        current_state: SpacecraftState,
        dt: float = 1.0,
        thrust_command_dict: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Executes one step of powered descent physics propagation.

        Args:
            current_state: Spacecraft TRUE STATE.
            dt: Timestep duration in seconds.
            thrust_command_dict: Optional retrograde descent throttle command dict.

        Returns:
            Dictionary payload containing updated state, landing status, and impact metrics.
        """
        cmd = ThrustCommand.from_dict(thrust_command_dict) if thrust_command_dict is not None else None

        new_state, status, metrics = self.landing_physics.step_landing(
            current_state=current_state,
            dt=dt,
            descent_command=cmd,
        )

        return {
            "state": new_state.to_dict(),
            "landing_status": status.value,
            "metrics": metrics,
        }

    def evaluate_landing_safety(self, state: SpacecraftState) -> Dict[str, Any]:
        """
        Evaluates current descent safety, altitude, vertical descent speed, and touchdown state.
        """
        status, metrics = self.landing_physics.evaluate_touchdown(state)
        return {
            "status": status.value,
            "altitude_m": metrics["altitude"],
            "vertical_velocity_m_s": metrics["vertical_velocity"],
            "horizontal_velocity_m_s": metrics["horizontal_velocity"],
            "impact_speed_m_s": metrics["impact_speed"],
            "safe_touchdown_ready": status == LandingStatus.TOUCHDOWN_SUCCESS,
        }

    def get_landing_telemetry(self, state: SpacecraftState) -> Dict[str, Any]:
        """
        Returns real-time landing telemetry frame consumed by mission landing displays.
        """
        altitude = self.landing_physics.calculate_altitude(state.position)
        status, metrics = self.landing_physics.evaluate_touchdown(state)

        return {
            "timestamp": state.timestamp,
            "altitude": altitude,
            "vertical_velocity": metrics["vertical_velocity"],
            "horizontal_velocity": metrics["horizontal_velocity"],
            "fuel_remaining": state.fuel,
            "status": status.value,
            "position": state.position.to_dict(),
            "velocity": state.velocity.to_dict(),
        }
