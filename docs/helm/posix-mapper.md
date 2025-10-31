# Deployment

This Helm chart deploys the POSIX Mapper application, which is designed to map POSIX file system operations to a cloud-native environment.

## Prerequisites

- Kubernetes 1.27+
- Helm 3.0+
- Deployed PostgreSQL database for application data storage

### PostgreSQL Database
The POSIX Mapper requires a PostgreSQL database to store UID/GID mappings.  As this is a critical component, ensure that your database is properly configured and accessible from the POSIX Mapper application.  Use some persistent storage solution (like a Persistent Volume Claim) to ensure that the database data is not lost if deploying PostgreSQL in Kubernetes, or install a dedicated instance outside of the cluster.

#### Sample PostgreSQL Installation (in Kubernetes)
You can deploy a PostgreSQL database using the following Helm chart, with a PVC to ensure data persistence (Using `skaha-system` namespace as an example):

##### Persistent Volume Claim (PVC)
Create a Persistent Volume Claim (PVC) for PostgreSQL:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: posix-mapper-postgres-pvc
  namespace: skaha-system
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi
  storageClassName: ""
  selector:
    matchLabels:
      storage: posix-mapper-postgres-storage
```

This will need to match to a Persistent Volume (PV) that is available in your Kubernetes cluster.  An example PV could look like this for a CephFS instance in an OpenStack Share:

```yaml
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: posix-mapper-postgres-pv
  labels:
    storage: posix-mapper-postgres-storage
spec:
  capacity:
    storage: 2Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Delete
  storageClassName: ""
  cephfs:
    monitors:
    - 10.0.0.1:6789
    - 10.0.0.2:6789
    path: /volumes/myvolume
    user: posix-mapper-postgres
    readOnly: false
    secretRef:
      name: posix-mapper-postgres-secret
      namespace: skaha-system
```

Ultimately, it will be up to the deployment to ensure that the PVC is bound to a suitable PV, and that the PV is available in the cluster.

##### Install PostgreSQL using Helm

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

Use a Helm Values file to customize the installation.  This will initialize the database schema and set up the required user credentials.  The schema should match what the POSIX Mapper expects in its configuration.
Create a file named `my-postgresql-values.yaml` with the following content:
```yaml
auth:
  username: posixmapperuser
  password: posixmapperpwd
  database: posixmapper
primary:
  initdb:
    scripts:
      init_schema.sql: |
          create schema mapping;
  persistence:
    enabled: true
    existingClaim: posix-mapper-postgres-pvc
```
```bash
helm install posix-mapper-postgres bitnami/postgresql \
  --namespace skaha-system \
  --values my-postgresql-values.yaml
```


## POSIX Mapper Installation
To deploy the POSIX Mapper application using the Helm chart, follow these steps:

1. **Add the Helm Repository**
```bash
helm repo add science-platform-repo https://images.opencadc.org/chartrepo/platform
helm repo update
```

2. **Install the POSIX Mapper Chart**:
```bash
helm -n skaha-system --values <myvalues.yaml> install posix-mapper science-platform-repo/posix-mapper
```

## Configuration
The POSIX Mapper Helm chart comes with _some_ default configuration suitable for most deployments. However, you can customize the installation by providing your own `values.yaml` file. This allows you to override default settings such as resource allocations, environment variables, and other parameters, as well as set **required** parameters such as the PostgreSQL database configuration.

To customize the installation:

- **Create a `local-values.yaml` File**: Define your custom configurations in this file.
- **Install the Chart with Custom Values**:
```bash
helm -n skaha-system upgrade --install --values local-values.yaml posix-mapper science-platform-repo/posix-mapper
```

### Supported Configuration Options
See the [values.yaml](values.yaml) file for a complete list of configuration options. Below are some of the key parameters you can configure:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `kubernetesClusterDomain` | Kubernetes cluster domain used to find internal hosts | `cluster.local` |
| `replicaCount` | Number of POSIX Mapper replicas to deploy | `1` |
| `tolerations` | Array of tolerations to pass to Kubernetes for fine-grained Node targeting of the `posix-mapper` API | `[]` |
| `deployment.hostname` | Hostname for the POSIX Mapper deployment | `""` |
| `deployment.posixMapper.loggingGroups` | List of groups permitted to adjust logging levels for the POSIX Mapper service. | `[]` |
| `deployment.posixMapper.image` | POSIX Mapper Docker image | `images.opencadc.org/platform/posix-mapper:<current release version>` |
| `deployment.posixMapper.imagePullPolicy` | Image pull policy for the POSIX Mapper container | `IfNotPresent` |
| `deployment.posixMapper.resourceID` | Resource ID (URI) for this POSIX Mapper service | `""` |
| `deployment.posixMapper.oidcURI` | URI (or URL) for the OIDC service | `""` |
| `deployment.posixMapper.gmsID` | Resource ID (URI) for the IVOA Group Management Service | `""` |
| `deployment.posixMapper.minUID` | Minimum UID for POSIX Mapper operations.  High to avoid conflicts. | `10000` |
| `deployment.posixMapper.minGID` | Minimum GID for POSIX Mapper operations.  High to avoid conflicts. | `900000` |
| `deployment.posixMapper.registryURL` | URL for the IVOA registry containing service locations | `""` |
| `deployment.posixMapper.nodeAffinity` | Kubernetes Node affinity for the POSIX Mapper API Pod | `{}` |
| `deployment.posixMapper.extraPorts` | List of extra ports to expose in the POSIX Mapper service.  See the `values.yaml` file for examples. | `[]` |
| `deployment.posixMapper.extraVolumeMounts` | List of extra volume mounts to be mounted in the POSIX Mapper deployment.  See the `values.yaml` file for examples. | `[]` |
| `deployment.posixMapper.extraVolumes` | List of extra volumes to be mounted in the POSIX Mapper deployment.  See the `values.yaml` file for examples. | `[]` |
| `deployment.posixMapper.extraHosts` | List of extra hosts to be added to the POSIX Mapper deployment.  See the `values.yaml` file for examples. | `[]` |
| `deployment.posixMapper.extraEnv` | List of extra environment variables to be set in the POSIX Mapper service.  See the `values.yaml` file for examples. | `[]` |
| `deployment.posixMapper.resources` | Resource requests and limits for the POSIX Mapper API | `{}` |
| `deployment.posixMapper.registryURL` | (list OR string) | `[]` IVOA Registry array of IVOA Registry locations or single IVOA Registry location |
| `postgresql.maxActive` | Maximum number of active connections to the PostgreSQL database | `8` |
| `postgresql.url` | Required JDBC URL for the PostgreSQL database | `""` |
| `postgresql.schema` | Required Database schema to use for the POSIX Mapper | `""` |
| `postgresql.auth.username` | Username for the PostgreSQL database | `""` |
| `postgresql.auth.password` | Password for the PostgreSQL database | `""` |
