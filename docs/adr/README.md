# Architecture Decision Records (ADRs)

This folder records significant structural and process decisions for the deployments repository. ADRs complement normative specs (for example [`helm/SPECIFICATION.md`](../../helm/SPECIFICATION.md)) by capturing context, options considered, and consequences.

## Format

Each ADR is a markdown file:

```text
docs/adr/NNNN-short-title.md
```

Use the template sections: **Status**, **Context**, **Decision**, **Consequences**.

## Status values

| Status | Meaning |
| --- | --- |
| Proposed | Under discussion; not yet binding |
| Accepted | In effect; follow unless superseded |
| Superseded | Replaced by a later ADR (link to successor) |
| Deprecated | No longer recommended |

## Index

| ADR | Title |
| --- | --- |
| [0001](0001-helm-repository-directory-layout.md) | Helm repository directory layout |
| [0002](0002-umbrella-charts-for-related-systems-only.md) | Umbrella charts for related systems only |
| [0003](0003-deployment-domains-via-environment-overlays.md) | Deployment domains via environment overlays |

When adding an ADR, increment the number, update this index, and link from the relevant specification.
