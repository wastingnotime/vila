from datetime import datetime, timedelta, timezone

from app.domain.model import Environment, Payment, notification_fatigue_environment


UNITS = ("unit-101", "unit-102", "unit-103")


def run_monthly_obligations(months: int = 3) -> tuple[Environment, list[int]]:
    if not 1 <= months <= 12:
        raise ValueError("months must be between 1 and 12")
    environment = notification_fatigue_environment()
    environment.payments.clear()
    overdue_counts: list[int] = []
    for month in range(1, months + 1):
        due_at = datetime(2026, month, 5, tzinfo=timezone.utc)
        for unit_id in UNITS:
            environment.payments.append(Payment(unit_id=unit_id, due_at=due_at))
        review_at = due_at + timedelta(days=1)
        environment.overdue_payments(review_at)
        first_index = len(environment.payments) - len(UNITS)
        environment.mark_payment_paid(first_index, review_at)
        environment.mark_payment_paid(first_index + 1, review_at)
        overdue_counts.append(len(environment.overdue_payments(review_at)))
    return environment, overdue_counts
