import unittest
from datetime import datetime, timedelta, timezone

from app.domain.model import notification_fatigue_environment


START = datetime(2026, 1, 1, tzinfo=timezone.utc)


class OnboardingTests(unittest.TestCase):
    def test_manager_can_invite_and_resident_can_accept_membership(self) -> None:
        environment = notification_fatigue_environment()

        environment.invite_resident(
            "invite-1",
            "new-resident",
            "unit-102",
            START,
            START + timedelta(days=7),
            invited_by="manager-1",
        )
        environment.accept_invitation("invite-1", "new-resident", START + timedelta(days=1))

        self.assertEqual(environment.unit_for_resident("new-resident", START + timedelta(days=1)), "unit-102")
        self.assertIn("new-resident", environment.residents)
        self.assertEqual(environment.invitations["invite-1"].status, "accepted")
        self.assertEqual(
            [event.name for event in environment.events],
            ["invitation_created", "invitation_accepted"],
        )

    def test_rejected_invitation_does_not_grant_access(self) -> None:
        environment = notification_fatigue_environment()
        environment.invite_resident(
            "invite-rejected",
            "new-resident",
            "unit-102",
            START,
            START + timedelta(days=7),
            invited_by="manager-1",
        )

        environment.reject_invitation("invite-rejected", "new-resident", START + timedelta(days=1))

        self.assertNotIn("new-resident", environment.residents)
        self.assertEqual(environment.invitations["invite-rejected"].status, "rejected")

    def test_expired_invitation_cannot_be_accepted(self) -> None:
        environment = notification_fatigue_environment()
        environment.invite_resident(
            "invite-expired",
            "new-resident",
            "unit-102",
            START,
            START + timedelta(days=1),
            invited_by="manager-1",
        )

        with self.assertRaises(ValueError):
            environment.accept_invitation("invite-expired", "new-resident", START + timedelta(days=1))

        self.assertNotIn("new-resident", environment.residents)


if __name__ == "__main__":
    unittest.main()
