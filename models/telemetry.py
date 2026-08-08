"""
ASTRAEA-IX — Telemetry and Sensor Measurement Data Models
Defines standard schemas for sensor observations, health states, and telemetry payloads.
"""

from enum import Enum
from typing import Dict, Any, Union, List
from backend.simulation.vector3 import Vector3


class SensorHealth(str, Enum):
    """Enumeration of supported sensor operational health states."""

    NORMAL = "NORMAL"
    NOISY = "NOISY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


class SensorMeasurement:
    """
    Standard schema for measurements produced by spacecraft sensors.
    
    Attributes:
        sensor_type: Name/type of the sensor (e.g. 'accelerometer', 'gyroscope', 'star_tracker', 'sun_sensor', 'imu')
        timestamp: Simulation timestamp in seconds (s)
        measurement: Sensor observation vector or value (Vector3, dict, or float)
        noise_level: Configured noise standard deviation applied to measurement
        confidence: Estimated confidence score between 0.0 (unusable) and 1.0 (perfect)
        health: Current operational health status ('NORMAL', 'NOISY', 'DEGRADED', 'FAILED')
    """

    def __init__(
        self,
        sensor_type: str,
        timestamp: float,
        measurement: Union[Vector3, float, Dict[str, Any], List[float]],
        noise_level: float = 0.0,
        confidence: float = 1.0,
        health: Union[SensorHealth, str] = SensorHealth.NORMAL,
    ) -> None:
        self.sensor_type = str(sensor_type)
        self.timestamp = float(timestamp)
        self.measurement = measurement
        self.noise_level = float(noise_level)
        self.confidence = max(0.0, min(1.0, float(confidence)))
        self.health = SensorHealth(health) if isinstance(health, str) else health

    def to_dict(self) -> Dict[str, Any]:
        """Converts SensorMeasurement to JSON-compatible dictionary."""
        meas_val = self.measurement
        if isinstance(meas_val, Vector3):
            meas_val = meas_val.to_list()
        elif isinstance(meas_val, dict):
            meas_val = {
                k: v.to_list() if isinstance(v, Vector3) else v
                for k, v in meas_val.items()
            }

        return {
            "sensor_type": self.sensor_type,
            "timestamp": self.timestamp,
            "measurement": meas_val,
            "noise_level": self.noise_level,
            "confidence": self.confidence,
            "health": self.health.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SensorMeasurement":
        """Constructs SensorMeasurement from dictionary."""
        raw_meas = data.get("measurement")
        if isinstance(raw_meas, list) and len(raw_meas) == 3:
            meas = Vector3.from_list(raw_meas)
        else:
            meas = raw_meas

        return cls(
            sensor_type=data.get("sensor_type", "unknown"),
            timestamp=data.get("timestamp", 0.0),
            measurement=meas,
            noise_level=data.get("noise_level", 0.0),
            confidence=data.get("confidence", 1.0),
            health=data.get("health", SensorHealth.NORMAL),
        )

    def __repr__(self) -> str:
        return (
            f"SensorMeasurement(type='{self.sensor_type}', t={self.timestamp:.2f}s, "
            f"meas={self.measurement}, confidence={self.confidence:.2f}, health='{self.health.value}')"
        )
