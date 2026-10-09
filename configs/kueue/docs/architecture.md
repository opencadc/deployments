# CANFAR Science Platform Kueue Architecture

This document is the primary architecture reference for Kueue rollout on the CANFAR Science
Platform. It captures the current baseline, the target
single-cluster architecture, and the future-ready extension points for
MultiKueue, topology-aware scheduling, and richer tenant control.

Use this document together with [roadmap.md](./roadmap.md), [operations.md](./operations.md),
[ui-spec.md](./ui-spec.md), and [the ADR index](./adrs/README.md). The existing
deep-dive reference remains useful background material, but this document is the
system design source of truth.

## 1. Introduction

This section defines the problem, the user groups, and the success criteria for
the Kueue architecture on the CANFAR Science Platform.

### 1.1 Problem statement

The CANFAR Science Platform needs a batch and tenant-admission layer for Kubernetes
that can absorb very large pending backlogs while still giving users predictable
submission behavior and clear explanations for delay. The platform must support
interactive sessions, persistent user-facing services, MPI and distributed jobs,
and very large numbers of batch jobs in the same managed environment.

The design target is not only to admit work fairly. It must also preserve
control-plane health when the backlog grows to `100,000`, `200,000`, or more
pending jobs or workload objects, while the active execution footprint remains
much smaller.

### 1.2 Users and stakeholders

The architecture serves the following groups:

- Science users who launch notebooks, interactive tools, batch jobs, and
  distributed workloads through `Skaha`
- Project administrators who manage projects and group membership inside a
  community
- Cluster system administrators who own infrastructure, Kueue policy, and
  emergency controls
- Platform operators who need strong observability, clear runbooks, and safe
  rollout procedures
- Future control-service operators who will manage community ownership, project
  metadata, and accounting relationships

### 1.3 Success Criteria

The design is successful when the platform can:

- Admit and manage work fairly across communities and projects
- Prioritize interactive work over batch work inside each project
- Preserve community ownership of resources while still borrowing idle capacity
- Explain pending or rejected work in terms users and admins can act on
- Support at least one shared production workload namespace now
- Stay compatible with future namespace splits, MultiKueue, and topology-aware
  scheduling
- Produce benchmark evidence and operational thresholds rather than relying on
  informal tuning

### 1.4 Quality Goals

The top quality goals for this system are:

- Fairness: projects compete fairly within a community, and communities reclaim
  owned resources within a cohort
- Transparency: users and admins can see why work is pending, admitted,
  preempted, or rejected
- Reliability: the Kueue control plane, Kubernetes API, and visibility surfaces
  remain healthy under heavy pending backlog
- Operability: cluster admins can pause, drain, observe, and roll back changes
  safely
- Scalability: the design can grow from a single-cluster deployment into a
  manager and worker model without rewriting the tenancy model

## 2. Constraints

This section captures the hard realities that shape the design.

### 2.1 Repository and Deployment Baseline

The current repository baseline still reflects an older Kueue deployment:

- Current deployment documents `0.11.6` as the installed release
- Current deployment uses `config.kueue.x-k8s.io/v1beta1`
- Current deployment uses `batch/job` only
- Current deployment references `skaha-workload` and `canfar-b-workload` rather than a single shared `workloads` namespace

This architecture therefore distinguishes three states:

- Current state: the repository and deployed baseline today
- Target state: the single-cluster architecture described in this package
- Future state: capabilities that remain out of scope for phase 1 but must stay
  compatible with the design

### 2.2 Identity and governance constraints

The current identity hierarchy is:

`Community -> Project -> POSIX Group -> User`

This means the scheduler cannot be the system of record for tenant structure.
Kueue needs an external control service to provide authoritative definitions for
communities, projects, project-to-group mappings, and later accounting policy.

### 2.3 Namespace constraint

The target design uses one shared `workloads` namespace for Kueue-managed user
work now. `LocalQueue` objects are still project-scoped, but they exist in that
shared namespace and are created on demand.

The architecture must also stay compatible with future namespace evolution, such
as:

- one namespace per community
- one namespace per workload class, such as `gpu-workloads` or
  `batch-workloads`

Those namespace changes are future roadmap items, not phase 1 requirements.

### 2.4 Operational constraints

The system must work in an environment where:

- the cluster is managed by CADC
- users mostly submit via `Skaha`, not by direct raw Kubernetes access
- batch backlog can exceed active capacity by two or more orders of magnitude
- interactive and persistent work cannot be treated as disposable noise
- the real bottleneck may be Kueue, the Kubernetes API server, etcd, or the
  submission path, not just one controller setting

