# ADR 0001: Helm repository directory layout

- **Status:** Accepted
- **Date:** 2026-10-22
- **Deciders:** CADC deployments maintainers

## Context

Helm charts for many different systems lived in multiple service repositories and in this repo under a flat `helm/applications/` tree (with ad hoc `sandbox/` and `archived/` folders). We need a converged layout that:

- Scales to many systems and imported charts.
- Supports a shared library chart.
- Supports umbrella stacks where appropriate.
- Stays compatible with independent Release Please versioning and OCI publication per chart.

The root README referenced `helm/common/` while the library chart lived at `helm/applications/utils`, which caused confusion.

## Decision

Adopt a four-layer layout under `helm/`:

1. **`library/`** — Helm library charts (`type: library`), not deployable alone.
2. **`charts/`** — Application charts; either flat (`charts/<name>/`) or grouped by system (`charts/<system>/<name>/`).
3. **`stacks/`** — Umbrella charts that declare subchart dependencies.
4. **`environments/`** — Optional value overlays for deployment targets (no templates).

Normative details live in [`helm/SPECIFICATION.md`](../../helm/SPECIFICATION.md).

Existing `helm/applications/` paths remain until migrated incrementally; new charts and imports follow the new layout.

## Consequences

**Positive**

- Clear separation between deployable charts, composition (stacks), shared templates (library), and environment-specific values.
- Imported service-repo charts map to a predictable path (`charts/<name>/` or `charts/<system>/<name>/`).
- Library chart has a single home (`library/utils`), aligned with documentation.

**Negative**

- Dual layout during migration requires updating Release Please paths, CI, and docs as charts move.
- Deeper paths change relative `file://` dependency URLs in stack charts (one-time fix per stack).

**Neutral**

- Operator runbooks stay under `docs/helm/`; ADRs and `helm/SPECIFICATION.md` target maintainers and chart authors.
