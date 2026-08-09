import unittest
from datetime import datetime, timezone

from app.domain.model import seeded_environment


class SimulationModelTests(unittest.TestCase):
    def test_overdue_and_maintenance_are_visible_in_resident_status(self) -> None:
        environment = seeded_environment()
        now = datetime(2026, 1, 6, tzinfo=timezone.utc)

        environment.open_request(
            now,
            request_id="request-1",
            resident_id="resident-1",
            category="plumbing",
            description="Low water pressure",
        )

        self.assertEqual(
            environment.resident_status("resident-1", now),
            ["overdue_payment", "maintenance_request"],
        )
        self.assertEqual(environment.manager_status(now), ["overdue_payment", "maintenance_request"])

    def test_resolved_request_cannot_silently_reopen(self) -> None:
        environment = seeded_environment()
        now = datetime(2026, 1, 6, tzinfo=timezone.utc)
        environment.open_request(
            now,
            request_id="request-1",
            resident_id="resident-1",
            category="plumbing",
            description="Low water pressure",
        )
        for next_status in ("under_review", "planned", "in_progress", "resolved"):
            environment.change_request_status(
                now,
                request_id="request-1",
                manager_id="manager-1",
                next_status=next_status,
            )

        with self.assertRaises(ValueError):
            environment.change_request_status(
                now,
                request_id="request-1",
                manager_id="manager-1",
                next_status="in_progress",
            )
        self.assertEqual(len(environment.events), 5)
        self.assertEqual(environment.events[-1].payload["changed_by"], "manager-1")

    def test_event_history_rebuilds_the_same_projection(self) -> None:
        environment = seeded_environment()
        now = datetime(2026, 1, 6, tzinfo=timezone.utc)
        environment.open_request(
            now,
            request_id="request-1",
            resident_id="resident-1",
            category="plumbing",
            description="Low water pressure",
        )
        original_status = environment.resident_status("resident-1", now)
        rebuilt = environment.from_history(seeded_environment(), environment.events)

        self.assertEqual(rebuilt.resident_status("resident-1", now), original_status)
        self.assertEqual(rebuilt.events, environment.events)


if __name__ == "__main__":
    unittest.main()
