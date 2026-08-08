"""
ASTRAEA-IX — API Response & End-of-Mission Report Models
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class MissionReport(BaseModel):
    mission_id: str
    status: str
    initial_fuel: float
    final_fuel: float
    fuel_used: float
    mission_duration: float
    recovery_duration: float
    max_navigation_error: float
    final_navigation_error: float
    max_anomaly_score: float
    number_of_corrections: int
    comm_loss_duration: float
    selected_strategy: str
    predicted_fuel: float
    actual_fuel: float
    fuel_prediction_error_percent: float
    predicted_time: float
    actual_time: float
    time_prediction_error_percent: float
    events_summary: List[Dict[str, Any]]
