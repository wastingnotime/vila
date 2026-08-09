from datetime import datetime, timezone

from app.domain.model import Environment, Payment, notification_fatigue_environment


MOVE_AT = datetime(2026, 1, 10, tzinfo=timezone.utc)


def run_membership_history_slice() -> tuple[Environment, list[str]]:
    environment = notification_fatigue_environment()
    environment.move_resident("resident-1", "unit-102", MOVE_AT)
    environment.payments.append(
        Payment(unit_id="unit-102", due_at=datetime(2026, 1, 12, tzinfo=timezone.utc))
    )
    return environment, environment.resident_status("resident-1", MOVE_AT)
