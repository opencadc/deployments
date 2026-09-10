# ac

A Helm chart for the OpenCADC Access Control and Group Management Service

| Chart | AppVersion | Type |
|:-----:|:----------:|:----:|
|0.0.0<!-- x-release-please-version --> | 1.5.0 | application |

## Runtime configuration

The chart generates non-sensitive runtime files in a ConfigMap and projects an
existing Secret into the same `/config` directory. At minimum, the Secret must
contain `ac-ldap-config.properties`. A deployment using the AC OIDC endpoints
must also provide `ac-oidc-clients.properties`, `oidc-rsa256-pub.key`, and
`oidc-rsa256-priv.key` in that Secret.

The completed LDAP and OIDC files must not be stored in Git.

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| application.domains | list | `[]` |  |
| application.endpoint | string | `"/ac"` |  |
| application.groupNameRules | object | `{}` |  |
| application.logging.groups | list | `[]` |  |
| application.logging.usernames | list | `[]` |  |
| application.logging.users | list | `[]` |  |
| application.readUsers | list | `[]` |  |
| application.registryURL | string | `"https://example.org/reg"` |  |
| application.resourceID | string | `"ivo://cadc.nrc.ca/gms"` |  |
| configuration.existingSecret | string | `"ac-runtime-config"` |  |
| fullnameOverride | string | `""` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"bucket.canfar.net/ac"` |  |
| image.tag | string | `"1.5.0-20260127T224241"` |  |
| imagePullSecrets | list | `[]` |  |
| ingress.annotations | object | `{}` |  |
| ingress.className | string | `""` |  |
| ingress.enabled | bool | `false` |  |
| ingress.hosts[0].host | string | `"chart-example.local"` |  |
| ingress.hosts[0].paths[0].path | string | `"/ac"` |  |
| ingress.hosts[0].paths[0].pathType | string | `"Prefix"` |  |
| ingress.tls | list | `[]` |  |
| livenessProbe.failureThreshold | int | `3` |  |
| livenessProbe.httpGet.path | string | `"/ac/availability"` |  |
| livenessProbe.httpGet.port | string | `"http"` |  |
| livenessProbe.initialDelaySeconds | int | `10` |  |
| livenessProbe.periodSeconds | int | `30` |  |
| livenessProbe.timeoutSeconds | int | `10` |  |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` |  |
| podAnnotations | object | `{}` |  |
| podLabels | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| readinessProbe.failureThreshold | int | `3` |  |
| readinessProbe.httpGet.path | string | `"/ac/availability"` |  |
| readinessProbe.httpGet.port | string | `"http"` |  |
| readinessProbe.initialDelaySeconds | int | `10` |  |
| readinessProbe.periodSeconds | int | `30` |  |
| readinessProbe.timeoutSeconds | int | `10` |  |
| replicaCount | int | `1` |  |
| resources | object | `{}` |  |
| securityContext | object | `{}` |  |
| service.port | int | `8080` |  |
| service.type | string | `"ClusterIP"` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.automount | bool | `false` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` |  |
| startupProbe.failureThreshold | int | `30` |  |
| startupProbe.httpGet.path | string | `"/ac/availability"` |  |
| startupProbe.httpGet.port | string | `"http"` |  |
| startupProbe.periodSeconds | int | `10` |  |
| startupProbe.timeoutSeconds | int | `10` |  |
| tolerations | list | `[]` |  |
| tomcat.connector.proxyName | string | `"hostname.example.com"` |  |
| tomcat.connector.proxyPort | string | `"443"` |  |
| tomcat.connector.scheme | string | `"https"` |  |
