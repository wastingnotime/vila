import unittest

from app.simulation.mrl_runtime_scenario import create_simulation
from mrl_simulation_runtime.runner import SimulationRunner


class RuntimeScenarioTests(unittest.TestCase):
    def test_runtime_adapter_emits_queue_projection_from_shared_environment(self) -> None:
        result = SimulationRunner().run(create_simulation())

        queue_observations = [
            observation
            for observation in result.observations.observations
            if observation.name == "manager_attention_queue_ready"
        ]
        self.assertEqual(len(queue_observations), 1)
        self.assertEqual(queue_observations[0].payload["count"], 3)
        names = [observation.name for observation in result.observations.observations]
        self.assertEqual(names.count("report_maintenance_issue"), 2)
        self.assertEqual(names.count("maintenance_request_opened"), 3)
        self.assertEqual(names.count("change_maintenance_status"), 2)


if __name__ == "__main__":
    unittest.main()
