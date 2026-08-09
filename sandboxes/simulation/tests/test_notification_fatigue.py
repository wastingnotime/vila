import unittest

from app.simulation.notification_fatigue import NOW, run_notification_fatigue_slice


class NotificationFatigueTests(unittest.TestCase):
    def test_overdue_obligations_are_summarized_without_per_payment_notifications(self) -> None:
        environment, notification_kinds = run_notification_fatigue_slice()

        self.assertEqual(len(environment.overdue_payments(NOW)), 3)
        self.assertEqual(environment.manager_status(NOW).count("overdue_payment"), 3)
        self.assertEqual(notification_kinds, ["maintenance_review_required"])
        self.assertEqual(environment.notifications[0].item_count, 1)

    def test_repeated_status_refresh_does_not_repeat_daily_notification(self) -> None:
        environment, _ = run_notification_fatigue_slice()

        self.assertEqual(environment.actionable_notifications("manager-1", NOW), [])
        self.assertEqual(len(environment.notifications), 1)


if __name__ == "__main__":
    unittest.main()
