# scienceportal

![Version: 1.0.0](https://img.shields.io/badge/Version-1.0.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.0.1](https://img.shields.io/badge/AppVersion-1.0.1-informational?style=flat-square)

A Helm chart to install the Science Portal UI

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Dustin Jenkins | <djenkins.cadc@gmail.com> |  |

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| file://../utils | utils | ^0.1.0 |
| oci://registry-1.docker.io/bitnamicharts | redis | ^18.19.0 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| deployment.hostname | string | `"example.host.com"` |  |
| deployment.sciencePortal.gmsID | string | `nil` |  |
| deployment.sciencePortal.identityManagerClass | string | `"org.opencadc.auth.StandardIdentityManager"` |  |
| deployment.sciencePortal.image | string | `"images.opencadc.org/platform/science-portal:1.0.1"` |  |
| deployment.sciencePortal.imagePullPolicy | string | `"Always"` |  |
| deployment.sciencePortal.resources.limits.cpu | string | `"500m"` |  |
| deployment.sciencePortal.resources.limits.memory | string | `"500M"` |  |
| deployment.sciencePortal.resources.requests.cpu | string | `"500m"` |  |
| deployment.sciencePortal.resources.requests.memory | string | `"500M"` |  |
| deployment.sciencePortal.skahaResourceID | string | `nil` |  |
| deployment.sciencePortal.tabLabels[0] | string | `"Standard"` |  |
| deployment.sciencePortal.tabLabels[1] | string | `"Advanced"` |  |
| deployment.sciencePortal.themeName | string | `nil` |  |
| experimentalFeatures.enabled | bool | `false` |  |
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
