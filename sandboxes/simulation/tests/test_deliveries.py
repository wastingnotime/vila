import unittest

from app.simulation.deliveries import run_delivery_slice
from app.simulation.notification_fatigue import NOW


class DeliveryTests(unittest.TestCase):
    def test_resident_sees_only_open_deliveries_for_their_unit(self) -> None:
        environment, delivery_ids = run_delivery_slice()

        self.assertEqual(delivery_ids, ["delivery-1"])
        self.assertEqual([delivery.delivery_id for delivery in environment.open_deliveries("manager-1", NOW)], ["delivery-1", "delivery-2"])

    def test_collection_removes_delivery_from_open_items_but_keeps_history(self) -> None:
        environment, _ = run_delivery_slice()

        environment.collect_delivery("delivery-1", "resident-1", NOW)

        self.assertEqual(environment.open_deliveries("resident-1", NOW), [])
        self.assertEqual(environment.deliveries["delivery-1"].status, "collected")
        self.assertEqual(environment.deliveries["delivery-1"].collected_at, NOW)

    def test_resident_cannot_collect_another_unit_delivery(self) -> None:
        environment, _ = run_delivery_slice()

        with self.assertRaises(PermissionError):
            environment.collect_delivery("delivery-2", "resident-1", NOW)


if __name__ == "__main__":
    unittest.main()
