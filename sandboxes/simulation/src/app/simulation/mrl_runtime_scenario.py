from datetime import datetime, timezone

from mrl_simulation_runtime.actors import Actor
from mrl_simulation_runtime.invariants import Invariant
from mrl_simulation_runtime.scenario import InitialScheduledAction, Scenario

from app.domain.model import Environment, seeded_environment


START = datetime(2026, 1, 1, tzinfo=timezone.utc)
ADVANCE = datetime(2026, 1, 6, tzinfo=timezone.utc)
MANAGER_REVIEW = datetime(2026, 1, 7, tzinfo=timezone.utc)
QUEUE_REVIEW = datetime(2026, 2, 8, tzinfo=timezone.utc)


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


def create_simulation() -> Scenario:
    environment = seeded_environment()

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
                when=QUEUE_REVIEW,
                action=_run_queue_observation,
                name="observe_manager_attention_queue",
                source="VilaSimulation",
                correlation_id="queue-slice-1",
            ),
        ],
        invariants=[Invariant(name="status_has_actionable_items", check=_status_has_actionable_items)],
    )
