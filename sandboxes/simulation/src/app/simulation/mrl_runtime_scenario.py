from datetime import datetime, timezone

from mrl_simulation_runtime.actors import Actor
from mrl_simulation_runtime.invariants import Invariant
from mrl_simulation_runtime.scenario import InitialScheduledAction, Scenario

from app.domain.model import Environment, notification_fatigue_environment


START = datetime(2026, 1, 1, tzinfo=timezone.utc)
ADVANCE = datetime(2026, 1, 6, tzinfo=timezone.utc)
MANAGER_REVIEW = datetime(2026, 1, 7, tzinfo=timezone.utc)
QUEUE_REVIEW = datetime(2026, 2, 8, tzinfo=timezone.utc)
SUMMARY_AT = datetime(2026, 1, 6, 1, 0, tzinfo=timezone.utc)


def _run_slice(context: object) -> None:
    environment: Environment = context.environment  # type: ignore[attr-defined]
    context.emit("intention", "review_status", actor="resident-1", payload={"scope": "home"})
    environment.overdue_payments(ADVANCE)
    context.emit("domain_event", "payment_became_overdue", source="PaymentProjection", actor="system")
    environment.open_request(
        ADVANCE,
        request_id="request-1",
        resident_id="resident-1",
        category="plumbing",
        description="Water pressure is low in the kitchen.",
    )
    context.emit("domain_event", "maintenance_request_opened", source="MaintenanceAggregate", actor="resident-1")
    context.emit(
        "projection",
        "resident_status_ready",
        source="StatusProjection",
        actor="resident-1",
        payload={"items": environment.resident_status("resident-1", ADVANCE)},
    )
    context.emit(
        "projection",
        "manager_status_ready",
        source="StatusProjection",
        actor="manager-1",
        payload={"items": environment.manager_status(ADVANCE)},
    )


def _emit_composed_status_summary(context: object) -> None:
    environment: Environment = context.environment  # type: ignore[attr-defined]
    environment.record_delivery("delivery-1", "unit-101", "Small package", SUMMARY_AT)
    environment.publish_announcement(
        "announcement-1",
        "Water maintenance",
        "Water will be unavailable Thursday.",
        "normal",
        SUMMARY_AT,
    )
    for viewer_id in ("resident-1", "manager-1"):
        summary = environment.status_summary(viewer_id, SUMMARY_AT)
        context.emit(
            "projection",
            "status_summary_ready",
            source="StatusSummaryProjection",
            actor=viewer_id,
            payload={
                "role": environment.roles[viewer_id],
                "action_items": list(summary.action_items),
                "latest_update": summary.latest_update,
                "open_delivery_ids": list(summary.open_delivery_ids),
            },
        )
        context.emit(
            "projection",
            "activity_history_ready",
            source="ActivityHistoryProjection",
            actor=viewer_id,
            payload={
                "entries": [
                    {
                        "kind": activity.kind,
                        "summary": activity.summary,
                        "subject_id": activity.subject_id,
                        "at": activity.at.isoformat(),
                    }
                    for activity in environment.activity_history(viewer_id, SUMMARY_AT)
                ]
            },
        )
    notifications = environment.actionable_notifications("manager-1", SUMMARY_AT)
    context.emit(
        "projection",
        "notification_policy_ready",
        source="NotificationPolicy",
        actor="manager-1",
        payload={
            "notifications": [
                {"kind": notification.kind, "item_count": notification.item_count}
                for notification in notifications
            ]
        },
    )


def _manager_reviews_request(context: object) -> None:
    environment: Environment = context.environment  # type: ignore[attr-defined]
    context.emit("intention", "review_maintenance_request", actor="manager-1", payload={"request_id": "request-1"})
    context.emit(
        "command",
        "change_maintenance_status",
        source="MaintenanceUseCase",
        actor="manager-1",
        correlation_id="request-1",
        payload={"to": "under_review"},
    )


def _resident_collects_delivery(context: object) -> None:
    environment: Environment = context.environment  # type: ignore[attr-defined]
    context.emit(
        "intention",
        "collect_delivery",
        source="ResidentActor",
        actor="resident-1",
        correlation_id="delivery-1",
        payload={"delivery_id": "delivery-1"},
    )
    environment.collect_delivery("delivery-1", "resident-1", MANAGER_REVIEW)
    context.emit(
        "domain_event",
        "delivery_collected",
        source="DeliveryAggregate",
        actor="resident-1",
        correlation_id="delivery-1",
        payload={"delivery_id": "delivery-1"},
    )
    context.emit(
        "projection",
        "open_deliveries_ready",
        source="DeliveryProjection",
        actor="resident-1",
        payload={"delivery_ids": [delivery.delivery_id for delivery in environment.open_deliveries("resident-1", MANAGER_REVIEW)]},
    )
    environment.change_request_status(
        MANAGER_REVIEW,
        request_id="request-1",
        manager_id="manager-1",
        next_status="under_review",
    )
    context.emit(
        "domain_event",
        "maintenance_status_changed",
        source="MaintenanceAggregate",
        actor="manager-1",
        correlation_id="request-1",
        payload={"to": "under_review"},
    )
    notifications = environment.maintenance_status_notifications("request-1", MANAGER_REVIEW)
    context.emit(
        "projection",
        "resident_maintenance_notifications_ready",
        source="NotificationPolicy",
        actor="manager-1",
        payload={
            "recipients": [notification.recipient_id for notification in notifications],
            "item_count": sum(notification.item_count for notification in notifications),
            "notifications": [
                {
                    "recipient_id": notification.recipient_id,
                    "kind": notification.kind,
                    "item_count": notification.item_count,
                }
                for notification in notifications
            ],
        },
    )


