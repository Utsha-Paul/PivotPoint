"""
ASTRAEA-IX — End-of-Mission Report Backend Service
Generates post-mission performance analytics, prediction error comparisons, and telemetry summaries.
"""

from typing import Dict, Any, List
from backend.models.response import MissionReport
from backend.services.mission_service import MissionService


class ReportService:
    """
    Generates structured end-of-mission performance reports.
    """

    @staticmethod
    def generate_report(mission_service: MissionService) -> MissionReport:
        """
        Calculates end-of-mission metrics comparing predicted vs actual fuel and time.
        """
        summary = mission_service.get_status_summary()

        initial_fuel = mission_service.fuel_manager.initial_fuel
        current_fuel = summary["current_fuel"]
        spent_fuel = summary["spent_fuel"]
        duration = summary["elapsed_time"]
        rec_duration = mission_service.recovery_duration

        # Nominal predictions
        pred_fuel = 200.0  # kg nominal predicted burn
        pred_time = 3600.0 * 18.0  # 18 hours nominal predicted duration

        fuel_err_pct = round(abs((spent_fuel - pred_fuel) / max(1.0, pred_fuel)) * 100.0, 1)
        time_err_pct = round(abs((duration - pred_time) / max(1.0, pred_time)) * 100.0, 1)

        events_data = [
            {
                "timestamp": evt.timestamp,
                "time_str": evt.time_str,
                "event_type": evt.event_type,
                "message": evt.message,
                "severity": evt.severity,
            }
            for evt in mission_service.event_log
        ]

        return MissionReport(
            mission_id=mission_service.mission_id,
            status=summary["status"],
            initial_fuel=initial_fuel,
            final_fuel=current_fuel,
            fuel_used=spent_fuel,
            mission_duration=round(duration, 1),
            recovery_duration=round(rec_duration, 1),
            max_navigation_error=round(mission_service.max_nav_error, 2),
            final_navigation_error=round(summary["position_error"], 2),
            max_anomaly_score=round(mission_service.max_anomaly_score, 2),
            number_of_corrections=mission_service.number_of_corrections,
            comm_loss_duration=round(mission_service.comm_loss_duration, 1),
            selected_strategy=mission_service.selected_strategy or "N/A",
            predicted_fuel=pred_fuel,
            actual_fuel=spent_fuel,
            fuel_prediction_error_percent=fuel_err_pct,
            predicted_time=pred_time,
            actual_time=round(duration, 1),
            time_prediction_error_percent=time_err_pct,
            events_summary=events_data,
        )
