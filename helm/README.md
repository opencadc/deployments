# Helm charts

Kubernetes deployment charts for CADC and CANFAR services, published as versioned OCI artifacts with automated releases.

**Authors and maintainers:** read the normative layout and conventions in [SPECIFICATION.md](SPECIFICATION.md).

**Operators:** see the [Helm charts documentation](../docs/helm/index.md) on the docs site for runbooks and per-service guides.

## Quick reference

```text
helm/library/       # shared library charts (common)
helm/charts/        # application charts
helm/stacks/        # umbrella charts for intentional multi-chart releases
helm/environments/  # optional domain/cluster value overlays
```

Architecture decisions that explain *why* the layout looks this way are in [`docs/adr/`](../docs/adr/README.md).
