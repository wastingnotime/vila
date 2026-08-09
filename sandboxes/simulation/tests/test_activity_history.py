import unittest

from app.simulation.activity_history import run_activity_history_slice


class ActivityHistoryTests(unittest.TestCase):
    def test_resident_sees_relevant_human_readable_activity(self) -> None:
        _, resident, _ = run_activity_history_slice()

        self.assertEqual(
            resident,
            [
                "Payment is overdue",
                "Maintenance request submitted",
                "Maintenance request under review",
            ],
        )

    def test_manager_sees_condominium_activity(self) -> None:
        _, _, manager = run_activity_history_slice()

        self.assertEqual(len(manager), 5)
        self.assertNotIn("maintenance_opened", manager)
        self.assertIn("Maintenance request under review", manager)


if __name__ == "__main__":
    unittest.main()