## 3. Context and scope

This section defines the system boundary and the key external actors.

### 3.1 System scope

The architecture covers:

- `Skaha` submission and workload resolution behavior
- Kueue queue, quota, flavor, and priority objects
- the future standalone accounting and control service
- user, project admin, and cluster admin visibility surfaces
- benchmark and operations evidence for scale and correctness

The architecture does not implement:

- the control service itself
- the accounting penalty model for temporary fair-share overrides
- a production user interface implementation
- a MultiKueue production rollout in phase 1

### 3.2 Communities and cohorts

Resources such as CPU, memory, storage, GPUs, network bandwidth, and I/O are
owned at the community level. Communities are implemented as `ClusterQueue`
objects. Multiple communities together form a cohort and may lend or borrow
capacity from one another.

The initial named communities used in examples and diagrams are:

- `cadc`
- `ska`
- `chimefrb`

### 3.3 Projects and local queues

Projects exist inside a community and are implemented as `LocalQueue` objects.
`LocalQueue` creation is project-scoped and on demand. The `LocalQueue`
therefore represents the scheduler-facing identity of a project inside a shared
community resource pool.

This has one important consequence: project fair sharing is intra-community.
Projects compete fairly with other projects that target the same community
`ClusterQueue`. Cross-community competition is governed by `ClusterQueue`
policies and the cohort, not by one global project fair-share plane.

## 4. Solution strategy

This section states the high-level design strategy and the main trade-offs.

### 4.1 Scheduler model

Kueue acts as the admission and quota orchestration layer. Kubernetes still
performs pod placement and runtime scheduling. Kueue decides when work can enter
the active scheduling plane and under what quota, flavor, and priority rules.

### 4.2 Tenancy model

The target tenancy mapping is:

- Community = `ClusterQueue`
- Project = `LocalQueue`
- Multiple communities = one or more `Cohort` relationships

This model gives CANFAR the following properties:

- community-owned resources remain a first-class concept
- communities can lend and borrow unused capacity
- projects compete fairly inside their community
- workload class ordering stays project-local through priority
- the control service remains the source of truth for project and group mapping

### 4.3 Fairness and priority model

The scheduling and fairness model is split deliberately:

- Within a cohort of communities, communities borrow and reclaim through
  `ClusterQueue` and cohort policy.
- Within a single community, projects compete using Admission Fair Sharing,
  driven by `LocalQueue` historical usage and adjustable weights.
- Within a project, workloads are ordered by `WorkloadPriorityClass`.

This preserves an important operational rule: interactive work wins inside a
project, but not at the cost of pretending that project fair-share history does
not exist. A project that has consumed a great deal of recent capacity can still
feel the effect of fair-share decay, even if its next workload is interactive.

### 4.4 Control service strategy

Kueue is not the tenant authority. A future standalone accounting and control
service is required to manage:

- community definitions and resource ownership
- project creation inside a community
- project-to-group mappings
- quota and usage relationships outside raw Kueue quota semantics
- temporary fair-share override workflow for project admins and cluster admins

This service is out of scope for phase 1 implementation, but it is in scope for
architecture and requirements.

## 5. Building block view

This section describes the main building blocks of the target system.

### 5.1 Submission plane

The submission plane consists of:

- `Skaha` as the main user-facing submission path
- a queue and policy resolution layer inside `Skaha`
- the future control service for project, group, and ownership lookup

`Skaha` accepts a user request, resolves the effective project and community,
selects the correct `LocalQueue`, attaches the required labels, and creates the
workload object in the shared `workloads` namespace.

### 5.2 Queueing plane

The queueing plane consists of Kueue CRDs and controller behavior:

- `ResourceFlavor` for cluster, zone, hardware, and future topology identity
- `ClusterQueue` for community-owned quota and preemption rules
- `LocalQueue` for project-level competition within a community
- `WorkloadPriorityClass` for workload-class ordering within a project
- `Cohort` for sharing and reclaim between communities

### 5.3 Execution plane

The execution plane remains native Kubernetes:

- Kubernetes API server and etcd store all workload state
- the default scheduler places admitted pods
- workload-specific controllers such as `Job`, `JobSet`, `MPIJob`, or `Ray`
  drive runtime behavior after admission

### 5.4 Visibility plane

The visibility plane combines several sources:

- Kueue Prometheus metrics
- the Kueue pending-workloads visibility API
- Kubernetes and apiserver metrics
- a future UI for user and admin-facing queue explanations

