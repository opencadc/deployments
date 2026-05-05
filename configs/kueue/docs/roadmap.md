# CANFAR Kueue Roadmap

This roadmap turns the architecture into an execution plan with measurable phase
exits. Use it together with [architecture.md](./architecture.md), [operations.md](./operations.md),
[ui-spec.md](./ui-spec.md), and [the ADR set](./adrs/README.md).

## Roadmap principles

This roadmap follows four principles:

- Prove policy and control-plane behavior before claiming scale
- Keep one shared `workloads` namespace first, but preserve future namespace and
  MultiKueue compatibility
- Separate what Kueue owns from what the future control service owns
- Use evidence-based phase exits instead of subjective readiness claims

## Phase 0: Architecture closure and upgrade prerequisites

This phase closes the design, records the decisions, and prepares the current
older repository baseline for a safer Kueue upgrade.

### Deliverables

- Approved architecture package in `configs/kueue/docs`
- Confirmed target vocabulary for community, project, cohort, flavor, and
  workload class
- Inventory of current repository gaps between the deployed baseline and the
  target feature set
- Upgrade preflight checklist for current Kueue controller configuration and
  CRDs

### Key activities

- Validate the current Kueue deployment and CRD baseline against target
  features such as Admission Fair Sharing, visibility APIs, and later topology
  support
- Confirm the initial communities and example queue structure for `cadc`, `ska`,
  and `chimefrb`
- Define the target `workloads` namespace and identify migration tasks from the
  current namespace configuration
- Confirm the initial workload-class vocabulary: interactive, persistent,
  batch, and advanced distributed

### Dependencies

- Architecture approval
- Access to current cluster configuration and deployment history

### Acceptance criteria

- The architecture package is merged and accepted as the design baseline
- The upgrade preflight checklist exists and identifies all current config
  mismatches
- No unresolved architectural blocker remains except ADR-006

## Phase 1: Core Kueue platform hardening

This phase upgrades and hardens the Kueue control plane to support the target
tenant model and observability baseline.

### Deliverables

- Updated Kueue installation aligned with the target feature baseline
- Shared `workloads` namespace policy
- Initial `ClusterQueue` objects for `cadc`, `ska`, and `chimefrb`
- Initial `ResourceFlavor` taxonomy for cluster, zone, CPU, memory, and GPU
- Prometheus and Grafana coverage for queue, controller, and API health

### Key activities

- Upgrade Kueue safely from the current older release line
- Enable the feature gates and controller settings needed for the target model
- Move managed namespace scope to the shared `workloads` namespace
- Introduce community `ClusterQueue` objects and a shared cohort
- Standardize flavor naming and resource coverage
- Turn on the visibility and metrics surfaces needed for later phase evidence

### Dependencies

- Phase 0 complete
- Confirmed upgrade window and rollback method

### Acceptance criteria

- Kueue runs stably on the target baseline with no repeated controller crashes
- Community `ClusterQueue` objects exist and report metrics cleanly
- The visibility API and core queue metrics are reachable
- Rollback to the previous deployment has been exercised in a non-production
  environment

## Phase 2: Tenancy and control-service integration points

This phase establishes the community and project model operationally, even if
the full control service is not implemented yet.

### Deliverables

- Project `LocalQueue` creation model in the shared namespace
- Project fair-share weight policy and administrative workflow
- Submission resolution rules from user and group context to project and
  community
- Requirements contract for the future standalone control service

### Key activities

- Define the project naming convention for `LocalQueue` objects
- Establish how `Skaha` resolves the effective project today and later through
  the control service
- Introduce project fair-share weights with cluster-admin-only approval
- Record the future control-service API and data needs
- Decide how temporary override requests are surfaced and approved

### Dependencies

- Phase 1 complete
- Administrative agreement on tenant naming and ownership boundaries

### Acceptance criteria

- New projects can be represented as `LocalQueue` objects on demand
- Project weights are visible and adjustable by cluster admins
- The submission path can resolve project and community deterministically for
  the selected mapping model, or require explicit project selection when the
  mapping model is ambiguous
- The control-service requirements are specific enough to hand to a separate
  implementation effort

## Phase 3: Visibility UX and policy-aware diagnostics

This phase focuses on making scheduling behavior understandable to users and
admins.

### Deliverables

