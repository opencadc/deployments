# Kueue capabilities deep dive

This document provides a practical, operator-focused overview of Kueue
capabilities relevant to `kueuer` benchmarking and platform rollout decisions.

## Kueue system role

Kueue is a Kubernetes-native admission and quota orchestration system for batch
workloads. Kueue does not replace the Kubernetes scheduler. Instead, it controls
when workloads are admitted, using queueing policies and quota rules.

## core resource model

Kueue behavior is built from the following resource types.

1. `ResourceFlavor`: Defines placement and flavor-level resource identity.
2. `ClusterQueue`: Defines quota, borrowing/lending behavior, queueing strategy,
   and preemption policy.
3. `LocalQueue`: Namespace-level queue that maps workloads to a ClusterQueue.
4. `WorkloadPriorityClass`: Defines workload priority for Kueue decisions.
5. `Workload`: Internal admission object that tracks reservation, admission,
   condition state, and lifecycle transitions.

## lifecycle model relevant to benchmarking

For benchmarking and diagnosis, the workload lifecycle is the most important
mental model.

1. Workload is created and enters queueing flow.
2. Quota is evaluated and reserved when possible.
3. Workload is admitted when reservation and admission checks are satisfied.
4. Job runs under Kubernetes scheduling and runtime behavior.
5. Workload reaches finished state or is evicted and possibly requeued.

For preemption, Kueue records eviction and preemption context in workload
conditions, including reason and related workload identifiers.

## queueing and fairness

Kueue supports queueing strategies such as FIFO variants and can share quota
across queues using cohorts. Queue behavior can include:

- nominal quota
- borrowing and lending limits
- preemption policies within queue and across cohort
- fair sharing models (when configured)

These mechanisms are critical for multi-tenant batch systems where workloads
compete for finite resources.

## observability surfaces

Kueue exposes Prometheus-style metrics for queue health, admission timing, and
eviction reason counts. Depending on feature gates and configuration, operators
can monitor:

- pending workload states (active versus inadmissible)
- quota reservation wait timing
- admission check wait timing
- eviction counts and reasons
- queue resource quota and usage metrics

## implications for platform rollout

For production readiness, you must validate both policy correctness and control
plane stability.

1. Policy correctness means workloads follow intended queue, quota, and priority
   behavior.
2. Stability means Kubernetes API latency and Kueue controller resource usage
   remain bounded under load.

`kueuer` is intended to provide benchmark evidence for both areas. Phase 1
focuses on data correctness of `kueuer` itself. Later phases add richer
observability and stronger scale conclusions.

## relationship to this repository

This repository includes:

- `dev/` and `prod/` Kueue deployment and queue configuration.
- `kueuer/` benchmark tooling for performance and eviction analysis.
- local Kueue docs and examples under `kueue-docs/` used as source material for
  behavior semantics and configuration guidance.

Use this deep dive together with `docs/kueuer/*.md` to onboard new developers
and operators into repeatable benchmark-driven Kueue evaluation.
