# ADR-008: Queue enforcement and managed namespace model

- Status: Accepted
- Date: March 12, 2026

## Context

Kueue policy only works predictably when managed workloads land in managed
namespaces and carry valid queue information. CANFAR requires users to
submit through `skaha`, not through raw Kubernetes APIs without platform policy.

## Decision

Use explicitly managed namespaces for Kueue-managed user work. In the target
state this is one shared `workloads` namespace. The submission path must resolve
and apply a `LocalQueue` explicitly.

Keep `manageJobsWithoutQueueName` disabled and reject malformed or unqueued
submissions in managed namespaces through admission policy and service-side
validation.

## Consequences

The scheduler does not need to guess tenant identity. Platform policy remains
explicit, and visibility stays consistent with actual queue assignment.

Future namespace evolution remains possible as long as the same enforcement
principles are preserved.

## Alternatives considered

- Allow silent default queue assignment everywhere
- Allow users to create unmanaged work in the same namespaces as managed work

These alternatives make fairness and explanation harder to trust.
