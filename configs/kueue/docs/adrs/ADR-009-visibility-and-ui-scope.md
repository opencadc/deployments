# ADR-009: Visibility and UI scope

- Status: Accepted
- Date: March 12, 2026

## Context

Fair scheduling without understandable visibility will be perceived as arbitrary.
CANFAR's users, project admins, and cluster admins all need different levels of
insight into ownership, pending reasons, and current queue position.

## Decision

Treat visibility as a first-class architectural concern. Production commitment relies on
`kubectl`, Grafana, Kueue metrics, and the pending-workloads visibility API.
Later phases add a read-only queue UI and then guided admin workflows.

The UI must explain scheduling outcomes in terms of:

- fair-share position
- workload priority
- quota exhaustion
- insufficient resource availability
- policy rejection

## Consequences

The architecture gains a clear product surface instead of assuming that raw
conditions or controller logs are enough.

This also creates a requirement for the control service to expose tenant and
override metadata to the UI.

## Alternatives considered

- Delay visibility until after scheduling is complete
- Rely only on Kubernetes-native object inspection

These alternatives make correct policy look opaque to most users.
