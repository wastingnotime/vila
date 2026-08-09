from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class Event:
    name: str
    at: datetime
    payload: dict[str, str]


@dataclass
class Payment:
    unit_id: str
    due_at: datetime
    status: str = "pending"


@dataclass
class MaintenanceRequest:
    request_id: str
    unit_id: str
    opened_by: str
    category: str
    description: str
    status: str = "submitted"


@dataclass(frozen=True)
class Notification:
    recipient_id: str
    kind: str
    item_count: int
    at: datetime


@dataclass
class Environment:
    condominium_id: str
    units: dict[str, str]
    memberships: dict[str, str]
    payments: list[Payment] = field(default_factory=list)
    requests: dict[str, MaintenanceRequest] = field(default_factory=dict)
    events: list[Event] = field(default_factory=list)
    notifications: list[Notification] = field(default_factory=list)

    def record(self, name: str, at: datetime, **payload: str) -> Event:
        event = Event(name=name, at=at.astimezone(timezone.utc), payload=payload)
        self.events.append(event)
        self._apply(event)
        return event

    @classmethod
    def from_history(cls, initial: "Environment", history: list[Event]) -> "Environment":
        replayed = cls(
            condominium_id=initial.condominium_id,
            units=dict(initial.units),
            memberships=dict(initial.memberships),
            payments=[Payment(unit_id=payment.unit_id, due_at=payment.due_at) for payment in initial.payments],
        )
        for event in history:
            replayed.events.append(event)
            replayed._apply(event)
        return replayed

    def _apply(self, event: Event) -> None:
        if event.name == "payment_overdue":
            self.payments[int(event.payload["payment_index"])].status = "overdue"
        elif event.name == "maintenance_opened":
            self.requests[event.payload["request_id"]] = MaintenanceRequest(
                request_id=event.payload["request_id"],
                unit_id=event.payload["unit_id"],
                opened_by=event.payload["opened_by"],
                category=event.payload["category"],
                description=event.payload["description"],
            )
        elif event.name == "maintenance_status_changed":
            request = self.requests[event.payload["request_id"]]
            request.status = event.payload["to"]

    def overdue_payments(self, now: datetime) -> list[Payment]:
        for index, payment in enumerate(self.payments):
            if payment.status == "pending" and now >= payment.due_at:
                self.record("payment_overdue", now, payment_index=str(index))
        return [payment for payment in self.payments if payment.status == "overdue"]

    def open_request(self, now: datetime, *, request_id: str, resident_id: str, category: str, description: str) -> Event:
        unit_id = self.memberships[resident_id]
        return self.record(
            "maintenance_opened",
            now,
            request_id=request_id,
            unit_id=unit_id,
            opened_by=resident_id,
            category=category,
            description=description,
        )

    def change_request_status(self, now: datetime, *, request_id: str, manager_id: str, next_status: str) -> Event:
        request = self.requests[request_id]
        allowed = {
            "submitted": {"under_review", "rejected"},
            "under_review": {"planned", "rejected"},
            "planned": {"in_progress", "rejected"},
            "in_progress": {"resolved"},
        }
        if next_status not in allowed.get(request.status, set()):
            raise ValueError(f"invalid maintenance transition: {request.status} -> {next_status}")
        return self.record(
            "maintenance_status_changed",
            now,
            request_id=request_id,
            from_status=request.status,
            to=next_status,
            changed_by=manager_id,
        )

    def resident_status(self, resident_id: str, now: datetime) -> list[str]:
        unit_id = self.memberships[resident_id]
        items = ["overdue_payment" for payment in self.overdue_payments(now) if payment.unit_id == unit_id]
        items.extend(
            "maintenance_request"
            for request in self.requests.values()
            if request.unit_id == unit_id and request.status not in {"resolved", "rejected"}
        )
        return items

    def manager_status(self, now: datetime) -> list[str]:
        items = ["overdue_payment" for _ in self.overdue_payments(now)]
        items.extend(
            "maintenance_request"
            for request in self.requests.values()
            if request.status in {"submitted", "under_review"}
        )
        return items

    def actionable_notifications(self, recipient_id: str, now: datetime) -> list[Notification]:
        """Return one notification per actionable category and simulated day."""
        day = now.astimezone(timezone.utc).date()
        notifications: list[Notification] = []
        pending_requests = [
            request
            for request in self.requests.values()
            if request.status == "submitted"
        ]
        if recipient_id == "manager-1" and pending_requests:
            already_sent = any(
                notification.recipient_id == recipient_id
                and notification.kind == "maintenance_review_required"
                and notification.at.astimezone(timezone.utc).date() == day
                for notification in self.notifications
            )
            if not already_sent:
                notification = Notification(
                    recipient_id=recipient_id,
                    kind="maintenance_review_required",
                    item_count=len(pending_requests),
                    at=now.astimezone(timezone.utc),
                )
                self.notifications.append(notification)
                notifications.append(notification)
        return notifications


def seeded_environment() -> Environment:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return Environment(
        condominium_id="condo-1",
        units={"unit-101": "101"},
        memberships={"resident-1": "unit-101", "manager-1": "unit-101"},
        payments=[Payment(unit_id="unit-101", due_at=start.replace(day=5))],
    )


def notification_fatigue_environment() -> Environment:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return Environment(
        condominium_id="condo-1",
        units={"unit-101": "101", "unit-102": "102", "unit-103": "103"},
        memberships={
            "resident-1": "unit-101",
            "resident-1b": "unit-101",
            "resident-2": "unit-102",
            "resident-3": "unit-103",
            "manager-1": "unit-101",
        },
        payments=[
            Payment(unit_id="unit-101", due_at=start.replace(day=5)),
            Payment(unit_id="unit-102", due_at=start.replace(day=5)),
            Payment(unit_id="unit-103", due_at=start.replace(day=5)),
        ],
    )
