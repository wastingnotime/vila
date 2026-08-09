from datetime import datetime, timedelta, timezone

from app.domain.model import Environment, notification_fatigue_environment


def run_maintenance_queue(months: int = 3) -> tuple[Environment, list[int]]:
    if not 1 <= months <= 12:
        raise ValueError("months must be between 1 and 12")
    environment = notification_fatigue_environment()
    queue_sizes: list[int] = []
    residents = ("resident-1", "resident-2")
    for month in range(1, months + 1):
        arrived_at = datetime(2026, month, 6, tzinfo=timezone.utc)
        for suffix, resident_id in zip(("a", "b"), residents):
            environment.open_request(
                arrived_at,
                request_id=f"request-{month}-{suffix}",
                resident_id=resident_id,
                category="plumbing",
                description=f"Monthly issue {month}-{suffix}",
            )
        response_at = arrived_at + timedelta(days=2)
        environment.change_request_status(
            response_at,
            request_id=f"request-{month}-a",
            manager_id="manager-1",
            next_status="under_review",
        )
        queue_sizes.append(
            sum(
                request.status in {"submitted", "under_review"}
                for request in environment.requests.values()
            )
        )
    return environment, queue_sizes
