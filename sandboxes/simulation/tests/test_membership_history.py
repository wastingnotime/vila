import unittest
from datetime import datetime, timezone

from app.domain.model import notification_fatigue_environment
from app.simulation.membership_history import MOVE_AT, run_membership_history_slice


class MembershipHistoryTests(unittest.TestCase):
    def test_move_changes_current_status_without_erasing_history(self) -> None:
        environment, status = run_membership_history_slice()

        self.assertEqual(status, ["overdue_payment"])
        self.assertEqual(
            environment.unit_for_resident("resident-1", MOVE_AT.replace(day=9, hour=23, minute=59)),
            "unit-101",
        )
        self.assertEqual(environment.unit_for_resident("resident-1", MOVE_AT), "unit-102")
        self.assertEqual(len(environment.membership_history), 5)

    def test_previous_unit_activity_remains_auditable(self) -> None:
        environment = notification_fatigue_environment()
        opened_at = datetime(2026, 1, 6, tzinfo=timezone.utc)
        environment.open_request(
            opened_at,
            request_id="request-1",
            resident_id="resident-1",
            category="plumbing",
            description="Low water pressure",
        )
        environment.move_resident("resident-1", "unit-102", MOVE_AT)

        self.assertEqual(environment.requests["request-1"].unit_id, "unit-101")
        with self.assertRaises(KeyError):
            environment.unit_for_resident("resident-1", datetime(2025, 12, 31, tzinfo=timezone.utc))

    def test_departure_removes_current_access_but_retains_membership_history(self) -> None:
        environment = notification_fatigue_environment()
        environment.leave_resident("resident-1", MOVE_AT)

        with self.assertRaises(KeyError):
            environment.unit_for_resident("resident-1", MOVE_AT)
        self.assertNotIn("resident-1", environment.residents)
        self.assertEqual(environment.membership_history[0].active_until, MOVE_AT)

    def test_membership_lifecycle_is_replayable(self) -> None:
        environment = notification_fatigue_environment()
        leave_at = datetime(2026, 2, 10, tzinfo=timezone.utc)
        rejoin_at = datetime(2026, 2, 12, tzinfo=timezone.utc)

        environment.move_resident("resident-1", "unit-102", MOVE_AT)
        environment.leave_resident("resident-1", leave_at)
        environment.rejoin_resident("resident-1", "unit-103", rejoin_at)

        replayed = environment.from_history(notification_fatigue_environment(), environment.events)

        self.assertEqual(
            [event.name for event in environment.events],
            ["resident_moved", "resident_departed", "resident_rejoined"],
        )
        self.assertEqual(replayed.unit_for_resident("resident-1", rejoin_at), "unit-103")
        self.assertEqual(replayed.membership_history, environment.membership_history)

    def test_move_to_current_unit_is_rejected_without_an_event(self) -> None:
        environment = notification_fatigue_environment()

        with self.assertRaises(ValueError):
            environment.move_resident("resident-1", "unit-101", MOVE_AT)

        self.assertEqual(environment.events, [])
        self.assertEqual(len(environment.membership_history), 4)

    def test_move_to_unknown_unit_is_rejected_as_domain_error(self) -> None:
        environment = notification_fatigue_environment()

        with self.assertRaises(ValueError):
            environment.move_resident("resident-1", "unit-999", MOVE_AT)

        self.assertEqual(environment.events, [])

    def test_rejoin_to_unknown_unit_is_rejected_as_domain_error(self) -> None:
        environment = notification_fatigue_environment()
        environment.leave_resident("resident-1", datetime(2026, 2, 10, tzinfo=timezone.utc))

        with self.assertRaises(ValueError):
            environment.rejoin_resident(
                "resident-1", "unit-999", datetime(2026, 2, 12, tzinfo=timezone.utc)
            )

        self.assertNotIn("resident_rejoined", [event.name for event in environment.events])


if __name__ == "__main__":
    unittest.main()
