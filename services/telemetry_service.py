"""
ASTRAEA-IX — Telemetry Backend Service
Generates, packages, and manages sensor observation telemetry streams from physics TRUE STATE.
"""

from typing import Dict, List, Any, Optional
from backend.models.spacecraft import SpacecraftState
from backend.models.telemetry import SensorMeasurement, SensorHealth
from backend.simulation.adapter import PhysicsBackendAdapter


class TelemetryService:
    """
    Telemetry service responsible for providing simulated sensor observation streams.
    """

    def __init__(self, adapter: Optional[PhysicsBackendAdapter] = None) -> None:
        self.adapter = adapter if adapter is not None else PhysicsBackendAdapter()

    def generate_telemetry_frame(
        self,
        true_state: SpacecraftState,
    ) -> Dict[str, Any]:
        """
        Generates complete telemetry frame containing sensor measurements and true state telemetry metadata.

        Args:
            true_state: Spacecraft TRUE STATE.

        Returns:
            Dictionary containing sensor observations list and state summary.
        """
        measurements: List[SensorMeasurement] = self.adapter.observe(true_state)
        meas_dicts = [m.to_dict() for m in measurements]

        return {
            "timestamp": true_state.timestamp,
            "true_state_summary": {
                "position": true_state.position.to_dict(),
                "velocity": true_state.velocity.to_dict(),
                "fuel": true_state.fuel,
                "mass": true_state.mass,
            },
            "sensor_measurements": meas_dicts,
        }

    def set_sensor_health(self, sensor_type: str, health_status: str) -> None:
        """Sets operational health status for a specific sensor."""
        self.adapter.sensor_suite.set_sensor_health(sensor_type, health_status)
