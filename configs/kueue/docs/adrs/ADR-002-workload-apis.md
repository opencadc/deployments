# ADR-002: Supported Workload APIs

- Status: Accepted
- Date: Spring 2025

## Context

The target architecture must support a broad workload taxonomy, but the current
repository baseline and the need for safe operational rollout make it unwise to
treat every Kueue integration production commitment.

## Decision

Production support centers on `batch/v1.Job`, including Indexed Job
usage patterns for large independent fan-out work. Protected interactive and
persistent workloads may be brought under Kueue using mature controller
patterns, but only where the team can verify the operational behavior.

`JobSet`, MPI, Ray, and other advanced or distributed controllers remain part of
the target taxonomy and future roadmap, not the initial production commitment.

## Consequences

The platform gets a safe first production lane for large-scale batch admission
without blocking future support for more advanced workload types.

The package still documents the full workload taxonomy so later phases do not
need to invent a new fairness or queue model.

## Alternatives considered

- Promise full support for every Kueue integration production commitment
- Delay all interactive or persistent integration until after batch-only rollout

The first option creates avoidable operational risk. The second option breaks
the desired unified scheduling model too early.
