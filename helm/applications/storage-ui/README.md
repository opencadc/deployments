# storageui

![Version: 0.7.0](https://img.shields.io/badge/Version-0.7.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.4.1](https://img.shields.io/badge/AppVersion-1.4.1-informational?style=flat-square)

A Helm chart to install the User Storage UI

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Dustin Jenkins | <djenkins.cadc@gmail.com> |  |
| Shiny Brar | <shiny.brar@nrc-cnrc.gc.ca> |  |

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
| deployment.storageUI.image | string | `"images.opencadc.org/client/storage-ui:1.4.1"` |  |
| deployment.storageUI.imagePullPolicy | string | `"IfNotPresent"` |  |
| deployment.storageUI.resources.limits.cpu | string | `"500m"` |  |
| deployment.storageUI.resources.limits.memory | string | `"850Mi"` |  |
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
| skaha.namespace | string | `"skaha-system"` |  |
| tolerations | list | `[]` |  |
