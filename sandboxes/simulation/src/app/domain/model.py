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
    paid_at: datetime | None = None


@dataclass
class MaintenanceRequest:
    request_id: str
    unit_id: str
    opened_by: str
    category: str
    description: str
    status: str = "submitted"
    created_at: datetime | None = None


@dataclass(frozen=True)
class Notification:
    recipient_id: str
    kind: str
    item_count: int
    at: datetime
    item_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class MembershipPeriod:
    resident_id: str
    unit_id: str
    active_from: datetime
    active_until: datetime | None = None


@dataclass(frozen=True)
class ActivityItem:
    kind: str
    summary: str
    at: datetime
    subject_id: str


@dataclass(frozen=True)
class StatusSummary:
    viewer_id: str
    action_items: tuple[str, ...]
    latest_update: str | None
    open_delivery_ids: tuple[str, ...]


@dataclass(frozen=True)
class Announcement:
    condominium_id: str
    announcement_id: str
    title: str
    body: str
    priority: str
    published_at: datetime
    expires_at: datetime | None = None


@dataclass
class Delivery:
    delivery_id: str
    condominium_id: str
    unit_id: str
    description: str
    received_at: datetime
    status: str = "waiting"
    collected_at: datetime | None = None


@dataclass
class Environment:
    condominium_id: str
    units: dict[str, str]
    memberships: dict[str, str]
    residents: set[str] = field(default_factory=set)
    roles: dict[str, str] = field(default_factory=dict)
    membership_history: list[MembershipPeriod] = field(default_factory=list)
    payments: list[Payment] = field(default_factory=list)
    requests: dict[str, MaintenanceRequest] = field(default_factory=dict)
    events: list[Event] = field(default_factory=list)
    notifications: list[Notification] = field(default_factory=list)
    announcements: list[Announcement] = field(default_factory=list)
    deliveries: dict[str, Delivery] = field(default_factory=dict)

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
            residents=set(initial.residents),
            roles=dict(initial.roles),
            membership_history=list(initial.membership_history),
            payments=[Payment(unit_id=payment.unit_id, due_at=payment.due_at, status=payment.status, paid_at=payment.paid_at) for payment in initial.payments],
            announcements=list(initial.announcements),
            deliveries={delivery_id: Delivery(**vars(delivery)) for delivery_id, delivery in initial.deliveries.items()},
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
                created_at=event.at,
            )
        elif event.name == "maintenance_status_changed":
            request = self.requests[event.payload["request_id"]]
            request.status = event.payload["to"]
        elif event.name == "payment_paid":
            payment = self.payments[int(event.payload["payment_index"])]
            payment.status = "paid"
            payment.paid_at = event.at
        elif event.name == "resident_moved":
            self._close_membership(event.payload["resident_id"], event.payload["from_unit_id"], event.at)
            self.membership_history.append(
                MembershipPeriod(
                    resident_id=event.payload["resident_id"],
                    unit_id=event.payload["to_unit_id"],
                    active_from=event.at,
                )
            )
            self.memberships[event.payload["resident_id"]] = event.payload["to_unit_id"]
        elif event.name == "resident_departed":
            self._close_membership(
                event.payload["resident_id"],
                event.payload["unit_id"],
                event.at,
            )
            self.memberships.pop(event.payload["resident_id"], None)
            self.residents.discard(event.payload["resident_id"])
        elif event.name == "resident_rejoined":
            self.membership_history.append(
                MembershipPeriod(
                    resident_id=event.payload["resident_id"],
                    unit_id=event.payload["unit_id"],
                    active_from=event.at,
                )
            )
            self.memberships[event.payload["resident_id"]] = event.payload["unit_id"]
            self.residents.add(event.payload["resident_id"])

    def _close_membership(self, resident_id: str, unit_id: str, at: datetime) -> None:
        for index, membership in enumerate(self.membership_history):
            if (
                membership.resident_id == resident_id
                and membership.unit_id == unit_id
                and membership.active_until is None
            ):
                self.membership_history[index] = MembershipPeriod(
                    resident_id=membership.resident_id,
                    unit_id=membership.unit_id,
                    active_from=membership.active_from,
                    active_until=at,
                )

    def overdue_payments(self, now: datetime) -> list[Payment]:
        current = now.astimezone(timezone.utc)
        for index, payment in enumerate(self.payments):
            if payment.status == "pending" and current >= payment.due_at:
                self.record("payment_overdue", current, payment_index=str(index))
        return [
            payment
            for payment in self.payments
            if current >= payment.due_at
            and (
                payment.status in {"pending", "overdue"}
                or (payment.status == "paid" and payment.paid_at is not None and payment.paid_at > current)
            )
        ]

    def mark_payment_paid(self, payment_index: int, at: datetime, confirmed_by: str | None = None) -> None:
        if confirmed_by is not None:
            self.require_manager(confirmed_by)
        payment = self.payments[payment_index]
        if payment.status == "paid":
            raise ValueError("payment is already paid")
        if payment.status == "cancelled":
            raise ValueError("cancelled payment cannot be paid")
        payment.status = "paid"
        payment.paid_at = at.astimezone(timezone.utc)
        self.record("payment_paid", payment.paid_at, payment_index=str(payment_index))

    def open_request(self, now: datetime, *, request_id: str, resident_id: str, category: str, description: str) -> Event:
        self.require_resident(resident_id)
        unit_id = self.unit_for_resident(resident_id, now)
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
        self.require_manager(manager_id)
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

    def require_resident(self, resident_id: str) -> None:
        if self.roles.get(resident_id) != "resident":
            raise PermissionError("only a resident can perform this action")

    def require_manager(self, manager_id: str) -> None:
        if self.roles.get(manager_id) != "building_manager":
            raise PermissionError("only a building manager can perform this action")

    def _is_manager(self, viewer_id: str) -> bool:
        return self.roles.get(viewer_id) == "building_manager"

    def resident_status(self, resident_id: str, now: datetime) -> list[str]:
        unit_id = self.unit_for_resident(resident_id, now)
        items = ["overdue_payment" for payment in self.overdue_payments(now) if payment.unit_id == unit_id]
        items.extend(
            "maintenance_request"
            for request in self.requests.values()
            if request.unit_id == unit_id and request.status not in {"resolved", "rejected"}
            and (request.created_at is None or request.created_at <= now.astimezone(timezone.utc))
        )
        return items

    def unit_for_resident(self, resident_id: str, at: datetime) -> str:
        if self.membership_history:
            active = [
                membership
                for membership in self.membership_history
                if membership.resident_id == resident_id
                and membership.active_from <= at
                and (membership.active_until is None or at < membership.active_until)
            ]
            if not active:
                raise KeyError(f"resident has no active unit at {at.isoformat()}: {resident_id}")
            return max(active, key=lambda membership: membership.active_from).unit_id
        return self.memberships[resident_id]

    def move_resident(self, resident_id: str, new_unit_id: str, at: datetime) -> None:
        if new_unit_id not in self.units:
            raise KeyError(f"unknown unit: {new_unit_id}")
        old_unit_id = self.unit_for_resident(resident_id, at)
        if old_unit_id == new_unit_id:
            raise ValueError("resident is already assigned to that unit")
        self.record(
            "resident_moved",
            at,
            resident_id=resident_id,
            from_unit_id=old_unit_id,
            to_unit_id=new_unit_id,
        )

    def leave_resident(self, resident_id: str, at: datetime) -> None:
        current_unit_id = self.unit_for_resident(resident_id, at)
        self.record("resident_departed", at, resident_id=resident_id, unit_id=current_unit_id)

    def rejoin_resident(self, resident_id: str, unit_id: str, at: datetime) -> None:
        if self.roles.get(resident_id) != "resident":
            raise PermissionError("only a resident can rejoin the condominium")
        if unit_id not in self.units:
            raise KeyError(f"unknown unit: {unit_id}")
        try:
            self.unit_for_resident(resident_id, at)
        except KeyError:
            self.record("resident_rejoined", at, resident_id=resident_id, unit_id=unit_id)
            return
        raise ValueError("resident already has an active membership")

    def manager_status(self, now: datetime) -> list[str]:
        items = ["overdue_payment" for _ in self.overdue_payments(now)]
        items.extend(
            "maintenance_request"
            for request in self.requests.values()
            if request.status in {"submitted", "under_review"}
            and (request.created_at is None or request.created_at <= now.astimezone(timezone.utc))
        )
        return items

    def publish_announcement(
        self,
        announcement_id: str,
        title: str,
        body: str,
        priority: str,
        published_at: datetime,
        expires_at: datetime | None = None,
        *,
        published_by: str,
    ) -> Announcement:
        self.require_manager(published_by)
        if priority not in {"normal", "high"}:
            raise ValueError(f"unknown announcement priority: {priority}")
        announcement = Announcement(
            condominium_id=self.condominium_id,
            announcement_id=announcement_id,
            title=title,
            body=body,
            priority=priority,
            published_at=published_at.astimezone(timezone.utc),
            expires_at=expires_at.astimezone(timezone.utc) if expires_at else None,
        )
        self.announcements.append(announcement)
        return announcement

    def active_announcements(self, now: datetime) -> list[Announcement]:
        current = now.astimezone(timezone.utc)
        return sorted(
            [
                announcement
                for announcement in self.announcements
                if announcement.condominium_id == self.condominium_id
                if announcement.published_at <= current
                and (announcement.expires_at is None or current < announcement.expires_at)
            ],
            key=lambda announcement: (
                announcement.priority != "high",
                -announcement.published_at.timestamp(),
                announcement.announcement_id,
            ),
        )

    def record_delivery(
        self,
        delivery_id: str,
        unit_id: str,
        description: str,
        received_at: datetime,
        recorded_by: str,
    ) -> Delivery:
        self.require_manager(recorded_by)
        if delivery_id in self.deliveries:
            raise ValueError(f"delivery already exists: {delivery_id}")
        if unit_id not in self.units:
            raise KeyError(f"unknown unit: {unit_id}")
        delivery = Delivery(
            delivery_id=delivery_id,
            condominium_id=self.condominium_id,
            unit_id=unit_id,
            description=description,
            received_at=received_at.astimezone(timezone.utc),
        )
        self.deliveries[delivery_id] = delivery
        return delivery

    def open_deliveries(self, viewer_id: str, at: datetime) -> list[Delivery]:
        if self._is_manager(viewer_id):
            visible_units = set(self.units)
        else:
            visible_units = {self.unit_for_resident(viewer_id, at)}
        return sorted(
            [
                delivery
                for delivery in self.deliveries.values()
                if delivery.condominium_id == self.condominium_id
                and delivery.unit_id in visible_units
                and delivery.received_at <= at.astimezone(timezone.utc)
                and delivery.status == "waiting"
            ],
            key=lambda delivery: (delivery.received_at, delivery.delivery_id),
        )

    def status_summary(self, viewer_id: str, at: datetime) -> StatusSummary:
        if self._is_manager(viewer_id):
            action_items = self.manager_status(at)
        else:
            action_items = self.resident_status(viewer_id, at)
        open_deliveries = self.open_deliveries(viewer_id, at)
        action_items = [*action_items, *(["delivery"] * len(open_deliveries))]
        announcements = self.active_announcements(at)
        return StatusSummary(
            viewer_id=viewer_id,
            action_items=tuple(action_items),
            latest_update=announcements[0].title if announcements else None,
            open_delivery_ids=tuple(delivery.delivery_id for delivery in open_deliveries),
        )

    def collect_delivery(self, delivery_id: str, viewer_id: str, at: datetime) -> None:
        delivery = self.deliveries[delivery_id]
        if not self._is_manager(viewer_id):
            self.require_resident(viewer_id)
            if self.unit_for_resident(viewer_id, at) != delivery.unit_id:
                raise PermissionError("resident cannot collect another unit's delivery")
        if delivery.status != "waiting":
            raise ValueError("delivery is already collected")
        delivery.status = "collected"
        delivery.collected_at = at.astimezone(timezone.utc)

    def activity_history(self, viewer_id: str, now: datetime) -> list[ActivityItem]:
        """Build a small user-facing history, not a raw technical event log."""
        self.overdue_payments(now)
        is_manager = self._is_manager(viewer_id)
        if is_manager:
            viewer_units: set[str] | None = None
        elif self.membership_history:
            viewer_units = {
                membership.unit_id
                for membership in self.membership_history
                if membership.resident_id == viewer_id
            }
        else:
            viewer_units = {self.unit_for_resident(viewer_id, now)}
        activities: list[ActivityItem] = []
        for event in self.events:
            if event.at > now.astimezone(timezone.utc):
                continue
            if event.name == "payment_overdue":
                payment = self.payments[int(event.payload["payment_index"])]
                if not is_manager and payment.unit_id not in viewer_units:
                    continue
                activities.append(ActivityItem("payment", "Payment is overdue", payment.due_at, payment.unit_id))
            elif event.name == "payment_paid":
                payment = self.payments[int(event.payload["payment_index"])]
                if not is_manager and payment.unit_id not in viewer_units:
                    continue
                activities.append(ActivityItem("payment", "Payment marked paid", event.at, payment.unit_id))
            elif event.name == "maintenance_opened":
                request_id = event.payload["request_id"]
                request = self.requests[request_id]
                if not is_manager and request.unit_id not in viewer_units:
                    continue
                activities.append(ActivityItem("maintenance", "Maintenance request submitted", event.at, request_id))
            elif event.name == "maintenance_status_changed":
                request_id = event.payload["request_id"]
                request = self.requests[request_id]
                if not is_manager and request.unit_id not in viewer_units:
                    continue
                activities.append(
                    ActivityItem(
                        "maintenance",
                        f"Maintenance request {event.payload['to'].replace('_', ' ')}",
                        event.at,
                        request_id,
                    )
                )
        return sorted(activities, key=lambda activity: activity.at)

    def actionable_notifications(self, recipient_id: str, now: datetime) -> list[Notification]:
        """Return one notification per actionable category and simulated day."""
        day = now.astimezone(timezone.utc).date()
        notifications: list[Notification] = []
        pending_requests = [
            request
            for request in self.requests.values()
            if request.status == "submitted"
        ]
        if self._is_manager(recipient_id) and pending_requests:
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

    def maintenance_status_notifications(self, request_id: str, now: datetime) -> list[Notification]:
        request = self.requests[request_id]
        recipients = sorted(
            [
            resident_id
            for resident_id in self.residents
            if self.memberships.get(resident_id) == request.unit_id
            ]
        )
        kind = f"maintenance_status_{request.status}"
        notifications: list[Notification] = []
        for recipient_id in recipients:
            existing_index, existing = next(
                (
                    (index, notification)
                    for index, notification in enumerate(self.notifications)
                    if notification.recipient_id == recipient_id
                    and notification.kind == kind
                    and notification.at.astimezone(timezone.utc).date() == now.astimezone(timezone.utc).date()
                ),
                (None, None),
            )
            if existing is not None:
                if request_id in existing.item_ids:
                    continue
                notification = Notification(
                    recipient_id=recipient_id,
                    kind=kind,
                    item_count=existing.item_count + 1,
                    at=existing.at,
                    item_ids=tuple(sorted((*existing.item_ids, request_id))),
                )
                self.notifications[existing_index] = notification  # type: ignore[index]
                notifications.append(notification)
                continue
            notification = Notification(
                recipient_id=recipient_id,
                kind=kind,
                item_count=1,
                at=now.astimezone(timezone.utc),
                item_ids=(request_id,),
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
        residents={"resident-1"},
        roles={"resident-1": "resident", "manager-1": "building_manager"},
        membership_history=[MembershipPeriod("resident-1", "unit-101", start)],
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
        residents={"resident-1", "resident-1b", "resident-2", "resident-3"},
        roles={
            "resident-1": "resident",
            "resident-1b": "resident",
            "resident-2": "resident",
            "resident-3": "resident",
            "manager-1": "building_manager",
        },
        membership_history=[
            MembershipPeriod("resident-1", "unit-101", start),
            MembershipPeriod("resident-1b", "unit-101", start),
            MembershipPeriod("resident-2", "unit-102", start),
            MembershipPeriod("resident-3", "unit-103", start),
        ],
        payments=[
            Payment(unit_id="unit-101", due_at=start.replace(day=5)),
            Payment(unit_id="unit-102", due_at=start.replace(day=5)),
            Payment(unit_id="unit-103", due_at=start.replace(day=5)),
        ],
    )
