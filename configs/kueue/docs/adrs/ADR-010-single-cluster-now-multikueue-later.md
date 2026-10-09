# ADR-010: Single-cluster now, MultiKueue-ready later

- Status: Accepted
- Date: March 12, 2026

## Context

CANFAR wants a design that can grow into a multi-cluster model, but the team
also needs to prove the policy model, control-plane behavior, and backlog
health in a single cluster before adding federation complexity.

## Decision

Build for a single-cluster production target first. Preserve a vocabulary and
resource model that remain compatible with future MultiKueue manager and worker
clusters.

Do not make MultiKueue a phase 1 requirement. Treat it as a later phase that is
triggered by proven need, such as API-server pressure, site-level separation, or
distinct hardware pools that require worker-cluster sharding.

## Consequences

The rollout remains practical while still avoiding a dead-end tenancy model.

The architecture package must still document manager-worker deployment patterns,
future quota mapping, and operational risks so later federation does not become
a redesign exercise.

## Alternatives considered

- Design only for one cluster with no future federation path
- Make MultiKueue a near-term mandatory target

The first option creates future migration pain. The second option adds too much
operational complexity before the single-cluster model is proven.
