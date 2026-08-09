from app.domain.model import Environment, notification_fatigue_environment

from .notification_fatigue import NOW


def run_delivery_slice() -> tuple[Environment, list[str]]:
    environment = notification_fatigue_environment()
    environment.record_delivery("delivery-1", "unit-101", "Small package", NOW)
    environment.record_delivery("delivery-2", "unit-102", "Large package", NOW)
    return environment, [delivery.delivery_id for delivery in environment.open_deliveries("resident-1", NOW)]
