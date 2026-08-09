from datetime import datetime, timezone

from app.domain.model import Environment, notification_fatigue_environment


NOW = datetime(2026, 1, 6, tzinfo=timezone.utc)


def run_announcement_slice() -> tuple[Environment, list[str]]:
    environment = notification_fatigue_environment()
    environment.publish_announcement(
        "announcement-1",
        "Water maintenance",
        "Water will be unavailable Thursday from 09:00 to 11:00.",
        "normal",
        NOW.replace(day=5),
    )
    environment.publish_announcement(
        "announcement-2",
        "Emergency elevator outage",
        "The elevator is temporarily unavailable.",
        "high",
        NOW,
        NOW.replace(day=7),
    )
    return environment, [announcement.title for announcement in environment.active_announcements(NOW)]
