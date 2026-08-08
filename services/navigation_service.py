"""
ASTRAEA-IX — Navigation Backend Service
Coordinates physics simulation state updates, trajectory predictions, Earth position queries,
and AI maneuver correction commands for the mission backend.
"""

from typing import Dict, List, Any, Optional
from backend.models.spacecraft import SpacecraftState
from backend.simulation.adapter import PhysicsBackendAdapter
from backend.simulation.vector3 import Vector3
from backend.simulation.thrust import ThrustCommand
from backend.simulation.disturbances import DisturbanceConfig


class NavigationService:
    """
    Service wrapper around the physics engine adapter providing mission navigation routines.
    """

    def __init__(self, adapter: Optional[PhysicsBackendAdapter] = None) -> None:
        self.adapter = adapter if adapter is not None else PhysicsBackendAdapter()

    def set_simulation_seed(self, seed: Optional[int]) -> None:
        """Configures deterministic seed for physics engine and sensors."""
        self.adapter.set_seed(seed)

    def step_simulation(
        self,
        current_state: SpacecraftState,
        dt: float,
        command_dict: Optional[Dict[str, Any]] = None,
        disturbance_dict: Optional[Dict[str, Any]] = None,
    ) -> SpacecraftState:
        """
        Executes a physics propagation step.

        Args:
            current_state: Current SpacecraftState (TRUE STATE).
            dt: Integration timestep in seconds.
            command_dict: Optional maneuver command payload.
            disturbance_dict: Optional disturbance parameters.

        Returns:
            Updated SpacecraftState (TRUE STATE).
        """
        return self.adapter.update(
            state=current_state,
            dt=dt,
            control_input=command_dict,
            disturbance_config=disturbance_dict,
        )

    def apply_ai_correction(
        self,
        current_state: SpacecraftState,
        correction_command: Dict[str, Any],
        dt: float = 1.0,
    ) -> SpacecraftState:
        """
        Applies a correction command issued by the AI navigation decision engine to the true state.

        Args:
            current_state: Current TRUE state.
            correction_command: Dict with 'direction', 'magnitude', 'duration'.
            dt: Timestep in seconds.

        Returns:
            New SpacecraftState after applying maneuver force.
        """
        cmd = ThrustCommand.from_dict(correction_command)
        return self.adapter.update(
            state=current_state,
            dt=dt,
            control_input=cmd,
        )

    def get_earth_position(self, elapsed_time: float) -> Dict[str, Any]:
        """Returns Earth position dict at elapsed mission time."""
        pos = self.adapter.earth_position(elapsed_time)
        return {
            "elapsed_time": elapsed_time,
            "position": pos.to_dict(),
        }

    def predict_trajectory(
        self,
        current_state: SpacecraftState,
        duration: float = 3600.0,
        dt: float = 60.0,
        planned_command: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generates predicted trajectory positions over a forecast horizon.
        """
        return self.adapter.propagate_trajectory(
            initial_state=current_state,
            duration=duration,
            dt=dt,
            control_input=planned_command,
        )
