"""
ASTRAEA-IX — Mission Report REST API Endpoints
"""

from fastapi import APIRouter, Depends
from backend.models.response import ApiResponse
from backend.services.report_service import ReportService
from backend.api.mission import get_mission_service, MissionService

router = APIRouter()


@router.get("/report", response_model=ApiResponse)
def get_mission_report(mission_service: MissionService = Depends(get_mission_service)):
    report = ReportService.generate_report(mission_service)
    return ApiResponse(success=True, message="Mission report generated.", data=report.model_dump())
