"""
ASTRAEA-IX — Mission Data Models & State Machine Schemas
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class MissionState(str, Enum):
    IDLE = "IDLE"
    LAUNCH = "LAUNCH"
    CRUISE = "CRUISE"
    COMMUNICATION_LOSS = "COMMUNICATION_LOSS"
    AUTONOMOUS_RECOVERY = "AUTONOMOUS_RECOVERY"
    TRAJECTORY_CORRECTION = "TRAJECTORY_CORRECTION"
    RETURN_NAVIGATION = "RETURN_NAVIGATION"
    MISSION_SUCCESS = "MISSION_SUCCESS"
    MISSION_FAILED = "MISSION_FAILED"


class TrajectoryCandidate(BaseModel):
    id: str
    name: str  # 'Direct Correction', 'Low Energy Arc', 'Emergency Intercept'
    estimated_fuel: float  # kg
    estimated_time: float  # hours
    risk_score: float  # 0.0 to 1.0
    feasible: bool
    rejection_reason: Optional[str] = None
    delta_v: float  # m/s
    burn_duration: float  # seconds
    path: List[Dict[str, float]] = Field(default_factory=list)


class ScientificDataUpload(BaseModel):
    name: Optional[str] = "Custom User Spacecraft"
    dry_mass_kg: float = Field(gt=0, default=1000.0)
    fuel_mass_kg: float = Field(ge=0, default=1000.0)
    max_thrust_n: float = Field(gt=0, default=500.0)
    isp_sec: float = Field(gt=0, default=300.0)
    fuel_reserve_kg: float = Field(ge=0, default=100.0)


class MissionStatusResponse(BaseModel):
    mission_id: str
    status: MissionState
    simulation_speed: float
    comm_online: bool
    system_health: str
    elapsed_time: float
    time_remaining: float
    deadline: float
    current_fuel: float
    usable_fuel: float
    fuel_reserve: float
    fuel_percentage: float
    anomaly_score: float
    navigation_confidence: float
    selected_strategy: Optional[str] = None
    candidates: List[TrajectoryCandidate] = Field(default_factory=list)
