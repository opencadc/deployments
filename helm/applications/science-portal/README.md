# science-portal

A Helm chart for the CANFAR Next.js Science Portal application

## Configuration

This chart treats [canfar/science-portal `.env.example`](https://github.com/canfar/science-portal/blob/main/.env.example) as **application configuration**: semantic fields under **`app`** (API URLs, auth mode, OIDC, NextAuth) are mapped to the container **`env`** names the Node process reads. **Environment variables are the transport**, not the source of truth in your values file.

- **`app`**: structured settings (including **`app.oidc`** for OIDC pairs). Empty or unset fields emit nothing so image defaults apply where appropriate.
- **`env`**: append native Kubernetes `env` entries; merged **after** chart-generated entries. If a name appears in **`env`**, the chart **does not** emit that name from `app` (so you can override or supply secrets with `valueFrom`).
- **`envFrom`**: optional Secret/ConfigMap injection unchanged.

Many **`NEXT_PUBLIC_*`** values are fixed at **image build**; runtime env from Helm mainly affects server-side behavior unless your image is built to honor overrides.

**Upgrade (chart 2.1+):** rename **`app.publicApi`** to **`app.public.api`** (same child keys). Overlays that still set `app.publicApi` continue to work: the chart merges it with `app.public.api`, and **`app.public.api` wins** on conflicts. Use **`app.public.services`** for the six **`NEXT_PUBLIC_SERVICE_*`** navigation URLs added in [science-portal eca70d9](https://github.com/canfar/science-portal/commit/eca70d91f45fe6578207c7bd70e67b91d2654700).

| Chart | AppVersion | Type |
|:-----:|:----------:|:----:|
|2.0.0<!-- x-release-please-version --> | eca70d91f45fe6578207c7bd70e67b91d2654700 | application |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| app | object | `{"api":{"login":"","skaha":"","srcCavern":"","srcSkaha":"","storage":"","timeoutMs":""},"auth":{"authSecret":{"existingSecret":"","secretKey":""},"nextauthUrl":""},"basePath":"","oidc":{"callbackUri":"","clientId":"","clientSecret":{"existingSecret":"","secretKey":""},"enabled":false,"redirectUri":"","scope":"","uri":""},"public":{"api":{"login":"","skaha":"","srcCavern":"","srcSkaha":"","timeoutMs":""},"services":{"cadcSearch":"","dataPublication":"","groupManagement":"","openstackCloud":"","sciencePortal":"","storageManagement":""}}}` | Product / application settings mapped to container env. Prefer over raw `env` for options from [upstream .env.example](https://github.com/canfar/science-portal/blob/main/.env.example). Many `NEXT_PUBLIC_*` values are fixed at **image build**; runtime env here mainly affects the server unless your image supports overrides. **app.api** — server-side (`SERVICE_*`, `LOGIN_API`, …). **app.public** — browser `NEXT_PUBLIC_*`: **public.api** maps to client API bases; **public.services** maps to Services menu / footer links ([eca70d9](https://github.com/canfar/science-portal/commit/eca70d91f45fe6578207c7bd70e67b91d2654700)). If you still use deprecated **app.publicApi** in overlays, it is merged with **public.api** and **public.api** wins on conflicts. |
| app.api | object | `{"login":"","skaha":"","srcCavern":"","srcSkaha":"","storage":"","timeoutMs":""}` | Server-side API URLs (`SERVICE_STORAGE_API`, `LOGIN_API`, `SKAHA_API`, `SRC_*`, `API_TIMEOUT`). Empty keys are omitted. |
| app.auth | object | `{"authSecret":{"existingSecret":"","secretKey":""},"nextauthUrl":""}` | NextAuth (`AUTH_TRUST_HOST`, `NEXTAUTH_URL`, optional `AUTH_SECRET` from Secret refs). |
| app.basePath | string | `""` | URL path prefix; must match `NEXT_PUBLIC_BASE_PATH` in the image. When non-empty, sets env `NEXT_PUBLIC_BASE_PATH`. HTTP probes hit this path (or /science-portal when empty). |
| app.oidc | object | `{"callbackUri":"","clientId":"","clientSecret":{"existingSecret":"","secretKey":""},"enabled":false,"redirectUri":"","scope":"","uri":""}` | OIDC settings. When `enabled` and `uri` are set, emits paired NEXT_OIDC_* / NEXT_PUBLIC_OIDC_* env vars. Use with useCanfar: false. Client secret via existingSecret + secretKey only. |
| app.public | object | `{"api":{"login":"","skaha":"","srcCavern":"","srcSkaha":"","timeoutMs":""},"services":{"cadcSearch":"","dataPublication":"","groupManagement":"","openstackCloud":"","sciencePortal":"","storageManagement":""}}` | Browser-facing `NEXT_PUBLIC_*` settings (runtime overrides when the image supports them). |
| app.public.api | object | `{"login":"","skaha":"","srcCavern":"","srcSkaha":"","timeoutMs":""}` | Client-side API bases (`NEXT_PUBLIC_*_API`, `NEXT_PUBLIC_API_TIMEOUT`). Empty keys are omitted. |
| app.public.services | object | `{"cadcSearch":"","dataPublication":"","groupManagement":"","openstackCloud":"","sciencePortal":"","storageManagement":""}` | Services menu / footer links (`NEXT_PUBLIC_SERVICE_*`). Empty keys are omitted. Requires an image built from eca70d9 or later. |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| env | list | `[]` | Extra container `env` entries (Kubernetes native). Merged **after** chart-generated env from `app`. If a variable name appears here, the chart **skips** emitting that name from `app` (no duplicate keys). Use for secrets and overrides. |
| envFrom | list | `[]` | Optional `envFrom` (Secret/ConfigMap refs). |
| fullnameOverride | string | `""` |  |
| httpRoute.annotations | object | `{}` |  |
| httpRoute.enabled | bool | `false` |  |
| httpRoute.hostnames[0] | string | `"science-portal.example.local"` |  |
| httpRoute.parentRefs[0].name | string | `"gateway"` |  |
| httpRoute.parentRefs[0].sectionName | string | `"http"` |  |
| httpRoute.rules[0].matches[0].path.type | string | `"PathPrefix"` |  |
| httpRoute.rules[0].matches[0].path.value | string | `"/"` |  |
| image | object | `{"pullPolicy":"IfNotPresent","repository":"ghcr.io/canfar/science-portal","tag":"eca70d91f45fe6578207c7bd70e67b91d2654700"}` | Container image (repository and tag). |
| imagePullSecrets | list | `[]` |  |
| ingress.annotations | object | `{}` |  |
| ingress.className | string | `""` |  |
| ingress.enabled | bool | `false` |  |
| ingress.hosts[0].host | string | `"science-portal.example.local"` |  |
| ingress.hosts[0].paths[0].path | string | `"/"` |  |
| ingress.hosts[0].paths[0].pathType | string | `"Prefix"` |  |
| ingress.tls | list | `[]` |  |
| livenessProbe.failureThreshold | int | `3` |  |
| livenessProbe.httpGet.port | string | `"http"` |  |
| livenessProbe.initialDelaySeconds | int | `10` |  |
| livenessProbe.periodSeconds | int | `10` |  |
| livenessProbe.timeoutSeconds | int | `3` |  |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` |  |
| podAnnotations | object | `{}` |  |
| podLabels | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| readinessProbe.failureThreshold | int | `3` |  |
| readinessProbe.httpGet.port | string | `"http"` |  |
| readinessProbe.initialDelaySeconds | int | `5` |  |
| readinessProbe.periodSeconds | int | `5` |  |
| readinessProbe.timeoutSeconds | int | `3` |  |
| replicaCount | int | `1` |  |
| resources | object | `{}` |  |
| securityContext | object | `{}` |  |
| service.port | int | `3000` |  |
| service.type | string | `"ClusterIP"` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.automount | bool | `true` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` |  |
| startupProbe.failureThreshold | int | `30` |  |
| startupProbe.httpGet.port | string | `"http"` |  |
| startupProbe.periodSeconds | int | `10` |  |
| startupProbe.timeoutSeconds | int | `3` |  |
| tolerations | list | `[]` |  |
| volumeMounts | list | `[]` |  |
| volumes | list | `[]` |  |
