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


if __name__ == "__main__":
    unittest.main()