The architecture uses these sources to explain whether a workload is delayed
because of fair-share position, workload priority, resource shortage, quota
exhaustion, or policy rejection.

### 5.5 Control service requirements

The future standalone accounting and control service must support:

- cluster admins creating and managing communities
- delegated project admins creating projects within a community
- attaching one or more POSIX groups to a project
- resolving a user or group to the correct project at submission time, or
  requiring explicit project selection when the mapping model is ambiguous
- tracking usage and quota relationships that are out of scope for Kueue alone
- handling temporary fair-share override requests

The service must expose enough state for both `Skaha` and the user visibility
surface. It does not need to become the workload execution system.

## 6. Runtime view

This section describes the key runtime behaviors of the target system. Detailed
sequence diagrams are provided in [diagrams.md](./diagrams.md).

### 6.1 Submit and admit flow

The normal runtime path is:

1. A user submits work through `Skaha`.
2. `Skaha` resolves the effective project and community through internal policy
   and later through the control service. If the mapping model is ambiguous, the
   submission path requires explicit project selection.
3. `Skaha` selects a `LocalQueue`, applies the required labels, and creates the
   Kubernetes workload object in `workloads`.
4. Kueue creates or updates the corresponding `Workload`.
5. Kueue evaluates quota, flavors, priority, and admission checks.
6. Once quota is reserved and admission is satisfied, Kueue admits the
   workload.
7. Kubernetes schedules the pods and the native controller runs them.

### 6.2 Community borrowing and reclaim

When one community is idle and another is busy, the busy community can borrow
from the cohort. When the idle community becomes active again, Kueue reclaims
nominal quota according to cohort preemption policy.

This behavior is community-scoped. It is not project-scoped reclaim. Project
competition inside a community is governed separately through `LocalQueue`
fairness and workload priority.

### 6.3 Priority and fair-share interaction

Project fair-sharing decides which project gets the next chance to consume
community quota. Workload priority decides which workload from that project is
selected first.

This means:

- higher-priority interactive work can win against lower-priority batch work
  inside the same project
- a project with a high recent usage history can still wait behind a project
  with lower recent usage
- temporary fair-share weight adjustments change the project's relative share,
  not just the priority of one workload

### 6.4 Pending-state explanation

The platform must expose actionable pending reasons. The user-facing explanation
model uses the following categories:

- waiting behind higher fair-share demand from other projects in the same
  community
- waiting behind higher-priority workloads in the same project
- blocked because owned or borrowed resources are not currently available
- blocked because the project or submission policy rejected the request
- blocked because the control plane is degraded and admission is not keeping up

## 7. Deployment view

This section describes the target single-cluster deployment and the future
expansion path.

### 7.1 Current target deployment

The target single-cluster deployment includes:

- one Kueue control plane in `kueue-system`
- one shared `workloads` namespace for Kueue-managed user workloads
- one `ClusterQueue` per community, such as `cadc`, `ska`, and `chimefrb`
- one or more project `LocalQueue` objects per community, created on demand
- `ResourceFlavor` objects that capture cluster, zone, GPU class, and later
  topology-aware placement
- one monitoring stack with Prometheus and Grafana

### 7.2 Namespace evolution

The architecture preserves compatibility with future namespace splits. Likely
future directions are:

- namespace per community
- namespace per workload class
- mixed namespace policy for highly specialized resources

The scheduler model and control service model remain valid under any of these
future namespace layouts. The main affected areas are `LocalQueue` ownership,
RBAC, and visibility scope.

### 7.3 Multi-cluster future

The future-state expansion path is MultiKueue, with one manager cluster and one
or more worker clusters. The manager and workers must preserve the same
community, project, and flavor vocabulary so the single-cluster tenant model can
evolve rather than be replaced.

## 8. Cross-cutting concepts

This section captures concepts that shape multiple parts of the design.

### 8.1 Workload taxonomy

The architecture recognizes the following workload classes:

- Interactive sessions such as notebooks and user-facing interactive tools
- Persistent user-facing services or deployments
- Standard batch `Job`
- Indexed `Job` for large independent fan-out workloads
- `JobSet` and MPI-style grouped or distributed jobs
- `RayJob`, `RayCluster`, and related distributed compute workloads
- Cron-triggered batch work
- Plain Pod or exception paths only when a better controller does not exist

Phase 1 does not need to productionize every Kueue integration, but the
taxonomy must be documented now because it affects priority, fairness, and
observability semantics.

### 8.2 Resource ownership and flavors

