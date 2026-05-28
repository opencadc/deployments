# cavern

A Helm chart to install the VOSpace User Storage API (Cavern)

| Chart | AppVersion | Type |
|:-----:|:----------:|:----:|
|0.10.0-rc.10<!-- x-release-please-version --> | 0.10.0 | application |

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| file://../utils | utils | ^0.1.0 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| deployment.cavern.allocations | object | `{"authorization":{"groupURIs":[],"permissionsAPI":{}},"defaultSizeGB":10,"parentFolders":["/home","/projects"]}` | User allocation settings mapped to `cavern.properties` (default quota, parent folders, and authorization). |
| deployment.cavern.allocations.authorization | object | `{"groupURIs":[],"permissionsAPI":{}}` | Authorization for who may create allocations (`authorization` block in `cavern.properties`). |
| deployment.cavern.allocations.authorization.groupURIs | list | `[]` | IVOA GMS group URIs whose members may self-allocate; each URI becomes `org.opencadc.cavern.selfAllocateGroup`. Omit or leave empty to disable GMS self-allocation. |
| deployment.cavern.allocations.authorization.permissionsAPI | object | `{}` | SRCNet Permissions API settings (`org.opencadc.cavern.papi.*`). Leave as `{}` to omit. When present, `baseURL` and `authAPIBaseURL` are required. |
| deployment.cavern.allocations.defaultSizeGB | int | `10` | Default allocation size in GiB when no Quota VOSpace property is set (`org.opencadc.cavern.defaultQuotaGB`). |
| deployment.cavern.allocations.parentFolders | list | `["/home","/projects"]` | Top-level folders under which user allocations are created; each entry becomes `org.opencadc.cavern.allocationParent`. Must match Skaha user-storage layout. At least one entry is required (Helm validates). |
| deployment.cavern.applicationName | string | `"cavern"` |  |
| deployment.cavern.cookieSignaturePublicKey.existingSecret.name | string | `""` |  |
| deployment.cavern.cookieSignaturePublicKey.existingSecret.path | string | `""` |  |
| deployment.cavern.endpoint | string | `"/cavern"` |  |
| deployment.cavern.filesystem.dataDir | string | `""` |  |
| deployment.cavern.filesystem.rootOwner.adminUsername | string | `""` |  |
| deployment.cavern.identityManagerClass | string | `"org.opencadc.auth.StandardIdentityManager"` |  |
| deployment.cavern.image | string | `"images.opencadc.org/platform/cavern:0.10.0"` |  |
| deployment.cavern.imagePullPolicy | string | `"IfNotPresent"` |  |
| deployment.cavern.resourceID | string | `"ivo://example.org/cavern"` |  |
| deployment.cavern.resources.limits.cpu | string | `"500m"` |  |
| deployment.cavern.resources.limits.memory | string | `"1Gi"` |  |
| deployment.cavern.resources.requests.cpu | string | `"500m"` |  |
| deployment.cavern.resources.requests.memory | string | `"1Gi"` |  |
| deployment.cavern.uws.db.auth.existingSecret | string | `""` |  |
| deployment.cavern.uws.db.auth.secretKeys.password | string | `"password"` |  |
| deployment.cavern.uws.db.auth.secretKeys.username | string | `"username"` |  |
| deployment.cavern.uws.db.database | string | `"uws"` |  |
| deployment.cavern.uws.db.image | string | `"postgres:15.17"` |  |
| deployment.cavern.uws.db.install | bool | `true` |  |
| deployment.cavern.uws.db.maxActive | int | `2` |  |
| deployment.cavern.uws.db.runUID | int | `999` |  |
| deployment.cavern.uws.db.schema | string | `"uws"` |  |
| deployment.hostname | string | `"example.org"` |  |
| kubernetesClusterDomain | string | `"cluster.local"` |  |
| livenessProbe | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| readinessProbe | object | `{}` |  |
| replicaCount | int | `1` |  |
| secrets | string | `nil` |  |
| securityContext | object | `{}` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.automount | bool | `true` |  |
| serviceAccount.create | bool | `false` |  |
| serviceAccount.name | string | `""` |  |
| storage.service.spec | string | `nil` |  |
| tolerations | list | `[]` |  |
| volumeInit.image | string | `"busybox:1.36"` |  |
| volumeInit.imagePullPolicy | string | `"IfNotPresent"` |  |
| volumeInit.podSecurityContext.seccompProfile.type | string | `"RuntimeDefault"` |  |
| volumeInit.securityContext.allowPrivilegeEscalation | bool | `false` |  |
| volumeInit.securityContext.capabilities.drop[0] | string | `"ALL"` |  |
| volumeInit.securityContext.runAsNonRoot | bool | `true` |  |
| volumeInit.securityContext.runAsUser | int | `8675309` |  |
