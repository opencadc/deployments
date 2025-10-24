# posixmapper

![Version: 0.5.0](https://img.shields.io/badge/Version-0.5.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.3.2](https://img.shields.io/badge/AppVersion-0.3.2-informational?style=flat-square)

A Helm chart to install the UID/GID POSIX Mapper

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Dustin Jenkins | <djenkins.cadc@gmail.com> |  |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| deployment.hostname | string | `"example.org"` |  |
| deployment.posixMapper.gmsID | string | `nil` |  |
| deployment.posixMapper.image | string | `"images.opencadc.org/platform/posix-mapper:0.3.2"` |  |
| deployment.posixMapper.imagePullPolicy | string | `"Always"` |  |
| deployment.posixMapper.minGID | int | `900000` |  |
| deployment.posixMapper.minUID | int | `10000` |  |
| deployment.posixMapper.oidcURI | string | `nil` |  |
| deployment.posixMapper.registryURL | string | `nil` |  |
| deployment.posixMapper.resourceID | string | `"ivo://opencadc.org/posix-mapper"` |  |
| deployment.posixMapper.resources.limits.cpu | string | `"750m"` |  |
| deployment.posixMapper.resources.limits.memory | string | `"1500Mi"` |  |
| deployment.posixMapper.resources.requests.cpu | string | `"500m"` |  |
| deployment.posixMapper.resources.requests.memory | string | `"1Gi"` |  |
| kubernetesClusterDomain | string | `"cluster.local"` |  |
| postgresql | object | `{}` |  |
| replicaCount | int | `1` |  |
| secrets | string | `nil` |  |
| tolerations | list | `[]` |  |
