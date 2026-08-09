import unittest

from app.simulation.multi_unit_status import run_multi_unit_status_slice


class MultiUnitStatusTests(unittest.TestCase):
    def test_resident_summary_stays_limited_to_current_unit(self) -> None:
        _, resident, _ = run_multi_unit_status_slice()

        self.assertEqual(resident.action_items, ("overdue_payment", "maintenance_request"))
        self.assertEqual(resident.open_delivery_ids, ())

    def test_manager_summary_covers_condominium_scope(self) -> None:
        _, _, manager = run_multi_unit_status_slice()

        self.assertEqual(manager.action_items.count("overdue_payment"), 3)
        self.assertEqual(manager.action_items.count("maintenance_request"), 1)
        self.assertEqual(manager.action_items.count("delivery"), 1)
        self.assertEqual(manager.open_delivery_ids, ("delivery-2",))


if __name__ == "__main__":
    unittest.main()
