import unittest
from datetime import timedelta

from app.simulation.notification_fatigue import NOW, run_notification_fatigue_slice


class NotificationFatigueTests(unittest.TestCase):
    def test_overdue_obligations_are_summarized_without_per_payment_notifications(self) -> None:
        environment, notification_kinds = run_notification_fatigue_slice()

        self.assertEqual(len(environment.overdue_payments(NOW)), 3)
        self.assertEqual(environment.manager_status(NOW).count("overdue_payment"), 3)
        self.assertEqual(notification_kinds, ["maintenance_review_required"])
        self.assertEqual(environment.notifications[0].item_count, 1)
        self.assertEqual(environment.notifications[0].item_ids, ("request-1",))

    def test_repeated_status_refresh_does_not_repeat_daily_notification(self) -> None:
        environment, _ = run_notification_fatigue_slice()

        self.assertEqual(environment.actionable_notifications("manager-1", NOW), [])
        self.assertEqual(len(environment.notifications), 1)

    def test_shared_unit_residents_see_the_same_unit_level_status(self) -> None:
        environment, _ = run_notification_fatigue_slice()

        self.assertEqual(
            environment.resident_status("resident-1", NOW),
            environment.resident_status("resident-1b", NOW),
        )
        self.assertEqual(
            environment.resident_status("resident-1b", NOW),
            ["overdue_payment", "maintenance_request"],
        )

    def test_future_request_does_not_trigger_early_manager_notification(self) -> None:
        environment, _ = run_notification_fatigue_slice()
        future = NOW + timedelta(days=1)
        environment.open_request(
            future,
            request_id="future-request",
            resident_id="resident-1",
            category="plumbing",
            description="Not submitted yet in the current window.",
        )
        environment.notifications.clear()

        notifications = environment.actionable_notifications("manager-1", NOW)

        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].item_count, 1)

    def test_unknown_actor_cannot_request_manager_notifications(self) -> None:
        environment, _ = run_notification_fatigue_slice()

        with self.assertRaises(PermissionError):
            environment.actionable_notifications("unknown-user", NOW)


if __name__ == "__main__":
    unittest.main()
