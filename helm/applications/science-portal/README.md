# scienceportal

A Helm chart to install the Science Portal UI

| Chart | AppVersion | Type |
|:-----:|:----------:|:----:|
|1.2.0<!-- x-release-please-version --> | 1.2.5 | application |

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| file://../utils | utils | ^0.1.0 |
| oci://registry-1.docker.io/bitnamicharts | redis | ^18.19.0 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| deployment.hostname | string | `"example.host.com"` |  |
| deployment.sciencePortal.defaultProjectName | string | `"skaha"` |  |
| deployment.sciencePortal.gmsID | string | `nil` |  |
| deployment.sciencePortal.identityManagerClass | string | `"org.opencadc.auth.StandardIdentityManager"` |  |
| deployment.sciencePortal.image | string | `"images.opencadc.org/platform/science-portal:1.2.5"` |  |
| deployment.sciencePortal.imagePullPolicy | string | `"Always"` |  |
| deployment.sciencePortal.resources.limits.cpu | string | `"1"` |  |
| deployment.sciencePortal.resources.limits.memory | string | `"1000Mi"` |  |
| deployment.sciencePortal.resources.requests.cpu | string | `"500m"` |  |
| deployment.sciencePortal.resources.requests.memory | string | `"750Mi"` |  |
| deployment.sciencePortal.skahaResourceID | string | `nil` |  |
| deployment.sciencePortal.tabLabels[0] | string | `"Standard"` |  |
| deployment.sciencePortal.tabLabels[1] | string | `"Advanced"` |  |
| deployment.sciencePortal.themeName | string | `nil` |  |
| experimentalFeatures.enabled | bool | `false` |  |
| experimentalFeatures.slider.enabled | bool | `false` |  |
| kubernetesClusterDomain | string | `"cluster.local"` |  |
| podSecurityContext | object | `{}` |  |
| redis.architecture | string | `"standalone"` |  |
| redis.auth.enabled | bool | `false` |  |
| redis.image.repository | string | `"redis"` |  |
| redis.image.tag | string | `"8.2.2-bookworm"` |  |
| redis.master.persistence.enabled | bool | `false` |  |
| replicaCount | int | `1` |  |
| securityContext | object | `{}` |  |
| tolerations | list | `[]` |  |
