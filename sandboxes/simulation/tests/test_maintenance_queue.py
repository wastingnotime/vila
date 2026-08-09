import unittest

from app.simulation.maintenance_queue import run_maintenance_queue


class MaintenanceQueueTests(unittest.TestCase):
    def test_queue_grows_when_arrivals_outpace_manager_response(self) -> None:
        environment, queue_sizes = run_maintenance_queue()

        self.assertEqual(queue_sizes, [1, 2, 3])
        self.assertEqual(sum(request.status == "under_review" for request in environment.requests.values()), 3)

    def test_queue_simulation_horizon_is_bounded(self) -> None:
        with self.assertRaises(ValueError):
            run_maintenance_queue(months=0)
        with self.assertRaises(ValueError):
            run_maintenance_queue(months=13)


if __name__ == "__main__":
    unittest.main()
