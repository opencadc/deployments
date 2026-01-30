# storageui

A Helm chart to install the User Storage UI

| Chart | AppVersion | Type |
|:-----:|:----------:|:----:|
|0.8.1<!-- x-release-please-version --> | 1.4.3 | application |

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| file://../utils | utils | ^0.1.0 |
| oci://registry-1.docker.io/bitnamicharts | redis | ^18.4.0 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| deployment.hostname | string | `"example.host.com"` |  |
| deployment.storageUI.gmsID | string | `nil` |  |
| deployment.storageUI.identityManagerClass | string | `"org.opencadc.auth.StandardIdentityManager"` |  |
| deployment.storageUI.image | string | `"images.opencadc.org/client/storage-ui:1.4.3"` |  |
| deployment.storageUI.imagePullPolicy | string | `"IfNotPresent"` |  |
| deployment.storageUI.resources.limits.cpu | string | `"750m"` |  |
| deployment.storageUI.resources.limits.memory | string | `"1Gi"` |  |
| deployment.storageUI.resources.requests.cpu | string | `"500m"` |  |
| deployment.storageUI.resources.requests.memory | string | `"500Mi"` |  |
| deployment.storageUI.themeName | string | `nil` |  |
| kubernetesClusterDomain | string | `"cluster.local"` |  |
| redis.architecture | string | `"standalone"` |  |
| redis.auth.enabled | bool | `false` |  |
| redis.image.repository | string | `"redis"` |  |
| redis.image.tag | string | `"8.2.2-bookworm"` |  |
| redis.master.persistence.enabled | bool | `false` |  |
| replicaCount | int | `1` |  |
| tolerations | list | `[]` |  |
