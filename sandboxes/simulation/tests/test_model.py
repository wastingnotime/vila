import unittest
from datetime import datetime, timezone

from app.domain.model import notification_fatigue_environment, seeded_environment


class SimulationModelTests(unittest.TestCase):
    def test_overdue_and_maintenance_are_visible_in_resident_status(self) -> None:
        environment = seeded_environment()
        now = datetime(2026, 1, 6, tzinfo=timezone.utc)

        environment.open_request(
            now,
            request_id="request-1",
            resident_id="resident-1",
            category="plumbing",
            description="Low water pressure",
        )

        self.assertEqual(
            environment.resident_status("resident-1", now),
            ["overdue_payment", "maintenance_request"],
        )
        self.assertEqual(environment.manager_status(now), ["overdue_payment", "maintenance_request"])

    def test_resolved_request_cannot_silently_reopen(self) -> None:
        environment = seeded_environment()
        now = datetime(2026, 1, 6, tzinfo=timezone.utc)
        environment.open_request(
            now,
            request_id="request-1",
            resident_id="resident-1",
            category="plumbing",
            description="Low water pressure",
        )
        for next_status in ("under_review", "planned", "in_progress", "resolved"):
            environment.change_request_status(
                now,
                request_id="request-1",
                manager_id="manager-1",
                next_status=next_status,
            )

        with self.assertRaises(ValueError):
            environment.change_request_status(
                now,
                request_id="request-1",
                manager_id="manager-1",
                next_status="in_progress",
            )
        self.assertEqual(len(environment.events), 5)
        self.assertEqual(environment.events[-1].payload["changed_by"], "manager-1")

    def test_duplicate_request_id_cannot_replace_existing_request(self) -> None:
        environment = seeded_environment()
        now = datetime(2026, 1, 6, tzinfo=timezone.utc)
        environment.open_request(
            now,
            request_id="request-1",
            resident_id="resident-1",
            category="plumbing",
            description="Original request",
        )

        with self.assertRaises(ValueError):
            environment.open_request(
                now,
                request_id="request-1",
                resident_id="resident-1",
                category="electrical",
                description="Replacement request",
            )

        self.assertEqual(environment.requests["request-1"].description, "Original request")
        self.assertEqual(len(environment.events), 1)

    def test_event_history_rebuilds_the_same_projection(self) -> None:
        environment = seeded_environment()
        now = datetime(2026, 1, 6, tzinfo=timezone.utc)
        environment.open_request(
            now,
            request_id="request-1",
            resident_id="resident-1",
            category="plumbing",
            description="Low water pressure",
        )
        original_status = environment.resident_status("resident-1", now)
        rebuilt = environment.from_history(seeded_environment(), environment.events)

        self.assertEqual(rebuilt.resident_status("resident-1", now), original_status)
        self.assertEqual(rebuilt.events, environment.events)

    def test_historical_summary_sees_payment_until_its_payment_timestamp(self) -> None:
        environment = seeded_environment()
        due = datetime(2026, 1, 6, tzinfo=timezone.utc)
        paid = datetime(2026, 1, 8, tzinfo=timezone.utc)
        environment.overdue_payments(due)
        environment.mark_payment_paid(0, paid)

        self.assertEqual(environment.manager_status(due), ["overdue_payment"])
        self.assertEqual(environment.manager_status(paid), [])

    def test_payment_confirmation_is_auditable_and_replayable(self) -> None:
        environment = seeded_environment()
        now = datetime(2026, 1, 8, tzinfo=timezone.utc)
        environment.mark_payment_paid(0, now, confirmed_by="manager-1")

        rebuilt = environment.from_history(seeded_environment(), environment.events)
        self.assertEqual(environment.events[-1].name, "payment_paid")
        self.assertEqual(rebuilt.payments[0].status, "paid")
        self.assertEqual(
            [item.summary for item in environment.activity_history("resident-1", now)],
            ["Payment marked paid"],
        )

        event_count = len(environment.events)
        with self.assertRaises(ValueError):
            environment.mark_payment_paid(0, now, confirmed_by="manager-1")
        self.assertEqual(len(environment.events), event_count)

    def test_any_building_manager_can_read_manager_scoped_projections(self) -> None:
        environment = notification_fatigue_environment()
        environment.roles["manager-2"] = "building_manager"
        now = datetime(2026, 1, 6, tzinfo=timezone.utc)
        environment.record_delivery("delivery-1", "unit-101", "Package", now, recorded_by="manager-1")

        summary = environment.status_summary("manager-2", now)
        history = environment.activity_history("manager-2", now)

        self.assertEqual(summary.open_delivery_ids, ("delivery-1",))
        self.assertEqual(summary.action_items.count("overdue_payment"), 3)
        self.assertEqual(len(history), 3)


if __name__ == "__main__":
    unittest.main()
