import unittest
from datetime import datetime, timezone

from app.domain.model import notification_fatigue_environment


class PermissionTests(unittest.TestCase):
    def test_resident_can_open_request_but_cannot_change_its_status(self) -> None:
        environment = notification_fatigue_environment()
        now = datetime(2026, 1, 6, tzinfo=timezone.utc)
        environment.open_request(
            now,
            request_id="request-1",
            resident_id="resident-1",
            category="plumbing",
            description="Low water pressure",
        )

        with self.assertRaises(PermissionError):
            environment.change_request_status(
                now,
                request_id="request-1",
                manager_id="resident-1",
                next_status="under_review",
            )

    def test_manager_can_change_status_after_resident_submits(self) -> None:
        environment = notification_fatigue_environment()
        now = datetime(2026, 1, 6, tzinfo=timezone.utc)
        environment.open_request(
            now,
            request_id="request-1",
            resident_id="resident-1",
            category="plumbing",
            description="Low water pressure",
        )

        environment.change_request_status(
            now,
            request_id="request-1",
            manager_id="manager-1",
            next_status="under_review",
        )
        self.assertEqual(environment.requests["request-1"].status, "under_review")

    def test_unknown_actor_cannot_submit_resident_request(self) -> None:
        environment = notification_fatigue_environment()
        now = datetime(2026, 1, 6, tzinfo=timezone.utc)

        with self.assertRaises(PermissionError):
            environment.open_request(
                now,
                request_id="request-1",
                resident_id="unknown-user",
                category="plumbing",
                description="Low water pressure",
            )


if __name__ == "__main__":
    unittest.main()