Communities own resources. Kueue expresses that ownership through `ClusterQueue`
quota and `ResourceFlavor` taxonomy. The flavor model must support:

- CPU and memory
- storage classes and local storage distinctions when relevant
- GPU model and accelerator pool identity
- cluster and zone placement
- future topology domains such as rack, block, or GPU island

### 8.3 Governance and enforcement

Managed workloads must set a queue explicitly or be assigned one by the
submission service. The target governance model is:

- users submit through `Skaha`
- `Skaha` resolves `LocalQueue` assignment
- managed namespaces reject malformed or unqueued submissions
- cluster admins retain emergency controls for stopping or draining queues

### 8.4 Protected workloads

Interactive and persistent workloads remain part of the same Kueue-managed
system, but they are not treated the same way as best-effort batch. Persistent
workloads are a protected class. Interactive work holds higher workload priority
than batch inside each project.

The architecture deliberately leaves room for stricter protection later if
evidence shows that the single-plane model causes avoidable user pain.

### 8.5 Temporary fair-share overrides

Project admins may request temporary fair-share overrides through a future UI
and control-service workflow. Only cluster admins can approve or apply those
changes.

The downstream accounting model for the quota or usage cost of those overrides
is explicitly out of scope here. This architecture only records the requirement
that the accounting model must exist and must remain visible to admins.

## 9. Quality requirements

This section turns the earlier goals into concrete architecture obligations.

### 9.1 Reliability

The design must keep Kueue and the Kubernetes API healthy under load. The
architecture therefore requires:

- benchmark-driven thresholds
- explicit rollout and rollback procedures
- visibility into queue backlog and controller saturation

### 9.2 Transparency

The design must expose queue state in ways users can understand without reading
controller logs or raw conditions. The UI and observability model therefore must
present effective fair-share state, workload priority, ownership boundaries, and
pending reasons clearly.

### 9.3 Scalability

The design must support large pending backlogs without assuming that listing all
raw objects remains cheap. This is why the architecture treats visibility APIs,
metrics, and summary views as primary interfaces rather than optional extras.

### 9.4 Operability

Cluster admins must be able to:

- inspect community and project usage quickly
- pause or drain queues safely
- identify whether bottlenecks are in Kueue, the Kubernetes API, or the
  submission path
- run repeatable benchmark suites before changing policy or scale assumptions

## 10. Risks and technical debt

This section identifies the major known risks.

- The current repository baseline is behind the target capability set and will
  require careful Kueue upgrade work before all target features are usable.
- Fairness is easy to misinterpret. Users may perceive a correct fair-share
  result as unfair if the UI does not explain recent usage and priority clearly.
- The one shared namespace is operationally simple now, but it may become a
  pressure point for RBAC and visibility policy as more workload types are
  onboarded.
- Flexible workloads with changing resource shape can challenge request-based
  admission semantics and will need careful validation before broader use.
- The control service is required by the architecture but remains out of scope
  for immediate implementation, so integration points must stay explicit.
- MultiKueue and topology-aware scheduling remain future capabilities with
  meaningful operational constraints and must not be promised as phase 1
  features.

## 11. Decisions summary

This section summarizes the architectural decisions captured in detail by the
ADR set.

- Use Kueue as the admission and quota orchestration system.
- Model communities as `ClusterQueue` objects and projects as `LocalQueue`
  objects.
- Keep one shared `workloads` namespace now and treat namespace evolution as a
  future roadmap item.
- Use a standalone accounting and control service as the future system of
  record.
- Use fair-share weights for project competition and workload priority for
  project-internal ordering.
- Keep persistent workloads protected and interactive workloads higher priority
  than batch workloads.
- Preserve a MultiKueue-ready vocabulary even while deploying single-cluster
  first.

See [the ADR index](./adrs/README.md) for the full decision log.

## 12. Glossary

This glossary standardizes the key terms used across the package.

- Community: the top-level resource owner in CANFAR; implemented as a
  `ClusterQueue`
- Cohort: a set of `ClusterQueue` objects that may lend or borrow capacity
- Project: the scheduler-facing tenant inside a community; implemented as a
  `LocalQueue`
- POSIX group: an identity grouping used for project membership and submission
  resolution
- Workload class: a platform-level category such as interactive, persistent, or
  batch
- Fair-share weight: the configurable project weighting used for community-local
  project competition
- Workload priority: the ordering signal used inside a project's queue
- Control service: the future standalone service that stores communities,
  projects, mappings, and accounting relationships
