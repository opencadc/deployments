# Architecture Decision Records

This directory contains the architecture decision records for the CANFAR Science Platform Kueue
design.

## ADR index

| ADR | Title | Status |
| --- | ----- | ------ |
| [ADR-001](./ADR-001-kueue-adoption.md) | Why CANFAR adopts Kueue | Accepted |
| [ADR-002](./ADR-002-phase-1-workload-apis.md) | Supported workload APIs in phase 1 | Accepted |
| [ADR-003](./ADR-003-shared-workloads-namespace.md) | Shared `workloads` namespace now, namespace evolution later | Accepted |
| [ADR-004](./ADR-004-standalone-control-service.md) | Standalone accounting and control service | Accepted |
| [ADR-005](./ADR-005-fairness-priority-and-preemption.md) | Fairness, workload priority, and preemption model | Accepted |
| [ADR-006](./ADR-006-posix-group-project-mapping.md) | POSIX group to project mapping options | Proposed |
| [ADR-007](./ADR-007-resource-flavor-taxonomy.md) | ResourceFlavor taxonomy and topology model | Accepted |
| [ADR-008](./ADR-008-queue-enforcement-and-managed-namespaces.md) | Queue enforcement and managed namespace model | Accepted |
| [ADR-009](./ADR-009-visibility-and-ui-scope.md) | Visibility and UI scope | Accepted |
| [ADR-010](./ADR-010-single-cluster-now-multikueue-later.md) | Single-cluster now, MultiKueue-ready later | Accepted |
| [ADR-011](./ADR-011-protected-persistent-and-interactive-workloads.md) | Protected persistent and interactive workloads | Accepted |
| [ADR-012](./ADR-012-scale-testing-and-operational-evidence.md) | Scale-testing and operational evidence | Accepted |

## How to use the ADR set

Read the ADRs in numerical order the first time. After that, use the table
above to jump to the specific decision you need. Only ADR-006 remains open in
this package. All other ADRs define the current architectural intent for the
target rollout.
