# sshd

An SSHD service with SSSD to get users from LDAP

| Chart | AppVersion | Type |
|:-----:|:----------:|:----:|
|1.1.0<!-- x-release-please-version --> | 1.0.0 | application |

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| file://../utils | utils | ^0.1.0 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| entryPoint | string | `""` |  |
| extraEnv | list | `[]` |  |
| extraHosts | list | `[]` |  |
| extraVolumeMounts | list | `[]` |  |
| extraVolumes | list | `[]` |  |
| image.digest | string | `""` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.pullSecrets | list | `[]` |  |
| image.registry | string | `"images.opencadc.org"` |  |
| image.repository | string | `"platform/sshd"` |  |
| image.tag | string | `"1.0.0"` |  |
| ldap | object | `{}` |  |
| replicaCount | int | `1` |  |
| resources | object | `{}` |  |
| rootPath | string | `""` |  |
| secrets | object | `{}` |  |
| storageSpec | object | `{}` |  |
