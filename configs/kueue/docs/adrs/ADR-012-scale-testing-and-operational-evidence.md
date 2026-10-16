# ADR-012: Scale-testing and operational evidence

- Status: Accepted
- Date: March 12, 2026

## Context

The target system must support large pending backlog without relying on guesses
about safe operating thresholds. Kueue behavior, Kubernetes API behavior, and
the submission path must be measured together.

## Decision

Use benchmark-driven operational evidence as a release gate. `kueuer`,
Prometheus, Grafana, and controlled workload storms are required parts of the
platform rollout, not optional afterthoughts.

The evidence model must include:

- scale gates at increasing backlog levels
- workload admission timing and throughput
- controller health and restart behavior
- API server latency and saturation
- visibility API behavior under backlog
- user-path latency through `skaha`

## Consequences

The platform gets explicit stop or go thresholds for production change rather
than relying on anecdotal experience.

This also means roadmap phases need objective exit criteria and repeatable test
artifacts.

## Alternatives considered

- Tune Kueue and trust best effort observations
- Measure only Kueue controller metrics

These alternatives fail to prove end-to-end system behavior under realistic
submission pressure.
