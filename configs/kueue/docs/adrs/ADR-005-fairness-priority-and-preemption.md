# ADR-005: Fairness, workload priority, and preemption model

- Status: Accepted
- Date: March 12, 2026

## Context

CANFAR needs fair competition between projects, community ownership of
resources, borrowing of idle capacity, and a workload-ordering model that keeps
interactive work ahead of batch work inside each project.

## Decision

Use the following split model:

- Community = `ClusterQueue`
- Project = `LocalQueue`
- Multiple communities sharing capacity = `Cohort`
- Project competition inside one community = Admission Fair Sharing with
  adjustable `LocalQueue` weights
- Workload ordering inside one project = `WorkloadPriorityClass`

Use cohort borrowing and reclaim for community-level resource ownership. Use
project-local workload priority to select interactive work before lower-priority
batch work inside the chosen project queue.

## Consequences

This preserves community ownership while still maximizing idle cluster use. It
also avoids pretending that project fair-share and workload priority are the
same thing.

Cross-community competition remains community-scoped rather than global
project-scoped. That is intentional.

## Alternatives considered

- One global project fair-share plane across all communities
- Priority-only scheduling without project fair-share weights
- Community-only fairness with no project-level balancing

These alternatives either ignore community ownership or fail to give projects a
meaningful fairness model inside a community.
