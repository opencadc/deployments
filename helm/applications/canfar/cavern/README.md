# Cavern Storage API Helm Chart

Installs the `cavern` service, a RESTful storage API (IVOA VOSpace 2.1 compliant), for the CANFAR Science Platform.  This Chart can also optionally install a PostgreSQL database to use as a UWS backend for Cavern.

## Prerequisites

A Kubernetes Cluster and Helm 3.

## Kubernetes Compatibility

The following Kubernetes versions are supported and work as we test against these versions in their respective branches. But note that other versions will likely work!

> [!NOTE]
> In CI we will be testing only last release and main branch on a regular basis.

| Cavern Release                                                                     | 1.29 |  1.30 |  1.31 |  1.32 |  1.33 |  1.34 |
|------------------------------------------------------------------------------------|------|-------|-------|-------|-------|-------|
| [`main` branch](https://github.com/opencadc/deployments/tree/main/helm/applications/canfar/cavern)                 | ✔               | ✔               | x               | x               | x               | x               |

## Installing the Chart

This Chart is meant to be used as a Production ready deployment of the Cavern VOSpace API. It is recommended to read through the configuration options and set them according to your needs.

### Add the Helm repository

```bash
helm repo add science-platform https://images.opencadc.org/chartrepo/platform
helm repo update
```

### External Dependencies

Cavern requires persistent storage and a PostgreSQL database.  The PostgreSQL database is used to store UWS job metadata.  Cavern can be configured to use an external PostgreSQL database, or the Chart can optionally install a PostgreSQL database as a Deployment with the `uwsDatabase.install=true` property set in the `values.yaml`.

For persistence, it is recommended to configure a `StorageClass`, create a PVC to use it, and set the appropriate values in the `values.yaml` file or via the `--set` flag during installation.

| Dependency                    | Description                                          |
|-------------------------------|------------------------------------------------------|
| Storage Specification         | Kubernetes storage YAML specification, such as a PVC declaration.  See the `filesystem.spec` in the [values.yaml file](../cavern/values.yaml#L167) |
| `PostgreSQL` >= 15 (optional) | Persistent storage for UWS metadata. See the [values.yaml file](../cavern/values.yaml#L188) |

### Configuration