# ADR-004: Standalone accounting and control service

- Status: Accepted
- Date: March 12, 2026

## Context

Kueue cannot serve as the system of record for communities, projects, POSIX
group mapping, delegated project administration, or accounting relationships.
Those concerns are fundamental to CANFAR's policy and visibility.

## Decision

Define a new standalone accounting and control service as a required future
dependency of the platform. The service remains out of scope for implementation
in this package, but it is in scope for architecture and requirements.

The service must support:

- community creation and management by cluster admins
- project creation inside a community by delegated project admins
- project-to-group mapping and later user or group resolution
- override request workflows for temporary fair-share changes
- exposure of tenant metadata to `skaha` and the future visibility UI

## Consequences

The scheduler design stays clean. Kueue owns admission and quota behavior while
the control service owns tenant and policy metadata.

The rollout now has an explicit dependency that must be addressed in later
phases rather than hidden behind manual configuration.

## Alternatives considered

- Extend an existing service implicitly without naming a new component
- Keep project metadata as static Kubernetes configuration only

Both alternatives hide ownership and make future admin workflows difficult to
design and operate.
