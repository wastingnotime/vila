from app.domain.model import Environment, notification_fatigue_environment

from .notification_fatigue import NOW


def run_status_summary_slice() -> tuple[Environment, object, object]:
    environment = notification_fatigue_environment()
    environment.open_request(
        NOW,
        request_id="request-1",
        resident_id="resident-1",
        category="plumbing",
        description="Low water pressure",
    )
    environment.overdue_payments(NOW)
    environment.record_delivery("delivery-1", "unit-101", "Small package", NOW, recorded_by="manager-1")
    environment.publish_announcement(
        "announcement-1",
        "Water maintenance",
        "Water will be unavailable Thursday.",
        "normal",
        NOW,
        published_by="manager-1",
    )
    return environment, environment.status_summary("resident-1", NOW), environment.status_summary("manager-1", NOW)
