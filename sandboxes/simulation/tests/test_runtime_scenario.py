import unittest

from app.simulation.mrl_runtime_scenario import create_simulation
from mrl_simulation_runtime.runner import SimulationRunner


class RuntimeScenarioTests(unittest.TestCase):
    def test_runtime_adapter_exposes_a_shared_domain_observatory_graph(self) -> None:
        scenario = create_simulation()
        nodes = {node.id: node for node in scenario.observatory_nodes}
        edges = {(edge.from_node, edge.to_node) for edge in scenario.observatory_edges}

        self.assertEqual(
            set(nodes),
            {
                "resident-actor",
                "manager-actor",
                "status-summary",
                "maintenance-queue",
                "delivery-flow",
                "payment-flow",
                "announcement-flow",
                "onboarding-flow",
                "resident-notifications",
                "activity-history",
            },
        )
        self.assertIn(("resident-actor", "status-summary"), edges)
        self.assertIn(("manager-actor", "maintenance-queue"), edges)
        self.assertIn(("maintenance-queue", "resident-notifications"), edges)
        self.assertIn(("payment-flow", "activity-history"), edges)
        self.assertIn(("delivery-flow", "status-summary"), edges)
        self.assertIn(("manager-actor", "onboarding-flow"), edges)
        self.assertEqual(nodes["status-summary"].layer, "projections")
        self.assertEqual(nodes["resident-notifications"].kind, "notification")
        self.assertEqual(nodes["resident-notifications"].layer, "events")
        self.assertNotEqual(nodes["resident-notifications"].layer, nodes["status-summary"].layer)
        self.assertIsNone(nodes["resident-actor"].realm)
        self.assertIsNone(nodes["status-summary"].domain)
        self.assertEqual(
            {node.domain for node in nodes.values() if node.domain},
            {"maintenance", "delivery", "payment", "announcement", "onboarding"},
        )
        self.assertTrue(all(edge.from_node in nodes and edge.to_node in nodes for edge in scenario.observatory_edges))
        self.assertTrue(
            {node.layer for node in nodes.values()} <=
            {"actors", "use_cases", "events", "projections", "outbound_adapters"}
        )

    def test_runtime_adapter_emits_onboarding_access_evidence(self) -> None:
        result = SimulationRunner().run(create_simulation())
        ready = [
            observation
            for observation in result.observations.observations
            if observation.name == "resident_onboarding_ready"
        ]

        self.assertEqual(len(ready), 1)
        self.assertEqual(ready[0].actor, "resident-new")
        self.assertEqual(ready[0].payload, {"unit_id": "unit-103", "current_access": True})

    def test_runtime_adapter_emits_onboarding_rejection_evidence(self) -> None:
        result = SimulationRunner().run(create_simulation())
        rejected = [
            observation
            for observation in result.observations.observations
            if observation.name == "resident_onboarding_rejected"
        ]

        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0].actor, "resident-declined")
        self.assertEqual(
            rejected[0].payload,
            {"invitation_id": "invite-declined", "status": "rejected", "current_access": False},
        )

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
            [{"kind": "maintenance_review_required", "item_count": 1, "item_ids": ["request-1"]}],
        )

    def test_runtime_adapter_traces_manager_status_inputs(self) -> None:
        result = SimulationRunner().run(create_simulation())
        names = [observation.name for observation in result.observations.observations]

        self.assertEqual(names.count("record_delivery"), 1)
        self.assertEqual(names.count("delivery_received"), 1)
        self.assertEqual(names.count("publish_announcement"), 1)
        self.assertEqual(names.count("announcement_published"), 1)
        self.assertLess(names.index("delivery_received"), names.index("status_summary_ready"))
        self.assertLess(names.index("announcement_published"), names.index("status_summary_ready"))
        events = {
            observation.name: observation
            for observation in result.observations.observations
            if observation.name in {"delivery_received", "announcement_published"}
        }
        self.assertEqual(events["delivery_received"].correlation_id, "delivery-1")
        self.assertEqual(events["delivery_received"].payload["delivery_id"], "delivery-1")
        self.assertEqual(events["delivery_received"].payload["recorded_by"], "manager-1")
        self.assertEqual(events["announcement_published"].correlation_id, "announcement-1")
        self.assertEqual(events["announcement_published"].payload["announcement_id"], "announcement-1")
        self.assertEqual(events["announcement_published"].payload["published_by"], "manager-1")

    def test_runtime_adapter_emits_explicit_empty_state(self) -> None:
        result = SimulationRunner().run(create_simulation())
        empty = [
            observation
            for observation in result.observations.observations
            if observation.name == "empty_status_summary_ready"
        ]

        self.assertEqual(len(empty), 1)
        self.assertEqual(empty[0].correlation_id, "empty-summary-1")
        self.assertEqual(empty[0].payload, {"action_items": [], "latest_update": None, "open_delivery_ids": []})

        invariant_results = [
            observation.payload["passed"]
            for observation in result.observations.observations
            if observation.type == "invariant_result"
        ]
        self.assertTrue(invariant_results)
        self.assertTrue(all(invariant_results))

    def test_runtime_adapter_emits_expired_announcement_state(self) -> None:
        result = SimulationRunner().run(create_simulation())
        closed = [
            observation
            for observation in result.observations.observations
            if observation.name == "announcement_window_closed"
        ]

        self.assertEqual(len(closed), 1)
        self.assertEqual(closed[0].correlation_id, "announcement-1")
        self.assertEqual(closed[0].payload, {"active_ids": [], "retained_ids": ["announcement-1"]})

    def test_runtime_adapter_emits_resident_movement_scope(self) -> None:
        result = SimulationRunner().run(create_simulation())
        moved = [
            observation
            for observation in result.observations.observations
            if observation.name == "resident_status_after_move_ready"
        ]

        self.assertEqual(len(moved), 1)
        self.assertEqual(moved[0].correlation_id, "resident-1-move")
        self.assertEqual(moved[0].payload["action_items"], ["overdue_payment"])
        self.assertEqual(moved[0].payload["historical_request_ids"], ["request-1"])

    def test_runtime_adapter_emits_departure_history(self) -> None:
        result = SimulationRunner().run(create_simulation())
        departure = [
            observation
            for observation in result.observations.observations
            if observation.name == "resident_departure_history_ready"
        ]

        self.assertEqual(len(departure), 1)
        self.assertEqual(departure[0].correlation_id, "resident-1-departure")
        self.assertFalse(departure[0].payload["current_access"])
        self.assertIn("request-1", departure[0].payload["history_subject_ids"])
        names = [observation.name for observation in result.observations.observations]
        self.assertLess(names.index("resident_membership_closed"), names.index("resident_departure_history_ready"))

    def test_runtime_adapter_emits_resident_rejoin_scope(self) -> None:
        result = SimulationRunner().run(create_simulation())
        rejoined = [
            observation
            for observation in result.observations.observations
            if observation.name == "resident_status_after_rejoin_ready"
        ]

        self.assertEqual(len(rejoined), 1)
        self.assertEqual(rejoined[0].payload["unit_id"], "unit-103")
        self.assertEqual(rejoined[0].payload["action_items"], ["overdue_payment"])
        self.assertEqual(
            rejoined[0].payload["historical_unit_ids"],
            ["unit-101", "unit-102", "unit-103"],
        )

    def test_runtime_adapter_correlates_membership_lifecycle_events(self) -> None:
        result = SimulationRunner().run(create_simulation())
        events = {
            observation.name: observation
            for observation in result.observations.observations
            if observation.name in {
                "resident_membership_changed",
                "resident_membership_closed",
                "resident_membership_started",
            }
        }

        self.assertEqual(events["resident_membership_changed"].payload, {
            "resident_id": "resident-1",
            "from_unit_id": "unit-101",
            "to_unit_id": "unit-102",
        })
        self.assertEqual(events["resident_membership_closed"].payload, {"resident_id": "resident-1"})
        self.assertEqual(events["resident_membership_started"].payload, {
            "resident_id": "resident-1",
            "unit_id": "unit-103",
        })
        self.assertLess(
            [observation.name for observation in result.observations.observations].index("resident_membership_closed"),
            [observation.name for observation in result.observations.observations].index("resident_status_after_rejoin_ready"),
        )

    def test_runtime_adapter_emits_shared_unit_status_notifications(self) -> None:
        result = SimulationRunner().run(create_simulation())

        notifications = [
            observation
            for observation in result.observations.observations
            if observation.name == "resident_maintenance_notifications_ready"
        ]
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].payload["recipients"], ["resident-1", "resident-1b"])
        self.assertEqual(notifications[0].payload["item_count"], 2)
        self.assertEqual(
            notifications[0].payload["notifications"],
            [
                {"recipient_id": "resident-1", "kind": "maintenance_status_under_review", "item_count": 1},
                {"recipient_id": "resident-1b", "kind": "maintenance_status_under_review", "item_count": 1},
            ],
        )

    def test_runtime_adapter_emits_delivery_collection(self) -> None:
        result = SimulationRunner().run(create_simulation())

        collected = [
            observation
            for observation in result.observations.observations
            if observation.name == "open_deliveries_ready"
        ]
        self.assertEqual(len(collected), 1)
        self.assertEqual(collected[0].payload["delivery_ids"], [])
        self.assertEqual(collected[0].payload["collected"]["delivery_id"], "delivery-1")
        self.assertEqual(collected[0].payload["collected"]["status"], "collected")
        self.assertEqual(collected[0].payload["collected"]["collected_at"], "2026-01-07T00:00:00+00:00")
        self.assertTrue(collected[0].payload["collection_event_recorded"])
        self.assertEqual(collected[0].payload["collected_by"], "resident-1")

    def test_runtime_adapter_emits_manual_payment_confirmation(self) -> None:
        result = SimulationRunner().run(create_simulation())

        confirmations = [
            observation
            for observation in result.observations.observations
            if observation.name == "manager_payment_status_ready"
        ]
        self.assertEqual(len(confirmations), 1)
        self.assertEqual(confirmations[0].payload["overdue_count"], 2)
        self.assertEqual(confirmations[0].payload["payment_index"], 0)
        self.assertEqual(confirmations[0].payload["status"], "paid")
        self.assertEqual(confirmations[0].payload["paid_at"], "2026-01-08T00:00:00+00:00")
        self.assertEqual(confirmations[0].payload["confirmed_by"], "manager-1")
        payment_events = [
            observation
            for observation in result.observations.observations
            if observation.name == "payment_marked_paid"
        ]
        self.assertEqual(payment_events[0].payload["confirmed_by"], "manager-1")

    def test_runtime_adapter_emits_paid_activity_after_confirmation(self) -> None:
        result = SimulationRunner().run(create_simulation())

        activity = [
            observation
            for observation in result.observations.observations
            if observation.name == "paid_activity_ready"
        ]
        self.assertEqual(len(activity), 1)
        self.assertEqual(
            activity[0].payload["entries"],
            [
                {
                    "summary": "Payment is overdue",
                    "subject_id": "unit-101",
                    "at": "2026-01-05T00:00:00+00:00",
                },
                {
                    "summary": "Maintenance request submitted",
                    "subject_id": "request-1",
                    "at": "2026-01-06T00:00:00+00:00",
                },
                {
                    "summary": "Maintenance request under review",
                    "subject_id": "request-1",
                    "at": "2026-01-07T00:00:00+00:00",
                },
                {
                    "summary": "Payment marked paid",
                    "subject_id": "unit-101",
                    "at": "2026-01-08T00:00:00+00:00",
                },
            ],
        )

    def test_runtime_actions_remain_in_chronological_order(self) -> None:
        result = SimulationRunner().run(create_simulation())
        names = [observation.name for observation in result.observations.observations]

        self.assertLess(names.index("maintenance_status_changed"), names.index("resident_maintenance_notifications_ready"))
        self.assertLess(names.index("delivery_collected"), names.index("open_deliveries_ready"))
        self.assertLess(names.index("payment_marked_paid"), names.index("paid_activity_ready"))

    def test_runtime_adapter_emits_role_scoped_activity_history(self) -> None:
        result = SimulationRunner().run(create_simulation())

        histories = {
            observation.actor: observation.payload["entries"]
            for observation in result.observations.observations
            if observation.name == "activity_history_ready"
        }
        self.assertEqual(
            [entry["summary"] for entry in histories["resident-1"]],
            ["Payment is overdue", "Maintenance request submitted"],
        )
        self.assertEqual(
            sum(entry["summary"] == "Payment is overdue" for entry in histories["manager-1"]),
            3,
        )
        self.assertIn("Maintenance request submitted", [entry["summary"] for entry in histories["manager-1"]])
        self.assertEqual(histories["resident-1"][0]["kind"], "payment")
        self.assertEqual(histories["resident-1"][1]["subject_id"], "request-1")


if __name__ == "__main__":
    unittest.main()
