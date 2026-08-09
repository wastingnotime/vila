from app.domain.model import Environment, notification_fatigue_environment

from .notification_fatigue import NOW


def run_activity_history_slice() -> tuple[Environment, list[str], list[str]]:
    environment = notification_fatigue_environment()
    environment.open_request(
        NOW,
        request_id="request-1",
        resident_id="resident-1",
        category="plumbing",
        description="Water pressure is low in the kitchen.",
    )
    environment.change_request_status(
        NOW,
        request_id="request-1",
        manager_id="manager-1",
        next_status="under_review",
    )
    resident = [item.summary for item in environment.activity_history("resident-1", NOW)]
    manager = [item.summary for item in environment.activity_history("manager-1", NOW)]
    return environment, resident, manager
