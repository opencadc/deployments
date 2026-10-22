# ADR 0003: Deployment domains via environment overlays

- **Status:** Accepted
- **Date:** 2026-10-22
- **Deciders:** CADC deployments maintainers

## Context

Charts deploy to different domains (hostnames, TLS certificates, LDAP/OIDC endpoints, registry entries). It is tempting to group charts in the filesystem by “where they run.” That conflates **product boundaries** with **deployment targets**.

Initial imports include three independent services that often run on the same public site:

| Chart | Source | Role |
| --- | --- | --- |
| `ac` | [opencadc/ac `ac/helm`](https://github.com/opencadc/ac/tree/main/ac/helm) | Access control and group management |
| `cred` | [at88mph/cdp `cred/helm`](https://github.com/at88mph/cdp/tree/main/cred/helm) | Credentials service |
| `reg` | [opencadc/reg `reg/helm`](https://github.com/opencadc/reg/tree/main/reg/helm) | IVOA Registry |

They share no Helm dependency graph; only deployment context overlaps.

## Decision

1. Model **deployment domain** with **environment value overlays**, not with chart directory parents or umbrella charts.
2. Store overlays under **`helm/environments/<domain-or-env>/`** when co-located in this repo:
   - `_common.yaml` for shared ingress, gateway, or `global.baseDomain`.
   - `<chart-name>.yaml` for required per-service config (LDAP, OIDC clients, `application.serviceEntries`, secret references).
3. Place independent services at **`helm/charts/<chart-name>/`** (flat), even when always deployed to the same domain.
4. Document the set of releases expected on a domain in **`docs/helm/`** (for example Core Services), not by merging charts in Git.

Overlays may alternatively live in an external GitOps repository; the path convention remains the reference.

## Consequences

**Positive**

- Chart templates stay reusable across dev, staging, and production.
- Same chart version can ship to multiple domains with different value files.
- Matches upstream chart documentation (values + secrets created out-of-band).

**Negative**

- Operators maintain multiple value files per domain instead of one monolithic stack values file.
- `_common.yaml` conventions must be documented and kept consistent across teams.

## Install illustration

```bash
helm upgrade --install ac oci://images.opencadc.org/platform/charts/ac:0.1.0 \
  -f helm/environments/example-org/_common.yaml \
  -f helm/environments/example-org/ac.yaml \
  --namespace ac --create-namespace
```

Repeat for `cred` and `reg` with their respective overlay files—three releases, one domain.
