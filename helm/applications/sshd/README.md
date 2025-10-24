# sshd

![Version: 1.0.1](https://img.shields.io/badge/Version-1.0.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.0.0](https://img.shields.io/badge/AppVersion-1.0.0-informational?style=flat-square)

An SSHD service with SSSD to get users from LDAP

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Dustin Jenkins | <djenkins.cadc@gmail.com> |  |
| Shiny Brar | <shiny.brar@nrc-cnrc.gc.ca> |  |

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| file://../../common | common | ^1.0.0 |

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
