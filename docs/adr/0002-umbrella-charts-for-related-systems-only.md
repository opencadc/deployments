# ADR 0002: Umbrella charts for related systems only

- **Status:** Accepted
- **Date:** 2026-10-22
- **Deciders:** CADC deployments maintainers

## Context

Helm umbrella charts bundle multiple subcharts into one release. They simplify installing a known set of components but tie version upgrades, rollbacks, and failure domains together.

Some chart groups in this repository are intentional products (for example the SC2 sandbox stack). Other services share operational context—same cluster or public domain—but are unrelated products with independent lifecycles.

## Decision

1. Place umbrella charts only under **`helm/stacks/<system>/<stack-name>/`**.
2. Use an umbrella when operators **routinely** install a **defined set** of subcharts together and want one Helm release to manage that set.
3. **Do not** create umbrella charts because services share:
   - a public DNS domain,
   - an ingress controller or gateway,
   - a namespace naming convention, or
   - the same operations team.

Unrelated co-located services are installed as **separate releases** (separate `helm upgrade --install` or separate GitOps applications), optionally sharing value files from `helm/environments/`.

System folders under `charts/<system>/` are for ownership and discovery only; they do not imply a stack chart.

## Consequences

**Positive**

- Independent semver and release cadence per service (for example ac, cred, reg).
- Smaller blast radius on upgrade and rollback.
- Stack charts remain meaningful (sandbox stack, future platform stacks).

**Negative**

- More releases to manage where a single umbrella might feel convenient for one-shot demos.
- Shared ingress or gateway configuration may be duplicated in environment overlays unless factored into `_common.yaml` or `global` values.

## Example

The SC2 sandbox **`stack`** chart composes bifrost, sc2meta, torkeep, search, and argus—an Accepted umbrella.

**ac**, **cred**, and **reg** on the same domain are **not** composed into a `cadc-site` umbrella; each chart is released and installed independently.
