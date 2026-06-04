# Science Portal Helm Chart

The Science Portal is the web dashboard where users start and monitor interactive sessions (notebooks, CARTA, terminals, and similar workloads managed by Skaha).

## New vs legacy chart

| | **science-portal** (recommended) | **science-portal legacy** (`scienceportal`) |
|---|----------------------------------|---------------------------------------------|
| Helm chart name | `science-portal` | `scienceportal` |
| Application | Next.js (Node.js) | Java web app on Apache Tomcat |
| UI technology | Modern React pages rendered by Next.js | Older server-generated JSP pages |
| Configuration | Structured `app` block in values (maps to env vars) | `deployment.sciencePortal` + Tomcat ConfigMap |
| Default image | `images.opencadc.org/platform/science-portal` (Node, port 3000) | `images.opencadc.org/platform/science-portal:1.4.0` (Tomcat, port 8080) |
| Chart source | [`opencadc/science-portal`](https://github.com/opencadc/science-portal) [`helm/`](https://github.com/opencadc/science-portal/tree/main/helm) | [archived chart](../../../helm/applications/archived/science-portal/) in this repo |

In plain terms: the **new** portal is a current-style website (fast page loads, React UI, Next.js server). The **legacy** portal is the older Java/Tomcat stack that builds each page on the server with JSP—still supported for existing deployments, but new installs should use `science-portal`.

!!! note "Chart source"

    The Helm chart source is in [`opencadc/science-portal`](https://github.com/opencadc/science-portal) under [`helm/`](https://github.com/opencadc/science-portal/tree/main/helm). Releases are consumed as `science-platform/science-portal` from the platform chart repository.

Step-by-step install instructions, a full example values file, and the legacy chart are documented in the [Deployment Guide](deployment.md#science-portal-nextjs).

## Dependencies

- Kubernetes 1.29+.
- [Skaha](skaha.md) deployed and registered in the IVOA Registry (the portal calls the Skaha API).
- For OpenID Connect login: a registered OIDC client and Kubernetes Secret for the client secret and NextAuth signing key (see deployment guide).
- Traefik installed per the [deployment guide](deployment.md#traefik-install) (`IngressRoute` / `Middleware` for sessions; `Ingress` for this chart).

## Install

```bash
helm repo add science-platform https://images.opencadc.org/chartrepo/platform
helm repo update

helm upgrade --install -n skaha-system \
  --values my-science-portal-local-values-file.yaml \
  science-portal science-platform/science-portal
```

Use the [example values](deployment.md#example-values-file) in the deployment guide as a starting point.

## Endpoints

With the default path prefix, the UI is served at `/science-portal` (for example `https://example.host.com/science-portal`). OIDC redirect URIs typically use `/science-portal/api/auth/callback/...` depending on auth mode; align these with your IdP registration and `app.oidc` / `app.auth` settings.

## Authentication

Browser login uses OpenID Connect (authorization code flow) or CANFAR credentials, depending on how the container image was built. Sessions are handled with NextAuth on the server (BFF-style), not by storing API tokens in browser local storage. See [Browser Authentication](browser-authentication.md) and the upstream [authentication modes guide](https://github.com/opencadc/science-portal/blob/main/helm/DEPLOYMENT-MODES.md).

## Configuration reference

The chart maps the structured `app` section in values to container environment variables (see [`.env.example`](https://github.com/opencadc/science-portal/blob/main/.env.example)). Many `NEXT_PUBLIC_*` settings are fixed at **image build** time; runtime Helm values mainly affect server-side URLs, OIDC, and NextAuth.

The generated values table and chart options are maintained in the service repository (not copied into this docs site):

- [Helm chart README](https://github.com/opencadc/science-portal/blob/main/helm/README.md) — full `values.yaml` reference
- [Default `values.yaml`](https://github.com/opencadc/science-portal/blob/main/helm/values.yaml) — starting point for overlays
- [Helm chart directory](https://github.com/opencadc/science-portal/tree/main/helm) — templates and deployment guides (`DEPLOYMENT-MODES.md`, and others)

## Legacy chart

To install the JSP/Tomcat chart (`science-platform/scienceportal`), see [Science Portal legacy](deployment.md#science-portal-legacy-jsp--tomcat) in the deployment guide.
