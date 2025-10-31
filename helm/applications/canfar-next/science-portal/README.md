# science-portal

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.1.0](https://img.shields.io/badge/AppVersion-0.1.0-informational?style=flat-square)

A Helm chart for Science Portal Next.js application

**Homepage:** <https://github.com/opencadc/science-portal>

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Science Portal Team |  |  |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity.podAntiAffinity.preferredDuringSchedulingIgnoredDuringExecution[0].podAffinityTerm.labelSelector.matchExpressions[0].key | string | `"app.kubernetes.io/name"` |  |
| affinity.podAntiAffinity.preferredDuringSchedulingIgnoredDuringExecution[0].podAffinityTerm.labelSelector.matchExpressions[0].operator | string | `"In"` |  |
| affinity.podAntiAffinity.preferredDuringSchedulingIgnoredDuringExecution[0].podAffinityTerm.labelSelector.matchExpressions[0].values[0] | string | `"science-portal"` |  |
| affinity.podAntiAffinity.preferredDuringSchedulingIgnoredDuringExecution[0].podAffinityTerm.topologyKey | string | `"kubernetes.io/hostname"` |  |
| affinity.podAntiAffinity.preferredDuringSchedulingIgnoredDuringExecution[0].weight | int | `100` |  |
| autoscaling.enabled | bool | `true` |  |
| autoscaling.maxReplicas | int | `10` |  |
| autoscaling.minReplicas | int | `2` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| autoscaling.targetMemoryUtilizationPercentage | int | `80` |  |
| env[0].name | string | `"SERVICE_STORAGE_API"` |  |
| env[0].value | string | `"https://ws-uv.canfar.net/arc/nodes/home/"` |  |
| env[10].name | string | `"NEXT_PUBLIC_API_TIMEOUT"` |  |
| env[10].value | string | `"30000"` |  |
| env[11].name | string | `"NEXT_PUBLIC_ENABLE_QUERY_DEVTOOLS"` |  |
| env[11].value | string | `"false"` |  |
| env[12].name | string | `"NEXT_PUBLIC_EXPERIMENTAL"` |  |
| env[12].value | string | `"true"` |  |
| env[13].name | string | `"NEXT_USE_CANFAR"` |  |
| env[13].value | string | `"true"` |  |
| env[14].name | string | `"NEXT_PUBLIC_USE_CANFAR"` |  |
| env[14].value | string | `"true"` |  |
| env[15].name | string | `"AUTH_TRUST_HOST"` |  |
| env[15].value | string | `"true"` |  |
| env[16].name | string | `"NEXTAUTH_URL"` |  |
| env[16].value | string | `"https://science-portal.example.com"` |  |
| env[1].name | string | `"LOGIN_API"` |  |
| env[1].value | string | `"https://ws-cadc.canfar.net/ac"` |  |
| env[2].name | string | `"SKAHA_API"` |  |
| env[2].value | string | `"https://ws-uv.canfar.net/skaha"` |  |
| env[3].name | string | `"SRC_SKAHA_API"` |  |
| env[3].value | string | `"https://src.canfar.net/skaha"` |  |
| env[4].name | string | `"SRC_CAVERN_API"` |  |
| env[4].value | string | `"https://src.canfar.net/cavern"` |  |
| env[5].name | string | `"API_TIMEOUT"` |  |
| env[5].value | string | `"30000"` |  |
| env[6].name | string | `"NEXT_PUBLIC_LOGIN_API"` |  |
| env[6].value | string | `"https://ws-cadc.canfar.net/ac"` |  |
| env[7].name | string | `"NEXT_PUBLIC_SKAHA_API"` |  |
| env[7].value | string | `"https://ws-uv.canfar.net/skaha"` |  |
| env[8].name | string | `"NEXT_PUBLIC_SRC_SKAHA_API"` |  |
| env[8].value | string | `"https://src.canfar.net/skaha"` |  |
| env[9].name | string | `"NEXT_PUBLIC_SRC_CAVERN_API"` |  |
| env[9].value | string | `"https://src.canfar.net/cavern"` |  |
| fullnameOverride | string | `""` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"science-portal-nextjs"` |  |
| image.tag | string | `""` |  |
| imagePullSecrets | list | `[]` |  |
| ingress.annotations."cert-manager.io/cluster-issuer" | string | `"letsencrypt-prod"` |  |
| ingress.annotations."nginx.ingress.kubernetes.io/force-ssl-redirect" | string | `"true"` |  |
| ingress.annotations."nginx.ingress.kubernetes.io/ssl-redirect" | string | `"true"` |  |
| ingress.className | string | `"nginx"` |  |
| ingress.enabled | bool | `true` |  |
| ingress.hosts[0].host | string | `"science-portal.example.com"` |  |
| ingress.hosts[0].paths[0].path | string | `"/"` |  |
| ingress.hosts[0].paths[0].pathType | string | `"Prefix"` |  |
| ingress.tls[0].hosts[0] | string | `"science-portal.example.com"` |  |
| ingress.tls[0].secretName | string | `"science-portal-tls"` |  |
| livenessProbe.failureThreshold | int | `3` |  |
| livenessProbe.httpGet.path | string | `"/api/health"` |  |
| livenessProbe.httpGet.port | int | `3000` |  |
| livenessProbe.initialDelaySeconds | int | `30` |  |
| livenessProbe.periodSeconds | int | `10` |  |
| livenessProbe.timeoutSeconds | int | `3` |  |
| nameOverride | string | `""` |  |
| networkPolicy.egress[0].ports[0].port | int | `443` |  |
| networkPolicy.egress[0].ports[0].protocol | string | `"TCP"` |  |
| networkPolicy.egress[0].ports[1].port | int | `53` |  |
| networkPolicy.egress[0].ports[1].protocol | string | `"TCP"` |  |
| networkPolicy.egress[0].ports[2].port | int | `53` |  |
| networkPolicy.egress[0].ports[2].protocol | string | `"UDP"` |  |
| networkPolicy.egress[0].to[0].namespaceSelector | object | `{}` |  |
| networkPolicy.enabled | bool | `true` |  |
| networkPolicy.ingress[0].from[0].namespaceSelector.matchLabels.name | string | `"ingress-nginx"` |  |
| networkPolicy.ingress[0].ports[0].port | int | `3000` |  |
| networkPolicy.ingress[0].ports[0].protocol | string | `"TCP"` |  |
| networkPolicy.policyTypes[0] | string | `"Ingress"` |  |
| networkPolicy.policyTypes[1] | string | `"Egress"` |  |
| nodeSelector | object | `{}` |  |
| oidc.callbackUri | string | `"https://science-portal.example.com/science-portal"` |  |
| oidc.clientId | string | `""` |  |
| oidc.redirectUri | string | `"https://science-portal.example.com/api/auth/callback/oidc"` |  |
| oidc.scope | string | `"openid profile offline_access"` |  |
| oidc.uri | string | `"https://ska-iam.stfc.ac.uk/"` |  |
| podAnnotations | object | `{}` |  |
| podDisruptionBudget.enabled | bool | `true` |  |
| podDisruptionBudget.minAvailable | int | `1` |  |
| podSecurityContext.fsGroup | int | `1001` |  |
| podSecurityContext.runAsGroup | int | `1001` |  |
| podSecurityContext.runAsNonRoot | bool | `true` |  |
| podSecurityContext.runAsUser | int | `1001` |  |
| podSecurityContext.seccompProfile.type | string | `"RuntimeDefault"` |  |
| readinessProbe.failureThreshold | int | `3` |  |
| readinessProbe.httpGet.path | string | `"/api/health/ready"` |  |
| readinessProbe.httpGet.port | int | `3000` |  |
| readinessProbe.initialDelaySeconds | int | `10` |  |
| readinessProbe.periodSeconds | int | `5` |  |
| readinessProbe.timeoutSeconds | int | `3` |  |
| replicaCount | int | `2` |  |
| resources.limits.cpu | string | `"1000m"` |  |
| resources.limits.memory | string | `"1Gi"` |  |
| resources.requests.cpu | string | `"100m"` |  |
| resources.requests.memory | string | `"256Mi"` |  |
| secrets.existingSecret | string | `"science-portal-secrets"` |  |
| secrets.keys.authSecret | string | `"auth-secret"` |  |
| secrets.keys.oidcClientSecret | string | `"oidc-client-secret"` |  |
| securityContext.allowPrivilegeEscalation | bool | `false` |  |
| securityContext.capabilities.drop[0] | string | `"ALL"` |  |
| securityContext.readOnlyRootFilesystem | bool | `false` |  |
| service.annotations | object | `{}` |  |
| service.port | int | `80` |  |
| service.targetPort | int | `3000` |  |
| service.type | string | `"ClusterIP"` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` |  |
| tolerations | list | `[]` |  |
