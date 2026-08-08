"""
ASTRAEA-IX — Telemetry REST API Endpoints
"""

from fastapi import APIRouter, Depends
from backend.models.response import ApiResponse
from backend.services.telemetry_service import TelemetryService
from backend.api.mission import get_mission_service, MissionService

router = APIRouter()


@router.get("/telemetry", response_model=ApiResponse)
def get_telemetry(mission_service: MissionService = Depends(get_mission_service)):
    telemetry_service = TelemetryService(adapter=mission_service.adapter)
    frame = telemetry_service.generate_telemetry_frame(mission_service.current_true_state)
    return ApiResponse(success=True, message="Telemetry frame retrieved.", data=frame)
