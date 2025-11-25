# cavern

A Helm chart to install the VOSpace User Storage API (Cavern)

| Chart | AppVersion | Type |
|:-----:|:----------:|:----:|
|0.8.1<!-- x-release-please-version --> | 0.9.0 | application |

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| file://../utils | utils | ^0.1.0 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| deployment.cavern.adminAPIKeys | object | `{}` |  |
| deployment.cavern.allocations.defaultSizeGB | int | `10` |  |
| deployment.cavern.allocations.parentFolders[0] | string | `"/home"` |  |
| deployment.cavern.allocations.parentFolders[1] | string | `"/projects"` |  |
| deployment.cavern.applicationName | string | `"cavern"` |  |
| deployment.cavern.endpoint | string | `"/cavern"` |  |
| deployment.cavern.filesystem.dataDir | string | `""` |  |
| deployment.cavern.filesystem.rootOwner.gid | string | `nil` |  |
| deployment.cavern.filesystem.rootOwner.uid | string | `nil` |  |
| deployment.cavern.filesystem.rootOwner.username | string | `""` |  |
| deployment.cavern.identityManagerClass | string | `"org.opencadc.auth.StandardIdentityManager"` |  |
| deployment.cavern.image | string | `"images.opencadc.org/platform/cavern:0.9.2"` |  |
| deployment.cavern.imagePullPolicy | string | `"IfNotPresent"` |  |
| deployment.cavern.resourceID | string | `"ivo://example.org/cavern"` |  |
| deployment.cavern.resources.limits.cpu | string | `"500m"` |  |
| deployment.cavern.resources.limits.memory | string | `"1Gi"` |  |
| deployment.cavern.resources.requests.cpu | string | `"500m"` |  |
| deployment.cavern.resources.requests.memory | string | `"1Gi"` |  |
| deployment.cavern.uws.db.database | string | `"uws"` |  |
| deployment.cavern.uws.db.image | string | `"postgres:15.12"` |  |
| deployment.cavern.uws.db.install | bool | `true` |  |
| deployment.cavern.uws.db.maxActive | int | `2` |  |
| deployment.cavern.uws.db.password | string | `"uwspwd"` |  |
| deployment.cavern.uws.db.runUID | int | `999` |  |
| deployment.cavern.uws.db.schema | string | `"uws"` |  |
| deployment.cavern.uws.db.username | string | `"uwsuser"` |  |
| deployment.hostname | string | `"example.org"` |  |
| kubernetesClusterDomain | string | `"cluster.local"` |  |
| livenessProbe | object | `{}` |  |
| readinessProbe | object | `{}` |  |
| replicaCount | int | `1` |  |
| secrets | string | `nil` |  |
| skaha.namespace | string | `"skaha-system"` |  |
| storage.service.spec | string | `nil` |  |
| tolerations | list | `[]` |  |
