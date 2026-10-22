# reg

IVOA Registry Service Helm Chart

| Chart | AppVersion | Type |
|:-----:|:----------:|:----:|
|1.2.0<!-- x-release-please-version --> | 1.2.1 | application |

## Overview

This Helm chart deploys the **reg** IVOA Registry Service on Kubernetes.

The chart runs the application built from the [`reg/`](../reg/) directory in this repository — the deployable WAR, Docker image, and runtime configuration described in [`reg/README.md`](../reg/README.md). Other modules in the repository (`cadc-registry`, `cadc-vosi`, and so on) are libraries consumed by that application; this chart does not deploy them separately.

The default container image is `images.opencadc.org/core/reg`, with tag matching the chart `appVersion` (aligned with [`reg/VERSION`](../reg/VERSION)).

## Install

From the repository root:

```bash
helm install my-reg ./helm -f my-values.yaml
```

`application.serviceEntries` is required. A minimal values file:

```yaml
application:
  serviceEntries:
    - id: "ivo://example.org/reg"
      url: "https://example.org/my-service/capabilities"
```

## Configuration

The chart renders a ConfigMap mounted at `/config` in the container. That produces the property files documented in [`reg/README.md`](../reg/README.md):

| ConfigMap key | Purpose |
|---------------|---------|
| `catalina.properties` | Tomcat and proxy settings (`tomcat.connector.*`) |
| `reg-resource-caps.properties` | VOSI-enabled API entries (from `application.serviceEntries`) |
| `reg-applications.properties` | Web application entries (from `application.applicationEntries`, optional) |
| `cadc-log.properties` | Dynamic logging control (optional) |

### Application settings (`application.*`)

- **`application.serviceEntries`** (required): list of `{ id, url }` pairs for VOSI-enabled APIs (web services). Rendered into `reg-resource-caps.properties` ([reg-resource-caps.properties](https://github.com/opencadc/reg/tree/main/reg#reg-resource-capsproperties-optional)).
- **`application.logging`**: users, groups, or DNs granted enhanced logging.
- **`application.applicationEntries`**: optional web application (user interface) feature ID to URL mappings ([reg-applications.properties](https://github.com/opencadc/reg/tree/main/reg#reg-applicationsproperites-optional-experimental)).

### Public URL (`tomcat.connector`)

When the service sits behind a reverse proxy, Tomcat needs the public URL clients use (equivalent to `X-Forwarded-Proto`, `X-Forwarded-Host`, and `X-Forwarded-Port`). These values are written to `catalina.properties` as `tomcat.connector.*` and affect VOSI capabilities output: `accessURL` hostnames are rewritten to match the request URL.

Resolution order for each field:

1. Explicit value in `tomcat.connector`
2. Auto-derived from `httpRoute` (if enabled) or `ingress` (if enabled)
3. Omitted when `proxyName` cannot be resolved

**Internal-only deployment (defaults):** with `ingress.enabled=false`, `httpRoute.enabled=false`, `service.type=ClusterIP`, and empty `tomcat.connector` fields, no `tomcat.connector.*` properties are emitted. The service stays ClusterIP-only (reachable by Pods in the cluster) and Tomcat uses each incoming request URL as-is.

Set `tomcat.connector` explicitly when the public URL differs from the ingress or HTTPRoute hostname — for example, when a CDN or external load balancer sits in front of the cluster.

### Service exposure

| Mechanism | Values key | Default |
|-----------|------------|---------|
| In-cluster only | `service.type: ClusterIP` | yes |
| Ingress | `ingress.enabled` | `false` |
| Gateway API HTTPRoute | `httpRoute.enabled` | `false` |

When ingress or HTTPRoute is enabled and `tomcat.connector` fields are left empty, the public URL is derived from the configured hostnames.

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| application.logging | string | `nil` |  |
| application.applicationEntries | list | `[]` | Web application (user interface) entries ([reg-applications.properties](https://github.com/opencadc/reg/tree/main/reg#reg-applicationsproperites-optional-experimental)) |
| application.serviceEntries | list | `[]` | VOSI-enabled API (web service) entries ([reg-resource-caps.properties](https://github.com/opencadc/reg/tree/main/reg#reg-resource-capsproperties-optional)) |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| fullnameOverride | string | `""` |  |
| httpRoute | object | `{"annotations":{},"enabled":false,"hostnames":["chart-example.local"],"parentRefs":[{"name":"gateway","sectionName":"http"}],"rules":[{"matches":[{"path":{"type":"PathPrefix","value":"/headers"}}]}]}` | Expose the service via gateway-api HTTPRoute Requires Gateway API resources and suitable controller installed within the cluster (see: https://gateway-api.sigs.k8s.io/guides/) |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"images.opencadc.org/core/reg"` |  |
| image.tag | string | `"1.2.1"` |  |
| imagePullSecrets | list | `[]` |  |
| ingress.annotations | object | `{}` |  |
| ingress.className | string | `""` |  |
| ingress.enabled | bool | `false` |  |
| ingress.hosts | list | `[]` |  |
| ingress.tls | list | `[]` |  |
| livenessProbe | string | `nil` |  |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` |  |
| podAnnotations | object | `{}` |  |
| podLabels | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| readinessProbe | string | `nil` |  |
| replicaCount | int | `1` |  |
| resources | object | `{}` |  |
| securityContext | object | `{}` |  |
| service.port | int | `8080` |  |
| service.type | string | `"ClusterIP"` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.automount | bool | `true` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` |  |
| tolerations | list | `[]` |  |
| tomcat.connector | object | `{"proxyName":"","proxyPort":"","scheme":""}` | Public URL for Tomcat behind a reverse proxy. Written to catalina.properties as tomcat.connector.* (X-Forwarded-Proto/Host/Port equivalent). Affects VOSI accessURL hostnames. Auto-derived from httpRoute or ingress when fields are empty; omitted for internal-only ClusterIP deployments. |
| tomcat.connector.proxyName | string | `""` | Public URL hostname. Auto-derived from httpRoute.hostnames[0] or ingress.hosts[0].host. |
| tomcat.connector.proxyPort | string | `""` | Public URL port. Auto-derived as 443 (https) or 80 (http). |
| tomcat.connector.scheme | string | `""` | Public URL scheme. Auto-derived as https (httpRoute or ingress with TLS) or http. |
| volumeMounts | list | `[]` |  |
| volumes | list | `[]` |  |
