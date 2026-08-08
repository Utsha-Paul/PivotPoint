"""
ASTRAEA-IX — Mission Event Log & Disturbance Request Models
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class MissionEvent(BaseModel):
    timestamp: float
    time_str: str
    event_type: str  # e.g., 'CRUISE_STARTED', 'DISTURBANCE_DETECTED', 'COMM_LOST', 'AI_RECOVERY_INITIATED', 'CORRECTION_EXECUTED'
    message: str
    severity: str = "INFO"  # INFO, WARNING, CRITICAL, SUCCESS


class DisturbanceRequest(BaseModel):
    navigation_drift: float = 0.05
    thruster_error: float = 0.15
    sensor_noise: float = 0.08
    environmental_acc: list[float] = [0.005, 0.005, 0.0]
