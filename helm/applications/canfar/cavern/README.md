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

The following table lists the configurable parameters of the Cavern Chart and their default values.  See the [values.yaml file](./values.yaml) for all configuration options.

| Parameter                       | Description                                          | Default Value                       |
|---------------------------------|------------------------------------------------------|-------------------------------------|
| `global.hostname`               | Hostname to use for all ingress routes               | ""                                  |
| `global.imagePullSecrets`      | Image pull secrets to use for all containers         | []                                  |
| `global.imagePullPolicy`       | Image pull policy to use for all containers          | IfNotPresent                        |
| `global.registryURL`           | Registry URL for IVOA compliant services             | ""                                  |
| `global.oidcURI`               | OIDC (IAM) server URI for token validation           | ""                                  |
| `global.gmsID`                 | GMS Service ID (URI)                                 | ""                                  |
| `global.loggingGroups`         | Array of groups allowed to set logging level         | []                                  |
| `global.identityManagerClass`  | IdentityManager class for authentication              | "org.opencadc.auth.StandardIdentityManager" |
| `global.podAnnotations`        | Annotations to add to the pod                         | {}                                  |
| `global.podLabels`             | Labels to add to the pod                              | {}                                  |
| `global.podSecurityContext`    | Pod security context settings                         | {}                                  |
| `global.securityContext`       | Container security context settings                   | {}                                  |
| `global.serviceAccount`        | Service account settings                              | {}                                  |
| `global.nodeSelector`          | Node selector settings                                | {}                                  |
| `global.tolerations`           | Tolerations settings                                 | []                                  |
| `global.affinity`              | Affinity settings                                    | {}                                  |
| `replicaCount`                 | Number of replicas to create                          | 1                                   |
| `image.repository`             | Container image repository                            | "images.opencadc.org/platform/cavern" |
| `image.pullPolicy`             | Container image pull policy                           | IfNotPresent                        |
| `image.tag`                    | Container image tag                                  | "0.9.0"                             |
| `resourceID`                   | Resource ID (IVOA identifier)                         | ""                                  |
| `posixMapperResourceID`        | Posix Mapper Resource ID (URI or URL)                | ""                                  |
| `quotaPlugin`                  | Quota plugin class name                              | "NoQuotaPlugin"                     |
| `allocations.defaultSizeGB`    | Default allocation size (GB)                         | ""                                  |
| `allocations.parentFolders`    | Parent folders for new allocations                   | ["/home", "/projects"]              |
| `filesystem.dataDir`           | Persistent data directory in container               | ""                                  |
| `filesystem.subPath`           | Relative path to node/file content                   | ""                                  |
| `filesystem.rootOwner`         | Root owner settings                                  | {}                                  |
| `filesystem.spec`              | Storage specification                                | {}                                  |
| `adminAPIKeys`                 | API keys for administrative tasks                    | {}                                  |
| `applicationName`              | Application name                                     | ""                                  |
| `uwsDatabase.install`          | Whether to deploy a local PostgreSQL database       | false                               |
| `uwsDatabase.username`         | PostgreSQL username                                  | "cavern"                            |
| `uwsDatabase.password`         | PostgreSQL password                                  | Randomly generated if not set     |
| `uwsDatabase.database`         | PostgreSQL database name                             | "cavern"                            |
| `uwsDatabase.url`              | PostgreSQL connection URL (if not installing)        | ""                                  |
| `service.type`                 | Kubernetes service type                              | | ClusterIP                           |
| `service.port`                 | Service port                                        | 8080                                |
| `ingress.enabled`              | Whether to create an Ingress resource                | false                               |
| `ingress.className`            | Ingress class name                                   | ""                                  |
| `ingress.annotations`          | Annotations to add to the Ingress resource           | | {}                                  |
| `ingress.hosts`                | Ingress hostnames                                   | []                                  |
| `ingress.tls`                  | Ingress TLS configuration                            | []                                  |
| `httpRoute.enabled`            | Use HTTP route Gateway API                            | false                             |
| `httpRoute.annotations`        | Annotations to add to the HTTPRoute resource         | {}                                  |
| `httpRoute.hostnames`          | HTTPRoute hostnames                                 | []                                  |
| `httpRoute.rules`              | HTTPRoute rules                                     | []                                  |
| `httpRoute.parentRefs`         | HTTPRoute parent references                          | []                                  |
| `resources`                    | Resource requests and limits                        | {}                                  |
| `livenessProbe`                | Liveness probe configuration                         | {}                                  |
| `readinessProbe`               | Readiness probe configuration                        | {}                                  |
| `autoscaling.enabled`          | Whether to enable Horizontal Pod Autoscaling         | false                               |
| `autoscaling.minReplicas`      | Minimum number of replicas for autoscaling           | 1                                   |
| `autoscaling.maxReplicas`      | Maximum number of replicas for autoscaling           | 10                                  |
| `autoscaling.targetCPUUtilizationPercentage` | Target CPU utilization percentage for autoscaling | 80                                  |
| `volumes`                      | Additional volumes to mount in the container         | []                                  |
| `volumeMounts`                 | Additional volume mounts for the container           | []                                  |

### Deploy
Create a `values.yaml` file to set the configuration options as needed (see above).  Then install the Chart with:

```bash
# Assumes the `canfar` namespace already exists
helm -n canfar upgrade --install -f values.yaml my-cavern science-platform/cavern
```
