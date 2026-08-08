"""
ASTRAEA-IX — Resource Management Subsystem: Mission Clock
Tracks mission elapsed time, time remaining, simulation speed multipliers (1x, 5x, 10x, 50x, 100x), and deadlines.
"""

from typing import Dict, Any


class MissionClock:
    """
    Manages mission elapsed time and speed factor scaling.
    """

    def __init__(self, deadline_seconds: float = 86400.0 * 24) -> None:  # 24 hours default
        self.elapsed_time = 0.0
        self.deadline = float(deadline_seconds)
        self.speed_multiplier = 1.0

    def reset(self) -> None:
        self.elapsed_time = 0.0
        self.speed_multiplier = 1.0

    def set_speed(self, speed: float) -> float:
        self.speed_multiplier = max(0.1, min(100.0, float(speed)))
        return self.speed_multiplier

    def advance(self, dt: float) -> float:
        scaled_dt = float(dt) * self.speed_multiplier
        self.elapsed_time += scaled_dt
        return self.elapsed_time

    @property
    def time_remaining(self) -> float:
        return max(0.0, self.deadline - self.elapsed_time)

    def is_deadline_exceeded(self) -> bool:
        return self.elapsed_time >= self.deadline

    def get_summary(self) -> Dict[str, float]:
        return {
            "elapsed_time": self.elapsed_time,
            "time_remaining": self.time_remaining,
            "deadline": self.deadline,
            "speed_multiplier": self.speed_multiplier,
        }
