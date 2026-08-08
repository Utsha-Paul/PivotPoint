"""
ASTRAEA-IX — Spacecraft State Models
Defines the physical state of the spacecraft using SI units internally.
"""

from typing import Dict, Any
from backend.simulation.vector3 import Vector3


class SpacecraftState:
    """
    Represents the TRUE physical state of the spacecraft at a given timestamp.
    
    Units (SI):
    - timestamp: seconds (s)
    - position: meters (m) [Cartesian coordinates]
    - velocity: meters/second (m/s)
    - acceleration: meters/second² (m/s²)
    - mass: total spacecraft mass in kilograms (kg)
    - fuel: remaining fuel mass in kilograms (kg)
    - dry_mass: structural spacecraft mass without fuel in kilograms (kg)
    """

    def __init__(
        self,
        timestamp: float = 0.0,
        position: Vector3 = None,
        velocity: Vector3 = None,
        acceleration: Vector3 = None,
        dry_mass: float = 1000.0,
        fuel: float = 500.0,
    ) -> None:
        self.timestamp = float(timestamp)
        self.position = position if position is not None else Vector3.zero()
        self.velocity = velocity if velocity is not None else Vector3.zero()
        self.acceleration = acceleration if acceleration is not None else Vector3.zero()
        self.dry_mass = float(dry_mass)
        self.fuel = max(0.0, float(fuel))

    @property
    def mass(self) -> float:
        """Total current mass (dry mass + remaining fuel mass) in kg."""
        return self.dry_mass + self.fuel

    def copy(self) -> "SpacecraftState":
        """Creates a deep copy of the SpacecraftState."""
        return SpacecraftState(
            timestamp=self.timestamp,
            position=Vector3(self.position.x, self.position.y, self.position.z),
            velocity=Vector3(self.velocity.x, self.velocity.y, self.velocity.z),
            acceleration=Vector3(self.acceleration.x, self.acceleration.y, self.acceleration.z),
            dry_mass=self.dry_mass,
            fuel=self.fuel,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts state to a JSON-serializable dictionary."""
        return {
            "timestamp": self.timestamp,
            "position": self.position.to_dict(),
            "velocity": self.velocity.to_dict(),
            "acceleration": self.acceleration.to_dict(),
            "mass": self.mass,
            "fuel": self.fuel,
            "dry_mass": self.dry_mass,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpacecraftState":
        """Constructs SpacecraftState from a dictionary."""
        pos_data = data.get("position", {})
        vel_data = data.get("velocity", {})
        acc_data = data.get("acceleration", {})

        pos = Vector3.from_dict(pos_data) if isinstance(pos_data, dict) else Vector3.from_list(pos_data)
        vel = Vector3.from_dict(vel_data) if isinstance(vel_data, dict) else Vector3.from_list(vel_data)
        acc = Vector3.from_dict(acc_data) if isinstance(acc_data, dict) else Vector3.from_list(acc_data)

        return cls(
            timestamp=data.get("timestamp", 0.0),
            position=pos,
            velocity=vel,
            acceleration=acc,
            dry_mass=data.get("dry_mass", 1000.0),
            fuel=data.get("fuel", 500.0),
        )

    def __repr__(self) -> str:
        return (
            f"SpacecraftState(t={self.timestamp:.2f}s, "
            f"pos={self.position}, vel={self.velocity}, "
            f"mass={self.mass:.1f}kg, fuel={self.fuel:.1f}kg)"
        )
