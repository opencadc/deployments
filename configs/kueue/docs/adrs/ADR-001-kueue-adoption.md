# ADR-001: Kueue Adoption

- Status: Accepted
- Date: January 2025

## Context

CANFAR needs a Kubernetes-native way to control admission, queueing, quotas,
borrowing, reclaim, and visibility for a mix of interactive, persistent, and
batch science workloads. The platform must handle very large pending backlogs
without treating direct Kubernetes scheduling as the tenant policy layer.

## Decision

CANFAR adopts Kueue as the admission and quota orchestration layer for the
Science Platform. Kubernetes remains the runtime scheduler and execution plane.
`skaha` remains the main user submission entry point.

## Consequences

Kueue provides the needed queue, quota, priority, cohort, and visibility
primitives. It also creates a clean path to future topology-aware scheduling and
MultiKueue.

CANFAR must still solve identity, project mapping, and accounting outside
Kueue. Kueue is not the tenant system of record.

## Alternatives considered

- Continue with direct Kubernetes scheduling and custom ad hoc controls
- Build a custom scheduling layer or scheduler plugin stack
- Treat the backlog problem as only a `skaha` rate-limiting problem

These alternatives either move too much policy into custom code or fail to give
native cohort, quota, and admission control semantics.
