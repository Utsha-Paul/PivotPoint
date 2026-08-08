"""
ASTRAEA-IX — AI Anomaly Detection and Navigation Confidence Estimator
"""

import math
from typing import Dict, Any, Tuple
from backend.simulation.vector3 import Vector3


class AnomalyDetector:
    """
    AI model evaluating spacecraft trajectory deviation and sensor degradation.
    Calculates Anomaly Score (0.0 to 1.0) and Navigation Confidence (0% to 100%).
    """

    def __init__(self, anomaly_threshold: float = 0.35) -> None:
        self.anomaly_threshold = float(anomaly_threshold)

    def evaluate(
        self,
        position_error: float,
        velocity_error: float,
        sensor_confidence: float = 1.0,
        comm_online: bool = True,
    ) -> Tuple[float, float, bool]:
        """
        Evaluates current physical state deviation and telemetry health.

        Returns:
            Tuple of (anomaly_score: float [0..1], navigation_confidence: float [0..100], anomaly_detected: bool).
        """
        # Anomaly score increases with position drift (scaled to 1e7 meters = 1.0) and velocity drift
        pos_score = min(1.0, position_error / 1e7)
        vel_score = min(1.0, velocity_error / 500.0)

        raw_anomaly = (pos_score * 0.7) + (vel_score * 0.3)
        if not comm_online:
            # Comm loss increases anomaly risk weight
            raw_anomaly = min(1.0, raw_anomaly + 0.15)

        anomaly_score = round(max(0.0, min(1.0, raw_anomaly)), 2)

        # Confidence drops as anomaly increases and sensor confidence drops
        confidence_pct = round(max(0.0, min(100.0, (1.0 - anomaly_score) * sensor_confidence * 100.0)), 1)
        anomaly_detected = anomaly_score >= self.anomaly_threshold

        return anomaly_score, confidence_pct, anomaly_detected
