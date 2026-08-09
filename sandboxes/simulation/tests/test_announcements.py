import unittest
from datetime import datetime, timezone

from app.domain.model import Announcement
from app.simulation.announcements import NOW, run_announcement_slice


class AnnouncementTests(unittest.TestCase):
    def test_active_announcements_prioritize_important_updates(self) -> None:
        _, titles = run_announcement_slice()

        self.assertEqual(titles, ["Emergency elevator outage", "Water maintenance"])

    def test_expired_announcement_is_not_active_but_remains_stored(self) -> None:
        environment, _ = run_announcement_slice()
        later = datetime(2026, 1, 8, tzinfo=timezone.utc)

        self.assertEqual([item.title for item in environment.active_announcements(later)], ["Water maintenance"])
        self.assertEqual(len(environment.announcements), 2)

    def test_announcement_window_is_timezone_aware_and_end_is_exclusive(self) -> None:
        environment, _ = run_announcement_slice()

        self.assertEqual(len(environment.active_announcements(NOW.replace(day=7))), 1)

    def test_other_condominium_announcement_is_not_visible(self) -> None:
        environment, _ = run_announcement_slice()
        environment.announcements.append(
            Announcement(
                condominium_id="other-condo",
                announcement_id="other-1",
                title="Other building",
                body="Not visible here",
                priority="high",
                published_at=NOW,
            )
        )

        self.assertNotIn("Other building", [item.title for item in environment.active_announcements(NOW)])


if __name__ == "__main__":
    unittest.main()
