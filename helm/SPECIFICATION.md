# Helm charts repository specification

This document defines how Helm charts are organized in the [opencadc/deployments](https://github.com/opencadc/deployments) repository: directory layout, naming, dependencies, environment overlays, and how charts imported from service repositories are placed here.

**Status:** Normative for new and migrated charts. Existing paths under `helm/applications/` remain valid until moved; new work should follow this specification.

**Decisions:** Rationale for major choices is recorded as Architecture Decision Records (ADRs) under [`docs/adr/`](../docs/adr/README.md).

---

## Goals

- Keep related charts easy to find while avoiding false coupling between independent services.
- Support multiple **systems** (product lines, sandboxes, platforms) and multiple **deployment domains** (hostnames, clusters, environments).
- Allow a **library chart** for shared templates without deploying it on its own.
- Support **umbrella (stack) charts** only where operators intentionally install a fixed set of subcharts as one release.
- Preserve **independent versioning and OCI publication** per chart (Release Please, Sigstore signing).

---

## Top-level layout

```text
helm/
├── SPECIFICATION.md          # this document
├── README.md                 # entry point for chart authors
├── library/                  # library charts (type: library), never installed alone
│   └── utils/
├── charts/                   # application charts (type: application)
│   ├── <chart-name>/         # independent services (flat)
│   ├── <system>/             # related services grouped by system
│   │   ├── <chart-name>/
│   │   └── archived/
│   └── archived/             # optional global graveyard
├── stacks/                   # umbrella charts only
│   └── <system>/
│       └── <stack-name>/
└── environments/             # optional: domain/cluster value overlays (no templates)
    └── <domain-or-env>/
        ├── _common.yaml
        └── <chart-name>.yaml
```

### Layer responsibilities

| Layer | Purpose | Deployed? |
| --- | --- | --- |
| `library/` | Shared helpers, partials, standard labels, ingress/HTTPRoute patterns | No |
| `charts/` | One chart per installable application or infrastructure component | Yes (standalone release) |
| `stacks/` | Compose subcharts via `dependencies`; wiring and shared stack-level values | Yes (single release) |
| `environments/` | Hostnames, TLS, LDAP/OIDC endpoints, replicas, feature flags for a target | No (values only) |

---

## When to use flat charts vs system folders

### Flat: `helm/charts/<chart-name>/`

Use when the chart is **independently owned, versioned, and released**, even if it shares a public domain with other charts.

**Example:** [ac](https://github.com/opencadc/ac/tree/main/ac/helm), [cred](https://github.com/at88mph/cdp/tree/main/cred/helm), and [reg](https://github.com/opencadc/reg/tree/main/reg/helm) deploy on the same site but are unrelated products. They live as siblings:

```text
helm/charts/ac/
helm/charts/cred/
helm/charts/reg/
```

Domain-specific settings (ingress hosts, LDAP, `application.serviceEntries`, secret references) belong in `helm/environments/<domain>/`, not in a parent folder or umbrella chart. See [ADR 0003](../docs/adr/0003-deployment-domains-via-environment-overlays.md).

### System folder: `helm/charts/<system>/<chart-name>/`

Use when charts are **developed, reviewed, and often upgraded together** as one logical system.

**Example:** SC2 sandbox components (`argus`, `bifrost`, `torkeep`, …) under `helm/charts/sandbox/`, with an optional umbrella at `helm/stacks/sandbox/stack/`.

**Example:** CANFAR Science Platform services under `helm/charts/science-platform/` (or equivalent name).

A system folder is **navigation and ownership**, not a Helm dependency. Subcharts do not automatically depend on each other unless declared in a stack chart or explicit `Chart.yaml` dependencies.

---

## Umbrella (stack) charts

- Location: `helm/stacks/<system>/<stack-name>/`.
- `type: application` in `Chart.yaml`; lists subcharts under `dependencies`.
- Subchart paths in a monorepo use `repository: "file://../../charts/<system>/<chart-name>"` (adjust depth as needed).
- Production installs may resolve the same versions from OCI (`oci://images.opencadc.org/platform/charts/...`).

**Do not** create an umbrella chart merely because services share a domain or ingress. See [ADR 0002](../docs/adr/0002-umbrella-charts-for-related-systems-only.md).

Stack `values.yaml` should contain:

- Composition (which subcharts are enabled, aliases).
- Shared infrastructure (gateway parent refs, common annotations).
- Not duplicate defaults that belong in subchart `values.yaml`.

---

## Library chart

- Location: `helm/library/utils/` (successor to `helm/applications/utils/`).
- `type: library` in `Chart.yaml`.
- Application charts add a dependency when shared templates reduce duplication (ingress, configmap patterns, labels).

```yaml
dependencies:
  - name: utils
    version: "0.x.x"
    repository: "file://../../library/utils"   # monorepo dev
    # repository: oci://images.opencadc.org/platform/charts/utils   # published
```

Library charts are versioned and published like application charts but are not installable with `helm install`.

---

## Importing charts from service repositories

Service repos often ship charts at `<module>/helm/`. When converging into this repository:

1. **Destination path**
   - Independent service → `helm/charts/<chart-name>/` (chart `name` in `Chart.yaml` matches directory name).
   - Part of a known system → `helm/charts/<system>/<chart-name>/`.
2. **Flatten** the tree: copy chart root contents only (do not preserve `ac/ac/helm` nesting in deployments).
3. **Provenance** (recommended annotation in `Chart.yaml`):

   ```yaml
   annotations:
     opencadc.org/source-repo: "opencadc/ac"
     opencadc.org/source-path: "ac/helm"
   ```

4. **Release Please:** add one manifest entry per chart path (e.g. `helm/charts/ac`).
5. **Secrets:** never commit credentials; document required Kubernetes Secrets in chart `README.md` (as upstream does for ac LDAP/OIDC).
6. **Renovate:** keep the `# renovate: image=...` comment before `appVersion` where applicable.

---

## Deployment domains and environments

**Deployment domain** means the operational target: cluster, public hostname(s), TLS, and identity backends—not a Helm chart grouping.

- Chart templates and default `values.yaml` stay **domain-agnostic** where possible.
- Use `global.*` for cross-chart conventions within a single release (stacks) or duplicate small shared snippets in per-chart env files for standalone releases.
- Store overlays under `helm/environments/<name>/`:
  - `_common.yaml` — shared ingress class, `baseDomain`, gateway references.
  - `<chart-name>.yaml` — chart-specific required config.

Install pattern (standalone):

```bash
helm upgrade --install reg oci://images.opencadc.org/platform/charts/reg:1.2.0 \
  -f helm/environments/canfar-prod/_common.yaml \
  -f helm/environments/canfar-prod/reg.yaml \
  --namespace reg --create-namespace
```

Environment files may also live in a separate GitOps repository; this repo’s `helm/environments/` is the reference layout when overlays are co-located with charts.

---

## Archived charts

Retired charts move to:

- `helm/charts/archived/<chart-name>/`, or
- `helm/charts/<system>/archived/<chart-name>/`.

Keep a short `ARCHIVED.md` (reason, replacement, last supported version). Remain in Release Please only if artifacts must still be published for rollback.

---

## Documentation mirror

Operator-facing runbooks live under `docs/helm/` and should mirror chart grouping:

- `docs/helm/science-platform/` — platform charts.
- `docs/helm/core/` — cross-cutting public services (e.g. reg, ac, cred).
- Per-chart pages linked from section index files.

Chart authors maintain **technical** `README.md` inside the chart (values table, secrets, `helm test`). The specification does not replace per-chart READMEs.

---

## Naming and metadata conventions

| Item | Rule |
| --- | --- |
| Chart name | Stable, matches OCI artifact name (`reg`, `ac`, `cavern`) |
| Directory | Same as chart `name` unless nested under `<system>/` |
| Stack name | Descriptive (`stack`, `science-platform`) under `stacks/<system>/` |
| Values keys | Subchart keys in stack values match dependency `name` or `alias` |
| `appVersion` | Container / application version; aligned with image tag where applicable |

---

## Migration from `helm/applications/`

Current repository layout uses `helm/applications/` (including `sandbox/`, `archived/`, and library `utils`). Target layout:

| Current | Target |
| --- | --- |
| `helm/applications/utils` | `helm/library/utils` |
| `helm/applications/<service>` | `helm/charts/<service>` or `helm/charts/science-platform/<service>` |
| `helm/applications/sandbox/*` | `helm/charts/sandbox/*` |
| `helm/applications/sandbox/stack` | `helm/stacks/sandbox/stack` |
| `helm/applications/archived/*` | `helm/charts/archived/*` or per-system `archived/` |

Update `.release-please-manifest.json`, CI publish paths, and README inventory when each chart moves. Moves may be incremental.

---

## Related documents

| Document | Description |
| --- | --- |
| [ADR 0001](../docs/adr/0001-helm-repository-directory-layout.md) | Directory layout (`library`, `charts`, `stacks`, `environments`) |
| [ADR 0002](../docs/adr/0002-umbrella-charts-for-related-systems-only.md) | When to use stack charts |
| [ADR 0003](../docs/adr/0003-deployment-domains-via-environment-overlays.md) | Domains vs chart grouping (ac, cred, reg) |
| [Repository README](../README.md) | Release, signing, adding a new chart |
| [docs/helm/index.md](../docs/helm/index.md) | Published operator documentation |
