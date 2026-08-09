import unittest
from datetime import datetime, timezone

from app.domain.model import notification_fatigue_environment
from app.simulation.membership_history import MOVE_AT, run_membership_history_slice


class MembershipHistoryTests(unittest.TestCase):
    def test_move_changes_current_status_without_erasing_history(self) -> None:
        environment, status = run_membership_history_slice()

        self.assertEqual(status, ["overdue_payment"])
        self.assertEqual(environment.unit_for_resident("resident-1", MOVE_AT), "unit-102")
        self.assertEqual(len(environment.membership_history), 5)

    def test_previous_unit_activity_remains_auditable(self) -> None:
        environment = notification_fatigue_environment()
        opened_at = datetime(2026, 1, 6, tzinfo=timezone.utc)
        environment.open_request(
            opened_at,
            request_id="request-1",
            resident_id="resident-1",
            category="plumbing",
            description="Low water pressure",
        )
        environment.move_resident("resident-1", "unit-102", MOVE_AT)

        self.assertEqual(environment.requests["request-1"].unit_id, "unit-101")
        with self.assertRaises(KeyError):
            environment.unit_for_resident("resident-1", datetime(2025, 12, 31, tzinfo=timezone.utc))


if __name__ == "__main__":
    unittest.main()
