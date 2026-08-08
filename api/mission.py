"""
ASTRAEA-IX — Mission Control REST API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from backend.models.response import ApiResponse
from backend.models.events import DisturbanceRequest
from backend.models.mission import ScientificDataUpload
from backend.services.mission_service import MissionService

router = APIRouter()

# Global mission service singleton instance for backend state persistence
global_mission_service = MissionService()


def get_mission_service() -> MissionService:
    return global_mission_service


@router.get("/mission", response_model=ApiResponse)
def get_mission_status(service: MissionService = Depends(get_mission_service)):
    summary = service.get_status_summary()
    return ApiResponse(success=True, message="Mission status retrieved.", data=summary)


@router.post("/mission/start", response_model=ApiResponse)
def start_mission(service: MissionService = Depends(get_mission_service)):
    summary = service.start_mission()
    return ApiResponse(success=True, message="Mission started.", data=summary)


@router.post("/mission/pause", response_model=ApiResponse)
def pause_mission(service: MissionService = Depends(get_mission_service)):
    summary = service.pause_mission()
    return ApiResponse(success=True, message="Mission paused.", data=summary)


@router.post("/mission/resume", response_model=ApiResponse)
def resume_mission(service: MissionService = Depends(get_mission_service)):
    summary = service.resume_mission()
    return ApiResponse(success=True, message="Mission resumed.", data=summary)


@router.post("/mission/reset", response_model=ApiResponse)
def reset_mission(service: MissionService = Depends(get_mission_service)):
    summary = service.reset_mission()
    return ApiResponse(success=True, message="Mission reset.", data=summary)


@router.post("/mission/communication-loss", response_model=ApiResponse)
def trigger_communication_loss(service: MissionService = Depends(get_mission_service)):
    summary = service.trigger_communication_loss()
    return ApiResponse(success=True, message="Communication loss triggered.", data=summary)


@router.post("/mission/disturbance", response_model=ApiResponse)
def trigger_disturbance(req: DisturbanceRequest = None, service: MissionService = Depends(get_mission_service)):
    summary = service.trigger_disturbance(req)
    return ApiResponse(success=True, message="Disturbance injected.", data=summary)


@router.post("/mission/backtrack", response_model=ApiResponse)
def trigger_backtrack(service: MissionService = Depends(get_mission_service)):
    summary = service.run_backtracking_recovery()
    return ApiResponse(success=True, message="AI Backtracking Solver executed and maneuver applied.", data=summary)


@router.post("/mission/upload-scientific-data", response_model=ApiResponse)
def upload_scientific_data(
    data: ScientificDataUpload,
    service: MissionService = Depends(get_mission_service),
):
    summary = service.upload_scientific_data(data)
    return ApiResponse(success=True, message="Scientific data loaded successfully.", data=summary)
