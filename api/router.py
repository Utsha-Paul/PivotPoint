"""
ASTRAEA-IX — Central REST API Router Aggregator
"""

from fastapi import APIRouter
from backend.api.mission import router as mission_router
from backend.api.telemetry import router as telemetry_router
from backend.api.report import router as report_router

api_router = APIRouter(prefix="/api")

@api_router.get("/health")
def health_check():
    return {"status": "ONLINE", "system": "ASTRAEA-IX Autonomous Navigation Engine"}

api_router.include_router(mission_router)
api_router.include_router(telemetry_router)
api_router.include_router(report_router)
