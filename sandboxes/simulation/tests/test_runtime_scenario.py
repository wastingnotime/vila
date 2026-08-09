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

    def test_runtime_adapter_emits_composed_status_for_both_roles(self) -> None:
        result = SimulationRunner().run(create_simulation())

        summaries = [
            observation
            for observation in result.observations.observations
            if observation.name == "status_summary_ready"
        ]
        self.assertEqual([observation.actor for observation in summaries], ["resident-1", "manager-1"])
        self.assertEqual([observation.payload["role"] for observation in summaries], ["resident", "building_manager"])
        self.assertEqual(summaries[0].payload["action_items"].count("overdue_payment"), 1)
        self.assertEqual(summaries[1].payload["action_items"].count("overdue_payment"), 3)
        self.assertEqual(summaries[0].payload["latest_update"], "Water maintenance")
        self.assertEqual(summaries[0].payload["open_delivery_ids"], ["delivery-1"])

        invariant_results = {
            observation.name: observation.payload["passed"]
            for observation in result.observations.observations
            if observation.type == "invariant_result"
        }
        self.assertTrue(invariant_results["summary_scope_is_temporal_and_tenant_scoped"])

    def test_runtime_adapter_emits_actionable_notification_policy(self) -> None:
        result = SimulationRunner().run(create_simulation())

        notifications = [
            observation
            for observation in result.observations.observations
            if observation.name == "notification_policy_ready"
        ]
        self.assertEqual(len(notifications), 1)
        self.assertEqual(
            notifications[0].payload["notifications"],
            [{"kind": "maintenance_review_required", "item_count": 1}],
        )


if __name__ == "__main__":
    unittest.main()
