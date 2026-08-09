import unittest

from datetime import datetime, timezone

from app.domain.model import seeded_environment
from app.simulation.status_summary import run_status_summary_slice


class StatusSummaryTests(unittest.TestCase):
    def test_resident_summary_prioritizes_actions_and_keeps_update_separate(self) -> None:
        _, resident, _ = run_status_summary_slice()

        self.assertEqual(resident.action_items, ("overdue_payment", "maintenance_request", "delivery"))
        self.assertEqual(resident.latest_update, "Water maintenance")
        self.assertEqual(resident.open_delivery_ids, ("delivery-1",))

    def test_manager_summary_uses_manager_attention_and_all_open_deliveries(self) -> None:
        _, _, manager = run_status_summary_slice()

        self.assertEqual(manager.action_items.count("overdue_payment"), 3)
        self.assertEqual(manager.action_items.count("maintenance_request"), 1)
        self.assertEqual(manager.action_items.count("delivery"), 1)
        self.assertEqual(manager.latest_update, "Water maintenance")

    def test_empty_summary_explicitly_answers_that_nothing_requires_action(self) -> None:
        environment = seeded_environment()
        summary = environment.status_summary("resident-1", datetime(2026, 1, 1, tzinfo=timezone.utc))

        self.assertEqual(summary.action_items, ())
        self.assertIsNone(summary.latest_update)
        self.assertEqual(summary.open_delivery_ids, ())


if __name__ == "__main__":
    unittest.main()
