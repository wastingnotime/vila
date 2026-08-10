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

    def test_onboarding_acceptance_is_replayable(self) -> None:
        environment = notification_fatigue_environment()
        accepted_at = START + timedelta(days=1)
        environment.invite_resident(
            "invite-replay",
            "new-resident",
            "unit-102",
            START,
            START + timedelta(days=7),
            invited_by="manager-1",
        )
        environment.accept_invitation("invite-replay", "new-resident", accepted_at)

        replayed = environment.from_history(notification_fatigue_environment(), environment.events)

        self.assertEqual(replayed.unit_for_resident("new-resident", accepted_at), "unit-102")
        self.assertEqual(replayed.invitations["invite-replay"].status, "accepted")
        self.assertEqual(replayed.membership_history[-1].active_from, accepted_at)

    def test_resident_cannot_have_two_active_onboarding_paths(self) -> None:
        environment = notification_fatigue_environment()
        environment.invite_resident(
            "invite-pending",
            "new-resident",
            "unit-102",
            START,
            START + timedelta(days=7),
            invited_by="manager-1",
        )

        with self.assertRaises(ValueError):
            environment.invite_resident(
                "invite-second",
                "new-resident",
                "unit-103",
                START,
                START + timedelta(days=7),
                invited_by="manager-1",
            )

        with self.assertRaises(ValueError):
            environment.invite_resident(
                "invite-existing",
                "resident-1",
                "unit-102",
                START,
                START + timedelta(days=7),
                invited_by="manager-1",
            )


if __name__ == "__main__":
    unittest.main()
