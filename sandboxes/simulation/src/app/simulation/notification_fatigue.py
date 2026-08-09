from datetime import datetime, timezone

from app.domain.model import Environment, notification_fatigue_environment


NOW = datetime(2026, 1, 6, tzinfo=timezone.utc)


def run_notification_fatigue_slice() -> tuple[Environment, list[str]]:
    environment = notification_fatigue_environment()
    environment.open_request(
        NOW,
        request_id="request-1",
        resident_id="resident-1",
        category="plumbing",
        description="Water pressure is low in the kitchen.",
    )
    environment.overdue_payments(NOW)
    notifications = environment.actionable_notifications("manager-1", NOW)
    return environment, [notification.kind for notification in notifications]
