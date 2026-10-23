# cavern

A Helm chart to install the VOSpace User Storage API (Cavern)

| Chart | AppVersion | Type |
|:-----:|:----------:|:----:|
|0.10.7<!-- x-release-please-version --> | 0.10.4 | application |

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| file://../utils | utils | ^0.1.0 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| application.allocations | object | `{"authorization":{"groupURIs":[],"permissionsAPI":{}},"defaultSizeGB":10,"parentFolders":["/home","/projects"]}` | User allocation settings mapped to `cavern.properties` (default quota, parent folders, and authorization). |
| application.allocations.authorization | object | `{"groupURIs":[],"permissionsAPI":{}}` | Authorization for who may create allocations (`authorization` block in `cavern.properties`). |
| application.allocations.authorization.groupURIs | list | `[]` | IVOA GMS group URIs whose members may self-allocate; each URI becomes `org.opencadc.cavern.selfAllocateGroup`. Omit or leave empty to disable GMS self-allocation. |
| application.allocations.authorization.permissionsAPI | object | `{}` | SRCNet Permissions API settings (`org.opencadc.cavern.papi.*`). Leave as `{}` to omit. When present, `baseURL` and `authAPIBaseURL` are required. |
| application.allocations.defaultSizeGB | int | `10` | Default allocation size in GiB when no Quota VOSpace property is set (`org.opencadc.cavern.defaultQuotaGB`). |
| application.allocations.parentFolders | list | `["/home","/projects"]` | Top-level folders under which user allocations are created; each entry becomes `org.opencadc.cavern.allocationParent`. Must match Skaha user-storage layout. At least one entry is required (Helm validates). |
| application.applicationName | string | `"cavern"` |  |
| application.cookieSignaturePublicKey.existingSecret.name | string | `""` |  |
| application.cookieSignaturePublicKey.existingSecret.path | string | `""` |  |
| application.endpoint | string | `"/cavern"` |  |
| application.filesystem.dataDir | string | `""` |  |
| application.filesystem.rootOwner.adminUsername | string | `""` |  |
| application.identityManagerClass | string | `"org.opencadc.auth.StandardIdentityManager"` |  |
| application.image | string | `"images.opencadc.org/platform/cavern:0.10.4"` |  |
| application.imagePullPolicy | string | `"IfNotPresent"` |  |
| application.resourceID | string | `"ivo://example.org/cavern"` |  |
| application.resources.limits.cpu | string | `"500m"` |  |
| application.resources.limits.memory | string | `"1Gi"` |  |
| application.resources.requests.cpu | string | `"500m"` |  |
| application.resources.requests.memory | string | `"1Gi"` |  |
| application.uws.db.auth.existingSecret | string | `""` |  |
| application.uws.db.auth.secretKeys.password | string | `"password"` |  |
| application.uws.db.auth.secretKeys.username | string | `"username"` |  |
| application.uws.db.database | string | `"uws"` |  |
| application.uws.db.image | string | `"postgres:15.17"` |  |
| application.uws.db.install | bool | `true` |  |
| application.uws.db.maxActive | int | `2` |  |
| application.uws.db.runUID | int | `999` |  |
| application.uws.db.schema | string | `"uws"` |  |
| deployment.hostname | string | `"example.org"` |  |
| kubernetesClusterDomain | string | `"cluster.local"` |  |
| livenessProbe | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| readinessProbe | object | `{}` |  |
| replicaCount | int | `1` |  |
| secrets | string | `nil` |  |
| securityContext | object | `{}` |  |
| service.port | int | `8080` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.automount | bool | `true` |  |
| serviceAccount.create | bool | `false` |  |
| serviceAccount.name | string | `""` |  |
| storage.service.spec | string | `nil` | Subdirectory of the service volume to mount at filesystem.dataDir (`volumeMount.subPath` on `cavern-volume`). subPath: "" |
| tolerations | list | `[]` |  |
| volumeInit.image | string | `"busybox:1.36"` |  |
| volumeInit.imagePullPolicy | string | `"IfNotPresent"` |  |
| volumeInit.podSecurityContext.seccompProfile.type | string | `"RuntimeDefault"` |  |
| volumeInit.securityContext.allowPrivilegeEscalation | bool | `false` |  |
| volumeInit.securityContext.capabilities.drop[0] | string | `"ALL"` |  |
| volumeInit.securityContext.runAsNonRoot | bool | `true` |  |
| volumeInit.securityContext.runAsUser | int | `8675309` |  |
