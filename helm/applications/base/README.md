# base

A Helm chart to install base components of the CANFAR Science Platform

| Chart | AppVersion | Type |
|:-----:|:----------:|:----:|
|0.5.0<!-- x-release-please-version --> | 0.1.4 | application |

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| https://traefik.github.io/charts | traefik | 26.1.0 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| kubernetesClusterDomain | string | `"cluster.local"` |  |
| secrets | string | `nil` |  |
| skaha.namespace | string | `"skaha-system"` |  |
| skahaWorkload.namespace | string | `"skaha-workload"` |  |
| traefik.install | bool | `false` |  |
| traefik.logs.access.enabled | bool | `false` | To enable access logs |
| traefik.logs.general.level | string | `"ERROR"` | Alternative logging levels are DEBUG, PANIC, FATAL, ERROR, WARN, and INFO. |
