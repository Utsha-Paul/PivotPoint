"""
ASTRAEA-IX — Planetary Models
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class PlanetInfo(BaseModel):
    name: str
    distance_au: float
    mass_kg: float
    radius_m: float
    gravity_m_s2: float
    atmosphere: str
    hazards: list[str]