def _run_queue_observation(context: object) -> None:
    environment: Environment = context.environment  # type: ignore[attr-defined]
    arrival = datetime(2026, 2, 6, tzinfo=timezone.utc)
    for suffix in ("a", "b"):
        request_id = f"queue-{suffix}"
        context.emit(
            "intention",
            "report_maintenance_issue",
            source="ResidentActor",
            actor="resident-1",
            correlation_id=request_id,
            payload={"request_id": request_id},
        )
        environment.open_request(
            arrival,
            request_id=request_id,
            resident_id="resident-1",
            category="plumbing",
            description=f"Recurring issue {suffix}",
        )
        context.emit(
            "domain_event",
            "maintenance_request_opened",
            source="MaintenanceAggregate",
            actor="resident-1",
            correlation_id=request_id,
            payload={"request_id": request_id},
        )
    context.emit(
        "command",
        "change_maintenance_status",
        source="MaintenanceUseCase",
        actor="manager-1",
        correlation_id="queue-a",
        payload={"to": "under_review"},
    )
    environment.change_request_status(
        QUEUE_REVIEW,
        request_id="queue-a",
        manager_id="manager-1",
        next_status="under_review",
    )
    context.emit(
        "domain_event",
        "maintenance_status_changed",
        source="MaintenanceAggregate",
        actor="manager-1",
        correlation_id="queue-a",
        payload={"to": "under_review"},
    )
    attention_queue = sum(
        request.status in {"submitted", "under_review"}
        for request in environment.requests.values()
    )
    context.emit(
        "projection",
        "manager_attention_queue_ready",
        source="MaintenanceProjection",
        actor="manager-1",
        payload={"count": attention_queue},
    )


def _status_has_actionable_items(context: object) -> bool:
    environment: Environment = context.environment  # type: ignore[attr-defined]
    return environment.resident_status("resident-1", ADVANCE) == ["overdue_payment", "maintenance_request"]


def _summary_scope_is_temporal_and_tenant_scoped(context: object) -> bool:
    environment: Environment = context.environment  # type: ignore[attr-defined]
    resident = environment.status_summary("resident-1", SUMMARY_AT)
    manager = environment.status_summary("manager-1", SUMMARY_AT)
    return (
        resident.action_items.count("overdue_payment") == 1
        and resident.action_items.count("maintenance_request") == 1
        and manager.action_items.count("overdue_payment") == 3
        and manager.action_items.count("maintenance_request") == 1
    )


def create_simulation() -> Scenario:
    environment = notification_fatigue_environment()

    def attach_environment(context: object) -> None:
        context.environment = environment  # type: ignore[attr-defined]

    class ResidentActor:
        def on_start(self, context: object) -> None:
            attach_environment(context)

    return Scenario(
        name="condominium-status-and-obligations",
        seed=7,
        initial_time=START,
        run_id="status-slice-2026-01-01",
        actors=[Actor(name="resident-1", behavior=ResidentActor())],
        scheduled_actions=[
            InitialScheduledAction(
                when=SUMMARY_AT,
                action=_emit_composed_status_summary,
                name="emit_composed_status_summary",
                source="VilaSimulation",
                correlation_id="summary-slice-1",
            ),
            InitialScheduledAction(
                when=ADVANCE,
                action=_run_slice,
                name="run_status_and_obligations_slice",
                source="VilaSimulation",
                correlation_id="slice-1",
            ),
            InitialScheduledAction(
                when=MANAGER_REVIEW,
                action=_manager_reviews_request,
                name="manager_reviews_maintenance_request",
                source="VilaSimulation",
                correlation_id="request-1",
            ),
            InitialScheduledAction(
                when=MANAGER_REVIEW,
                action=_resident_collects_delivery,
                name="resident_collects_delivery",
                source="VilaSimulation",
                correlation_id="delivery-1",
            ),
            InitialScheduledAction(
                when=QUEUE_REVIEW,
                action=_run_queue_observation,
                name="observe_manager_attention_queue",
                source="VilaSimulation",
                correlation_id="queue-slice-1",
            ),
        ],
        invariants=[
            Invariant(name="status_has_actionable_items", check=_status_has_actionable_items),
            Invariant(name="summary_scope_is_temporal_and_tenant_scoped", check=_summary_scope_is_temporal_and_tenant_scoped),
        ],
    )
