# ADR-007: ResourceFlavor taxonomy and topology model

- Status: Accepted
- Date: March 12, 2026

## Context

CANFAR needs a flavor model that captures resource identity across cluster,
zone, accelerator type, storage class, and later topology-aware scheduling
domains. The model must stay readable to operators and extensible to future
MultiKueue deployments.

## Decision

Use `ResourceFlavor` as the canonical scheduler-facing identity for placement and
hardware classes. Standardize flavor naming around stable placement and hardware
dimensions rather than workload class.

Adopt the following naming pattern:

`rf-<cluster>-<zone>-<resource-class>[-<accelerator-class>]`

Examples:

- `rf-ca-west-01-cpu-standard`
- `rf-ca-west-01-cpu-highmem`
- `rf-ca-west-01-gpu-a100`

Treat topology-aware scheduling as a future phase. When topology becomes active,
use `Topology` objects and flavor association rather than encoding full topology
hierarchy into the flavor name itself.

## Consequences

Operators get a stable taxonomy that works in both single-cluster and future
manager-worker designs. Users and admins can also read flavor identity in a
predictable way.

## Alternatives considered

- Opaque flavor names with documentation-only meaning
- One flavor per workload class
- Encoding every topology dimension directly in the flavor name

These alternatives either hide meaning or create unnecessary flavor sprawl.
