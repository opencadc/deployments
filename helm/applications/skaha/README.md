# skaha

A Helm chart to install the Skaha web service of the CANFAR Science Platform

| Chart | AppVersion | Type |
|:-----:|:----------:|:----:|
|1.4.0<!-- x-release-please-version --> | 1.2.0 | application |

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| file://../utils | utils | ^0.1.0 |
| oci://registry-1.docker.io/bitnamicharts | redis | ^18.19.0 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| deployment.hostname | string | `"myhost.example.com"` |  |
| deployment.skaha.apiVersion | string | `"v1"` |  |
| deployment.skaha.defaultQuotaGB | string | `"10"` |  |
| deployment.skaha.identityManagerClass | string | `"org.opencadc.auth.StandardIdentityManager"` |  |
| deployment.skaha.image | string | `"images.opencadc.org/platform/skaha:1.1.7"` |  |
| deployment.skaha.imageCache.refreshSchedule | string | `"*/30 * * * *"` |  |
| deployment.skaha.imagePullPolicy | string | `"Always"` |  |
| deployment.skaha.init.image | string | `"busybox:1.37.0"` |  |
| deployment.skaha.init.imagePullPolicy | string | `"IfNotPresent"` |  |
| deployment.skaha.posixMapperCacheTTLSeconds | string | `"86400"` |  |
| deployment.skaha.priorityClassName | string | `"uber-user-preempt-high"` |  |
| deployment.skaha.registryHosts | string | `"images.canfar.net"` |  |
| deployment.skaha.resources.limits.cpu | string | `"2000m"` |  |
| deployment.skaha.resources.limits.memory | string | `"3Gi"` |  |
| deployment.skaha.resources.requests.cpu | string | `"1000m"` |  |
| deployment.skaha.resources.requests.memory | string | `"2Gi"` |  |
| deployment.skaha.serviceAccountName | string | `"skaha"` |  |
| deployment.skaha.sessions.expirySeconds | string | `"345600"` |  |
| deployment.skaha.sessions.imagePullPolicy | string | `"Always"` |  |
| deployment.skaha.sessions.ingress.customResponseHeaders | object | `{}` |  |
| deployment.skaha.sessions.ingress.tls | object | `{}` |  |
| deployment.skaha.sessions.initContainerImage | string | `"redis:8.2.2-bookworm"` |  |
| deployment.skaha.sessions.kueue | object | `{}` |  |
| deployment.skaha.sessions.maxCount | string | `"5"` |  |
| deployment.skaha.sessions.maxEphemeralStorage | string | `"200Gi"` |  |
| deployment.skaha.sessions.minEphemeralStorage | string | `"20Gi"` |  |
| deployment.skaha.sessions.nodeLabelSelector | string | `nil` |  |
| deployment.skaha.sessions.tolerations | list | `[]` |  |
| deployment.skaha.sessions.userStorage.admin.auth | string | `nil` |  |
| deployment.skaha.sessions.userStorage.homeDirectory | string | `"home"` |  |
| deployment.skaha.sessions.userStorage.persistentVolumeClaimName | string | `"skaha-workload-cavern-pvc"` |  |
| deployment.skaha.sessions.userStorage.projectsDirectory | string | `"projects"` |  |
| deployment.skaha.sessions.userStorage.topLevelDirectory | string | `"/cavern"` |  |
| experimentalFeatures.enabled | bool | `false` |  |
| experimentalFeatures.sessionLimitRange.enabled | bool | `false` |  |
| experimentalFeatures.sessionLimitRange.limitSpec | object | `{}` |  |
| experimentalFeatures.sessionLimitRange.rbac.create | bool | `true` |  |
| ingress.enabled | bool | `true` |  |
| ingress.path | string | `"/skaha"` |  |
| kubernetesClusterDomain | string | `"cluster.local"` |  |
| podSecurityContext | object | `{}` |  |
| redis.architecture | string | `"standalone"` |  |
| redis.auth.enabled | bool | `false` |  |
| redis.image.repository | string | `"redis"` |  |
| redis.image.tag | string | `"8.2.2-bookworm"` |  |
| redis.master.containerSecurityContext.allowPrivilegeEscalation | bool | `false` |  |
| redis.master.containerSecurityContext.capabilities.drop[0] | string | `"ALL"` |  |
| redis.master.containerSecurityContext.readOnlyRootFilesystem | bool | `true` |  |
| redis.master.containerSecurityContext.runAsGroup | int | `1001` |  |
| redis.master.containerSecurityContext.runAsNonRoot | bool | `true` |  |
| redis.master.containerSecurityContext.runAsUser | int | `1001` |  |
| redis.master.containerSecurityContext.seccompProfile.type | string | `"RuntimeDefault"` |  |
| redis.master.persistence.enabled | bool | `false` |  |
| replicaCount | int | `1` |  |
| secrets | string | `nil` |  |
| securityContext | object | `{}` |  |
| service.port | int | `8080` |  |
| skahaWorkload.namespace | string | `"skaha-workload"` |  |
| tolerations | list | `[]` |  |
