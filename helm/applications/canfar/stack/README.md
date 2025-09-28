# CANFAR Science Platform Stack

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
> In CI we will be testing only last two releases and main branch on a regular basis.

| CANFAR stack                                                                      | Kubernetes 1.29 | Kubernetes 1.30 | Kubernetes 1.31 | Kubernetes 1.32 | Kubernetes 1.33 | Kubernetes 1.34 |
|--------------------------------------------------------------------------------------------|-----------------|-----------------|-----------------|-----------------|-----------------|-----------------|
| [`main`](https://github.com/prometheus-operator/kube-prometheus/tree/main)                 | ✔               | ✔               | x               | x               | x               | x               |

## Quickstart

This Chart is meant to be used as a Production ready deployment of the CANFAR Science Platform. It is recommended to read through the configuration options and set them according to your needs.

### Add the Helm repository

```bash
helm repo add canfar https://images.opencadc.org/chartrepo/platform
helm repo update
```

### External Dependencies

Some services require persistent storage or a running PostgreSQL database. 

For persistence, it is recommended to configure a `StorageClass` and set the appropriate values in the `values.yaml` file or via the `--set` flag during installation.

| Service        | Dependency | Description                              |
|----------------|------------------------|------------------------------------------|
| `posix-mapper` | `PostgreSQL` >= 15 (required)    | Persistent storage for UID and GID information.  See the [`posix-mapper` values.yaml file](../posix-mapper/values.yaml#L131) |
| `cavern`       | Storage Specification | PVC or some Kubernetes storage spec.  See the `filesystem.spec` in the [`cavern` values.yaml file](../cavern/values.yaml#L174) |
| `cavern`       | `PostgreSQL` >= 15 (optional) | Persistent storage for UWS metadata. See the [`cavern` values.yaml file](../cavern/values.yaml#L195) |

### Install the Chart

```bash
helm install -n canfar upgrade --install --create-namespace canfar science-platform/canfar
```