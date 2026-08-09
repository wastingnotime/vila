from app.domain.model import Environment, notification_fatigue_environment

from .notification_fatigue import NOW


def run_multi_unit_status_slice() -> tuple[Environment, object, object]:
    environment = notification_fatigue_environment()
    environment.open_request(
        NOW,
        request_id="request-1",
        resident_id="resident-1",
        category="plumbing",
        description="Low water pressure",
    )
    environment.overdue_payments(NOW)
    environment.record_delivery("delivery-2", "unit-102", "Large package", NOW)
    return environment, environment.status_summary("resident-1", NOW), environment.status_summary("manager-1", NOW)
