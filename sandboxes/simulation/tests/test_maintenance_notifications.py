import unittest

from app.simulation.maintenance_notifications import run_maintenance_notification_slice


class MaintenanceNotificationTests(unittest.TestCase):
    def test_status_update_reaches_each_resident_of_shared_unit(self) -> None:
        environment, recipients = run_maintenance_notification_slice()

        self.assertEqual(recipients, ["resident-1", "resident-1b"])
        self.assertEqual(
            [notification.kind for notification in environment.notifications],
            ["maintenance_status_under_review", "maintenance_status_under_review"],
        )

    def test_status_update_is_idempotent_for_each_recipient(self) -> None:
        environment, _ = run_maintenance_notification_slice()

        self.assertEqual(environment.maintenance_status_notifications("request-1", environment.notifications[0].at), [])
        self.assertEqual(len(environment.notifications), 2)

    def test_two_requests_are_aggregated_without_losing_the_second_request(self) -> None:
        environment, _ = run_maintenance_notification_slice()
        environment.open_request(
            environment.notifications[0].at,
            request_id="request-2",
            resident_id="resident-1",
            category="electrical",
            description="Hall light is flickering.",
        )
        environment.change_request_status(
            environment.notifications[0].at,
            request_id="request-2",
            manager_id="manager-1",
            next_status="under_review",
        )
        environment.maintenance_status_notifications("request-2", environment.notifications[0].at)

        self.assertEqual(len(environment.notifications), 2)
        self.assertEqual(environment.notifications[0].item_count, 2)
        self.assertEqual(environment.notifications[0].item_ids, ("request-1", "request-2"))


if __name__ == "__main__":
    unittest.main()
