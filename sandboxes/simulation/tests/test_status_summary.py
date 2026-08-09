import unittest

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


if __name__ == "__main__":
    unittest.main()
