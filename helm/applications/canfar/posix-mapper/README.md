# POSIX Mapper API Helm Chart

Installs the `posix-mapper` service, a RESTful API for mapping UIDs and GIDs to POSIX user and group names.

## Prerequisites

A Kubernetes Cluster, Helm 3, and a PostgreSQL database.

## Kubernetes Compatibility

The following Kubernetes versions are supported and work as we test against these versions in their respective branches. But note that other versions will likely work!

> [!NOTE]
> In CI we will be testing only last release and main branch on a regular basis.

| POSIX Mapper Release                                                                     | 1.29 |  1.30 |  1.31 |  1.32 |  1.33 |  1.34 |
|------------------------------------------------------------------------------------|------|-------|-------|-------|-------|-------|
| [`main` branch](https://github.com/opencadc/deployments/tree/main/helm/applications/canfar/cavern)                 | ✔               | ✔               | x               | x               | x               | x               |

## Installing the Chart

This Chart is meant to be used as a Production ready deployment. It is recommended to read through the configuration options and set them according to your needs.

### Add the Helm repository

```bash
helm repo add science-platform https://images.opencadc.org/chartrepo/platform
helm repo update
```

### External Dependencies

POSIX Mapper requires a persistent PostgreSQL database used to store UIDs and GIDs with their mapped names.  This can be installed in Kubernetes with persistent storage, or an external PostgreSQL database can be used.  
The information stored in the database must be persistent across restarts of the POSIX Mapper service as the UIDs and GIDs are used in Cavern's POSIX storage **must not change**.

| Dependency                    | Description                                          |
|-------------------------------|------------------------------------------------------|
| `PostgreSQL` >= 15            | Persistent storage for UIDs and GIDs. See the [values.yaml file](../posix-mapper/values.yaml#L131) |

### Configuration

The following table lists the configurable parameters of the POSIX Mapper Chart and their default values.  See the [values.yaml file](./values.yaml) for all configuration options.

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
| `applicationName`              | Application name                                     | ""                                  |
| `minUID`                       | Minimum UID to assign                                | 10000                              |
| `maxGID`                       | Maximum GID to assign                                | 900000                              |
| `postgresql.auth.username`     | PostgreSQL username                                  | ""                            |
| `postgresql.auth.password`     | PostgreSQL password                                  | ""                                  |
| `postgresql.maxActive`         | Maximum active connections to PostgreSQL              | ""                                 |
| `postgresql.url`               | PostgreSQL connection URL (if not installing)        | ""                                  |
| `postgresql.schema`            | PostgreSQL schema name                               | ""                            |
| `service.type`                 | Kubernetes service type                              | ClusterIP                           |
| `service.port`                 | Service port                                        | 8080                                |
| `nameOverride`                 | Override the name of the Chart                        | ""                                  |
| `fullnameOverride`             | Override the full name of the Chart                   | ""                                  |
| `ingress.enabled`              | Whether to create an Ingress resource                | false                               |
| `ingress.className`            | Ingress class name                                   | ""                                  |
| `ingress.annotations`          | Annotations to add to the Ingress resource           | {}                                  |
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
helm -n canfar upgrade --install --create-namespace --values values.yaml posix-mapper science-platform/posix-mapper
```