- Read-only queue explorer backed by Kueue visibility and metrics surfaces
- Pending-state explanation model implemented in the UI or CLI layer
- Resource ownership view by community and project
- Temporary fair-share override request workflow design

### Key activities

- Expose `LocalQueue` and `ClusterQueue` visibility in user-facing terms
- Show current effective project fair-share position and weight
- Show workload priority and protected workload-class policy
- Explain delays as one of the approved explanation categories
- Provide cluster-admin visibility into community reclaim and borrowing state

### Dependencies

- Phase 2 complete
- Stable visibility API and metrics from phase 1

### Acceptance criteria

- A user can inspect a workload and receive an actionable pending explanation
- A project admin can see project weight and current community position
- A cluster admin can inspect cohort borrowing and community reclaim behavior
- The UI language matches the vocabulary defined in `ui-spec.md`

## Phase 4: Scale, benchmark, and operational proof

This phase proves backlog scale and control-plane behavior with repeatable test
artifacts.

### Deliverables

- `kueuer` benchmark suites for raw Kueue and end-to-end `Skaha` pressure
- Measured thresholds for backlog growth and control-plane degradation
- Evidence pack for `10k`, `50k`, `100k`, and `200k` backlog gates
- Clear stop or go criteria for larger backlog claims

### Key activities

- Extend benchmark coverage to user-path submission and visibility stress
- Record admission timing, controller health, API server latency, and pending
  backlog behavior
- Measure user-facing interactive behavior during large batch backlog
- Capture failure modes such as memory pressure, API slowness, and visibility
  degradation

### Dependencies

- Phases 1 through 3 complete
- Bench environments and monitoring available

### Acceptance criteria

- Benchmark suites run repeatably and produce comparable artifacts
- The team can state a measured safe operating region for backlog size
- The evidence distinguishes Kueue bottlenecks from API-server or etcd
  bottlenecks
- Interactive and protected workloads retain acceptable service behavior during
  backlog tests

## Phase 5: Future capability evaluation

This phase evaluates advanced Kueue capabilities without making them phase 1
production promises.

### Deliverables

- Evaluation of topology-aware scheduling for MPI, JobSet, Ray, and GPU work
- Evaluation of advanced controller integrations such as `JobSet`, MPI, and Ray
- Evaluation of elastic workload applicability for CANFAR batch patterns
- Decision updates or new ADRs for supported future capabilities

### Key activities

- Test topology-aware scheduling against real node and fabric labels
- Test distributed workload semantics with `waitForPodsReady` where needed
- Evaluate whether elastic workloads help high-parallelism batch patterns
- Evaluate whether protected persistent or interactive workloads need stronger
  isolation than the initial single-plane model

### Dependencies

- Phase 4 evidence complete
- Access to representative GPU, network, and multi-pod job environments

### Acceptance criteria

- Each advanced capability has a documented fit, risk, and recommendation
- New workload classes are not promoted to production without measured evidence
- Any capability that remains unsuitable is documented clearly rather than left
  ambiguous

## Phase 6: Optional MultiKueue federation

This phase introduces manager and worker cluster federation only if the evidence
supports the need.

### Deliverables

- MultiKueue proof of concept
- Manager and worker flavor and queue mapping design
- Operational model for manager and worker observability and failure handling
- Migration criteria for deciding when to move from one cluster to many

### Key activities

- Define manager and worker queue vocabulary and synchronization rules
- Decide how worker clusters map to community ownership and specialized hardware
- Test manager visibility and worker execution state consistency
- Define site-placement and failure-domain policy

### Dependencies

- Phases 1 through 5 complete
- Evidence that single-cluster operation is insufficient or too risky

### Acceptance criteria

- The team has a documented reason to federate, not just a theoretical interest
- A MultiKueue proof of concept validates the community and project model
- Manager and worker failure handling is documented and testable

## Cross-phase risks

These risks apply across the whole roadmap:

- Users may interpret fair-share behavior as arbitrary if visibility lags behind
  policy rollout
- The control service may become the gating dependency for later phases if its
  requirements stay vague
- Namespace evolution may be forced earlier if workload-class policies diverge
  faster than expected
- Advanced features such as topology-aware scheduling or elastic workloads may
  reveal integration limits that require new ADRs

## Exit criteria for the package

The roadmap is complete when each phase can answer four questions:

- What is being delivered?
- What evidence proves it works?
- What dependencies and risks apply?
- What operator or user behavior changes when the phase lands?
