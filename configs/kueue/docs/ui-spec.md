# CANFAR Kueue visibility and UI specification

This document defines the user-facing and admin-facing product surface for the
CANFAR Kueue architecture. It does not describe a finished implementation. It
defines the information model, workflows, and explanation language that the UI
must support.

Use this document together with [architecture.md](./architecture.md), [operations.md](./operations.md),
[roadmap.md](./roadmap.md), and [the ADR index](./adrs/README.md).

## 1. Product goals

The UI exists to make queue and ownership behavior understandable. It must not
become a generic Kubernetes portal. It must explain why work is pending, what
resources a community owns, and what position a project holds inside its
community.

The UI must support:

- science users who need workload status and explanation
- project admins who need project-level fairness and ownership visibility
- cluster admins who need policy, override, and incident visibility

## 2. Personas

This section defines the primary personas and what each one needs.

### 2.1 Science user

The science user needs to:

- submit work through `Skaha`
- see current workload state
- understand why work is pending
- distinguish priority delays from quota or capacity delays

The user does not need raw CRD editing or full Kubernetes visibility.

### 2.2 Project administrator

The project administrator needs to:

- see which projects exist in a community
- see which POSIX groups attach to a project
- understand project fair-share position and weight
- request temporary fair-share overrides through the control-service workflow

The project administrator does not approve overrides directly.

### 2.3 Cluster administrator

The cluster administrator needs to:

- inspect community ownership and borrow or reclaim behavior
- see and adjust project fair-share weights
- approve or reject temporary override requests
- diagnose fairness, preemption, and visibility problems

## 3. Primary views

This section defines the minimum view set the product must expose.

### 3.1 Queue explorer

The queue explorer is the main entry point for queue visibility. It must show:

- community
- project
- workload class
- current queue position where available
- effective fair-share state
- workload priority
- pending reason summary

### 3.2 Resource ownership view

The resource ownership view must show:

- which resources each community owns
- current usage against owned quota
- borrowing or lending state
- key `ResourceFlavor` breakdowns such as CPU, memory, GPU, cluster, and zone

This view is important for both project admins and cluster admins.

### 3.3 Project fairness view

The project fairness view must show:

- current fair-share weight
- recent effective usage
- relative position inside the community
- whether a temporary override is active
- who approved the override and when it expires

### 3.4 Workload detail view

The workload detail view must show:

- workload class
- priority class
- selected queue
- community and project identity
- active, pending, admitted, running, finished, or preempted state
- pending or preemption explanation using the standard reason language

## 4. Explanation language

The UI must use standard explanation categories so users see consistent,
actionable reasons rather than raw controller text.

### 4.1 Approved pending reasons

Use the following pending reason categories:

- Waiting behind other projects with better current fair-share position
- Waiting behind higher-priority work in the same project
- Waiting for community-owned or borrowed resources to become available
- Waiting because the project or policy does not currently allow admission
- Waiting because the platform control plane is degraded

### 4.2 Approved rejection or policy reasons

Use the following rejection categories:

- Project or community could not be resolved
- Submission is missing required queue or policy metadata
- Workload requests do not satisfy platform requirements
- External control-service policy denied the request

### 4.3 Approved preemption reasons

Use the following preemption categories:

- Preempted because the owning community reclaimed its quota
- Preempted by higher-priority work inside the same community
- Evicted because platform recovery policy triggered
- Evicted because queue stop or drain policy was applied

## 5. Workflows

This section defines the primary workflows the UI must support.

### 5.1 User workload inspection

The user inspects a workload and sees:

1. Which community and project it belongs to
2. Which queue it targets
3. Which workload class and priority apply
4. Why it is waiting or what preempted it
5. What the next likely action is

### 5.2 Project admin fairness inspection

The project admin inspects a project and sees:

1. Current fair-share weight
2. Current community-relative position
3. Current active and pending work counts
4. Whether an override exists or has expired
5. Which POSIX groups attach to the project

### 5.3 Temporary override request

The request flow is:

1. Project admin selects a project
2. Project admin proposes a temporary weight increase and business reason
3. Control-service workflow records the request
4. Cluster admin approves, rejects, or modifies the request
5. UI displays approval state and expiry time

The downstream accounting or quota-cost model for the override is out of scope
for this document, but the UI must display that such a cost model exists.

## 6. Phased product surface

The UI strategy is phased to match the roadmap.

### Phase 1

Use `kubectl`, Grafana, and the Kueue visibility API. No custom UI is required
yet beyond operator tooling.

### Phase 2

Introduce a read-only queue visibility UI with workload detail, project fairness
view, and community ownership view.

### Phase 3

Introduce admin workflows such as temporary override requests and richer project
and mapping inspection.

### Phase 4

Introduce guided submission hints, recommended queue or flavor explanations, and
self-service debugging aids if the earlier phases prove stable.

## 7. Data requirements

The UI needs data from multiple sources:

- Kueue visibility API for queue position and pending workloads
- Kueue metrics for quota, admission latency, and queue health
- Kubernetes workload state for current execution status
- Control-service metadata for projects, groups, ownership, and overrides

The UI must not depend on full raw workload listing for basic queue views when
the backlog is large.

## 8. Non-goals

This UI specification does not require:

- raw Kubernetes object editing
- a full generic cluster dashboard
- per-user accounting implementation
- automated override approval logic

The goal is clarity and policy transparency, not a complete platform portal.
