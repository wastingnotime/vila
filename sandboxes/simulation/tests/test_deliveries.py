import unittest

from app.domain.model import Delivery, notification_fatigue_environment
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

    def test_any_building_manager_can_collect_a_delivery(self) -> None:
        environment, _ = run_delivery_slice()
        environment.roles["manager-2"] = "building_manager"

        environment.collect_delivery("delivery-2", "manager-2", NOW)

        self.assertEqual(environment.deliveries["delivery-2"].status, "collected")

    def test_duplicate_delivery_id_cannot_overwrite_history(self) -> None:
        environment, _ = run_delivery_slice()

        with self.assertRaises(ValueError):
            environment.record_delivery("delivery-1", "unit-101", "Replacement package", NOW, recorded_by="manager-1")
        self.assertEqual(environment.deliveries["delivery-1"].description, "Small package")

    def test_foreign_condominium_delivery_is_not_visible(self) -> None:
        environment, _ = run_delivery_slice()
        environment.deliveries["foreign-1"] = Delivery(
            delivery_id="foreign-1",
            condominium_id="other-condo",
            unit_id="unit-101",
            description="Foreign package",
            received_at=NOW,
        )

        self.assertNotIn("foreign-1", [delivery.delivery_id for delivery in environment.open_deliveries("manager-1", NOW)])

    def test_delivery_cannot_be_collected_before_receipt(self) -> None:
        environment, _ = run_delivery_slice()
        future = NOW.replace(day=8)
        environment.record_delivery("future-1", "unit-101", "Future package", future, recorded_by="manager-1")

        with self.assertRaises(ValueError):
            environment.collect_delivery("future-1", "resident-1", NOW)

        self.assertEqual(environment.deliveries["future-1"].status, "waiting")

    def test_delivery_collection_is_replayable(self) -> None:
        environment, _ = run_delivery_slice()
        environment.collect_delivery("delivery-1", "resident-1", NOW)

        rebuilt = environment.from_history(notification_fatigue_environment(), environment.events)

        self.assertEqual(rebuilt.deliveries["delivery-1"].status, "collected")
        self.assertEqual(rebuilt.deliveries["delivery-1"].collected_at, NOW)

    def test_delivery_requires_description(self) -> None:
        environment, _ = run_delivery_slice()

        with self.assertRaises(ValueError):
            environment.record_delivery(
                "empty-description",
                "unit-101",
                " ",
                NOW,
                recorded_by="manager-1",
            )

        self.assertNotIn("empty-description", environment.deliveries)

    def test_unknown_delivery_reference_is_rejected_as_domain_error(self) -> None:
        environment, _ = run_delivery_slice()

        with self.assertRaises(ValueError):
            environment.collect_delivery("missing-delivery", "resident-1", NOW)


if __name__ == "__main__":
    unittest.main()
