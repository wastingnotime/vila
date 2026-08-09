import unittest

from datetime import datetime, timezone

from app.domain.model import notification_fatigue_environment
from app.simulation.activity_history import run_activity_history_slice
from app.simulation.membership_history import MOVE_AT


class ActivityHistoryTests(unittest.TestCase):
    def test_resident_sees_relevant_human_readable_activity(self) -> None:
        _, resident, _ = run_activity_history_slice()

        self.assertEqual(
            resident,
            [
                "Payment is overdue",
                "Maintenance request submitted",
                "Maintenance request under review",
            ],
        )

    def test_manager_sees_condominium_activity(self) -> None:
        _, _, manager = run_activity_history_slice()

        self.assertEqual(len(manager), 5)
        self.assertNotIn("maintenance_opened", manager)
        self.assertIn("Maintenance request under review", manager)

    def test_resident_retains_historical_activity_after_moving_units(self) -> None:
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

        history = environment.activity_history("resident-1", MOVE_AT)

        self.assertTrue(any(item.subject_id == "request-1" for item in history))
        self.assertEqual(environment.resident_status("resident-1", MOVE_AT), ["overdue_payment"])


if __name__ == "__main__":
    unittest.main()
