# Archived Helm charts

Charts in this directory are **no longer maintained or released** from [opencadc/deployments](https://github.com/opencadc/deployments). They are kept for historical reference and documentation snippets only.

Use the locations below for current chart source, values, and releases.

## Chart relocation guide

| Archived path | Chart name (Helm) | Current chart source | Published install (Helm repo) |
|---------------|-------------------|----------------------|-------------------------------|
| [`skaha/`](skaha/) | `skaha` | [`opencadc/science-platform`](https://github.com/opencadc/science-platform) — [`helm/`](https://github.com/opencadc/science-platform/tree/main/helm) | `science-platform/skaha` from `https://images.opencadc.org/chartrepo/platform` |
| [`science-portal/`](science-portal/) | `scienceportal` (legacy Tomcat / JSP UI) | **Superseded by** [`opencadc/science-portal`](https://github.com/opencadc/science-portal) — [`helm/`](https://github.com/opencadc/science-portal/tree/main/helm) (Next.js UI; chart name `science-portal`) | `science-platform/science-portal` from `https://images.opencadc.org/chartrepo/platform` |

### Skaha

- **Service & chart development:** [github.com/opencadc/science-platform](https://github.com/opencadc/science-platform)
- **Kueue examples** (ClusterQueue, LocalQueue, RBAC): [science-platform/helm/kueue/examples/](https://github.com/opencadc/science-platform/tree/main/helm/kueue/examples)
- **Deployment docs:** [Science Platform deployment guide](https://www.opencadc.org/deployments/helm/science-platform/deployment/) (Skaha install section)
- See also [`skaha/ARCHIVED.md`](skaha/ARCHIVED.md)

### Science Portal (legacy `scienceportal` chart)

The archived **`science-portal/`** directory is the **1.x Tomcat / JSP** chart (`scienceplatform/scienceportal`). New deployments should use the **Next.js** chart from `opencadc/science-portal`, not this copy.

- **Current chart source:** [github.com/opencadc/science-portal](https://github.com/opencadc/science-portal) (`helm/`)
- **Deployment docs:** [Science Portal](https://www.opencadc.org/deployments/helm/science-platform/science-portal/) and [deployment guide — Science Portal (Next.js)](https://www.opencadc.org/deployments/helm/science-platform/deployment/#science-portal-nextjs)
- **Legacy install only:** `science-platform/scienceportal` — documented under [Science Portal legacy](https://www.opencadc.org/deployments/helm/science-platform/deployment/#science-portal-legacy-jsp--tomcat)

## Related moves (not stored here)

| Former chart | Notes |
|--------------|--------|
| `base` | Obsolete for new installs. Traefik is installed separately; Skaha chart provides session RBAC. See [deployment guide — Base chart (obsolete)](https://www.opencadc.org/deployments/helm/science-platform/deployment/#base-chart-obsolete). Historical PV samples: [science-platform `deployment/helm/base/volumes`](https://github.com/opencadc/science-platform/tree/master/deployment/helm/base/volumes). |

## Do not

- Open release-please or publishing PRs against charts in this folder
- Treat these trees as the source of truth for new features or version bumps

For active charts still released from this repository, see the [chart inventory](../../../README.md#managed-charts) in the project README.
