# ADR-011: Protected persistent and interactive workloads

- Status: Accepted
- Date: March 12, 2026

## Context

CANFAR does not run only batch jobs. The platform also runs interactive sessions
and persistent user-facing services that users experience directly.

## Decision

Keep persistent and interactive work in the same overall Kueue-managed system,
but treat them as protected workload classes rather than ordinary best-effort
batch.

Inside each project:

- interactive work has higher workload priority than batch work
- persistent workloads are protected and must not be treated as cheap
  preemption targets

The exact controller integrations may mature in phases, but the policy model is
fixed now.

## Consequences

The platform retains a unified tenant and fairness model while still protecting
the user experience for long-lived or interactive work.

Operators must still watch for cases where the single-plane model causes too
much contention and then adjust protection or namespace boundaries later.

## Alternatives considered

- Keep all persistent and interactive work outside Kueue
- Treat persistent and interactive work exactly like best-effort batch

The first option breaks the unified policy model. The second option creates
avoidable user pain and preemption risk.
