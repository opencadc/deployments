# ADR-003: Shared `workloads` namespace now, namespace evolution later

- Status: Accepted
- Date: March 12, 2026

## Context

The current Kueue repository baseline uses multiple managed namespaces, but the
target architecture wants one shared Kueue-managed namespace at first so queue
governance, RBAC, and visibility can be kept simple while the new tenant model
is introduced.

## Decision

Use one shared `workloads` namespace for Kueue-managed user workloads in the
target single-cluster design. Create project-scoped `LocalQueue` objects in that
shared namespace on demand.

Future supported namespace layouts include one namespace per community, one namespace per workload class, or a
hybrid namespace layout.

## Consequences

This keeps the initial rollout simpler and reduces the number of moving parts
while project-based fairness and community ownership are introduced.

Future namespace splits remain possible without changing the core
community-project-cohort model.

## Alternatives considered

- Start immediately with one namespace per community
- Start immediately with one namespace per workload class

Both alternatives increase governance and visibility complexity too early for
production commitment.
