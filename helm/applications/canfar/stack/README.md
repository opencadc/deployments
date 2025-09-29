# CANFAR Science Platform Stack Helm Chart

Installs core components of the [CANFAR Science Platform](https://github.com/opencadc/science-platform.git), a collection of web services and browser-based user interfaces for accessing and processing large astronomical datasets.

This Helm Chart assembles the following components:
- [posix-mapper](../posix-mapper/) to maintain POSIX UID and GID mappings for users
- [skaha](../skaha/) to provide an Interactive and Batch User Session management API
- [cavern](../cavern/) to provide an IVOA VOSpace 2.1 compliant storage service
- [science-portal](../science-portal/) to provide a web-based user interface for interactive with User Sessions and the `skaha` API
- [storage-ui](../storage-ui/) to provide a web-based user interface for interacting with the `cavern` VOSpace service

## Prerequisites

A Kubernetes Cluster and Helm 3.

## Compatibility

The following Kubernetes versions are supported and work as we test against these versions in their respective branches. But note that other versions might work!

> [!NOTE]
> In CI we will be testing only last release and main branch on a regular basis.

| CANFAR stack                                                                      | Kubernetes 1.29 | Kubernetes 1.30 | Kubernetes 1.31 | Kubernetes 1.32 | Kubernetes 1.33 | Kubernetes 1.34 |
|--------------------------------------------------------------------------------------------|-----------------|-----------------|-----------------|-----------------|-----------------|-----------------|
| [`main`](https://github.com/prometheus-operator/kube-prometheus/tree/main)                 | ✔               | ✔               | x               | x               | x               | x               |

## Quickstart

This Chart is meant to be used as a Production ready deployment of the CANFAR Science Platform. It is recommended to read through the configuration options and set them according to your needs.

### Add the Helm repository

```bash
helm repo add science-platform https://images.opencadc.org/chartrepo/platform
helm repo update
```

### External Dependencies

Some services require persistent storage or a running PostgreSQL database. 

For persistence, it is recommended to configure a `StorageClass` and set the appropriate values in the `values.yaml` file or via the `--set` flag during installation.

| Service        | Dependency | Description                                          |
|----------------|------------------------|------------------------------------------|
| `posix-mapper` | `PostgreSQL` >= 15 (required)    | Persistent storage for UID and GID information.  See the [`posix-mapper` values.yaml file](../posix-mapper/values.yaml#L131) |
| `cavern`       | Storage Specification | PVC or some Kubernetes storage spec.  See the `filesystem.spec` in the [`cavern` values.yaml file](../cavern/values.yaml#L174) |
| `cavern`       | `PostgreSQL` >= 15 (optional) | Persistent storage for UWS metadata. See the [`cavern` values.yaml file](../cavern/values.yaml#L195) |
| `skaha`        | Storage Specification | PVC or some Kubernetes storage spec.  See the `session.storageSpec` in the [`skaha` values.yaml file](../skaha/values.yaml#L177) |

### Configuration
The following table lists the configurable parameters of the CANFAR stack and their default values. See the individual component's `values.yaml` files for more configuration options.

```yaml
# Global settings
global:
  hostname: canfar.example.org

  # This section builds out the service account more information can be found here: https://kubernetes.io/docs/concepts/security/service-accounts/
  serviceAccount:
    # Specifies whether a service account should be created
    create: true
    # Automatically mount a ServiceAccount's API credentials?
    automount: true
    # Annotations to add to the service account
    annotations: {}
    # The name of the service account to use.
    # If not set and create is true, a name is generated using the fullname template
    name: "canfar"
```

Each service can be configured separately.  Override `global` values in each service's configuration section.

```yaml
# Configuration for the POSIX Mapper service
posix-mapper:
  enabled: true
  global:
    hostname: posix-mapper.canfar.example.org
    serviceAccount:
      name: "canfar-posix-mapper"
      create: false

# Configuration for the Cavern service
cavern:
  enabled: true
  global:
    hostname: cavern-ivoa.example.org
    serviceAccount:
    name: "canfar-cavern"
      create: true
      annotations: {
        "exmple.org/annotation": "example-value"
      }
```
      
### Install the Chart

```bash
helm install -n canfar upgrade --install --create-namespace canfar science-platform/canfar
```

## Values Reference

The following table summarizes the configurable options available in
[`values.yaml`](./values.yaml):

| Key | Description | Defaults |
|---|---|---|
| `global.hostname` | Hostname to access all services on the Science Platform. | `hostname`, `serviceAccount` |
| `global.replicaCount` | Number of replicas for each service. | 1 |
| `global.imagePullSecrets` | Image pull secrets for private registries. | `[]` |
| `global.imagePullPolicy` | Image pull policy for containers. | `IfNotPresent` |
| `global.registryURL` | Container registry URL. |  |
| `global.oidcURI` | OIDC provider URL. |  |
| `global.gmsID` | GMS ID for the service. |  |
| `global.loggingGroups` | Logging groups for the service. | `[]` |
| `global.identityManagerClass` | Identity manager class for the service. | `org.opencadc.auth.StandardIdentityManager` |
| `global.serviceAccount.create` | Whether to create a service account. | `true` |
| `global.serviceAccount.automount` | Whether to automount the service account token. | `true` |
| `global.serviceAccount.name` | Name of the service account. |  |
| `global.tolerations` | Tolerations for the service. | `[]` |
| `posix-mapper` | Configuration for the POSIX Mapper service. See [`posix-mapper` values.yaml](../posix-mapper/values.yaml) | `{ enabled: true }` |
| `cavern` | Configuration for the Cavern service. See [`cavern` values.yaml](../cavern/values.yaml) | `{ enabled: true }` |
| `skaha` | Configuration for the Skaha service. See [`skaha` values.yaml](../skaha/values.yaml) | `{ enabled: true }` |
| `science-portal` | Configuration for the Science Portal service. See [`science-portal` values.yaml](../science-portal/values.yaml) | `{ enabled: true }` |
| `storage-ui` | Configuration for the Storage UI service. See [`storage-ui` values.yaml](../storage-ui/values.yaml) | `{ enabled: true }` |

For the full schema and default values, see each Chart's `values.yaml` file:
| Service | Documentation | Values File |
|---|---|---|
| `posix-mapper` | [../posix-mapper/](../posix-mapper/) | [values.yaml](../posix-mapper/values.yaml) |
| `cavern` | [../cavern/](../cavern/) | [values.yaml](../cavern/values.yaml) |
| `skaha` | [../skaha/](../skaha/) | [values.yaml](../skaha/values.yaml) |
| `science-portal` | [../science-portal/](../science-portal/) | [values.yaml](../science-portal/values.yaml) |
| `storage-ui` | [../storage-ui/](../storage-ui/) | [values.yaml](../storage-ui/values.yaml) |
