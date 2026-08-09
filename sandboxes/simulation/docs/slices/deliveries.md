# Slice: delivery notifications

## Use-case contract

When a delivery is recorded for a unit, residents of that unit see it as an
open item. Residents cannot see or collect another unit's delivery. After
collection, the delivery leaves open items but remains historical data.

## Rules

- deliveries are condominium- and unit-scoped;
- delivery identifiers are unique within the simulation;
- only waiting deliveries appear as open items;
- collection is explicit and timestamped;
- manager visibility covers all units in the condominium;
- no hardware or courier integration is required.

## Done criteria

- resident visibility is unit-scoped;
- collection is authorized and idempotence is guarded;
- collection preserves delivery history;
- manager can inspect open deliveries across units;
- foreign-condominium deliveries are excluded from every view.

## Out of scope

Concierge devices, barcode scanning, courier integrations, resident-to-resident
sharing, delivery photos, and push-provider behavior.
