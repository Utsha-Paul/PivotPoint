"""
ASTRAEA-IX — Application Configuration Settings
"""

import os
from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "ASTRAEA-IX"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*",
    ]
    WS_TELEMETRY_INTERVAL: float = 0.1  # 10 Hz telemetry broadcasting frequency
    DEFAULT_SEED: int = 42


settings = Settings()
