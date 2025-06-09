# Skaha Helm Chart

See the [Deployment Guide](../science-platform/README.md) for a better idea of a full system.

The Skaha Helm chart facilitates the deployment of the Skaha application within a Kubernetes cluster. This chart is designed to streamline the installation and management of Skaha, ensuring a seamless integration into your Kubernetes environment.

## Prerequisites
Before deploying the Skaha Helm chart, ensure that the following conditions are met:

- **Kubernetes Cluster**: A running Kubernetes cluster, version 1.27 or higher.
- **Helm**: Helm package manager, version 3, installed on your machine. Refer to the [official Helm documentation](https://helm.sh/docs/) for installation instructions.
- **Kueue**: Kueue must be installed in your cluster, as Skaha integrates with Kueue for job queueing. Follow the [Kueue installation guide](https://kueue.sigs.k8s.io/docs/) to set it up.

## Installation
To deploy the Skaha application using the Helm chart, follow these steps:

1. **Add the Skaha Helm Repository**:
```bash
helm repo add skaha-repo https://images.opencadc.org/chartrepo/platform
```

2. **Update Helm Repositories**:
```bash
helm repo update
```

3. **Install the Skaha Chart**:
```bash
helm install skaha-release skaha-repo/skaha
```

Replace `skaha-release` with your desired release name.

## Configuration
The Skaha Helm chart comes with a default configuration suitable for most deployments. However, you can customize the installation by providing your own `values.yaml` file. This allows you to override default settings such as resource allocations, environment variables, and other parameters.

To customize the installation:

- **Create a `values.yaml` File**: Define your custom configurations in this file.
- **Install the Chart with Custom Values**:
```bash
helm install skaha-release skaha-repo/skaha -f values.yaml
```

### Supported Configuration Options
The following table lists the configurable parameters for the Skaha Helm chart:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `kubernetesClusterDomain` | Kubernetes cluster domain used to find internal hosts | `cluster.local` |
| `replicaCount` | Number of Skaha replicas to deploy | `1` |
| `tolerations` | Array of tolerations to pass to Kubernetes for fine-grained Node targeting of the `skaha` API | `[]` |
| `skaha.namespace` | Namespace where Skaha is deployed | `skaha-system` |
| `skahaWorkload.namespace` | Namespace where Skaha Workload (User Sesssion space) is deployed | `skaha-workload` |
| `deployment.hostname` | Hostname for the Skaha deployment | `""` |
| `deployment.skaha.image` | Skaha Docker image | `images.opencadc.org/platform/skaha:<current release version>` |
| `deployment.skaha.imagePullPolicy` | Image pull policy for the Skaha container | `IfNotPresent` |
| `deployment.skaha.imageCache.refreshSchedule` | Schedule for refreshing the Skaha image cache in `cron` format | `@daily` |
| `deployment.skaha.skahaTld` | Top-level directory for Skaha | `/cavern` |
| `deployment.skaha.defaultQuotaGB` | Default quota for Skaha in GB.  Used when allocating first-time users into the system. | `10` |
| `deployment.skaha.registryHosts` | Space delimited list of Docker (Harbor) registry hosts | `images.canfar.net` |
| `deployment.skaha.usersGroup` | GMS style Group URI for Skaha users to belong to | `""` |
| `deployment.skaha.adminsGroup` | GMS style Group URI for Skaha admins to belong to | `""` |
| `deployment.skaha.headlessGroup` | GMS style Group URI whose members can submit headless jobs | `""` |
| `deployment.skaha.headlessPriorityGroup` | GMS style Group URI whose member's headless jobs can pre-empt other's.  Useful fortight deadlines in processing | `""` |
| `deployment.skaha.loggingGroups` | List of GMS style Group URIs whose members can alter the log level.  See [cadc-log](https://github.com/opencadc/core/tree/main/cadc-log) regarding the `/logControl` endpoint. | `[]` |
| `deployment.skaha.posixMapperResourceID` | Resource ID (URI) for the POSIX Mapper service containing the UIDs and GIDs | `""` |
| `deployment.skaha.oidcURI` | URI (or URL) for the OIDC service | `""` |
| `deployment.skaha.gmsID` | Resource ID (URI) for the IVOA Group Management Service | `""` |
| `deployment.skaha.registryURL` | URL for the IVOA registry containing service locations | `""` |
| `deployment.skaha.nodeAffinity` | Kubernetes Node affinity for the Skaha API Pod | `{}` |
| `deployment.skaha.sessions.expirySeconds` | Expiry time, in seconds, for interactive sessions.  Defaults to four (4) days. | `"345600"` |
| `deployment.skaha.sessions.maxCount` | Maximum number of interactive sessions per user.  Defaults to three (3). | `"3"` |
| `deployment.skaha.sessions.minEphemeralStorage` | Minimum ephemeral storage, in [Kubernetes quantity](https://kubernetes.io/docs/reference/kubernetes-api/common-definitions/quantity/), for interactive sessions.  Defaults to 20Gi. | `"20Gi"` |
| `deployment.skaha.sessions.maxEphemeralStorage` | Maximum ephemeral storage, in [Kubernetes quantity](https://kubernetes.io/docs/reference/kubernetes-api/common-definitions/quantity/), for interactive sessions.  Defaults to 200Gi. | `"200Gi"` |
| `deployment.skaha.sessions.initContainerImage` | Init container image for Skaha User Sessions. | `redis-7.4.2-alpine3.21` |
| `deployment.skaha.sessions.queue.default.queueName` | Name of the default `LocalQueue` instance from Kueue for all types | `""` |
| `deployment.skaha.sessions.queue.default.priorityClass` | Name of the `priorityClass` for the all types to allow some pre-emption | `""` |
| `deployment.skaha.sessions.queue.<typename>.queueName` | Name of the `LocalQueue` instance from Kueue for the given type | `""` |
| `deployment.skaha.sessions.queue.<typename>.priorityClass` | Name of the `priorityClass` for the given type to allow some pre-emption | `""` |
| `deployment.skaha.sessions.hostname` | Hostname to access user sessions on.  Defaults to `deployment.hostname` | `deployment.hostname` |
| `deployment.skaha.sessions.extraVolumes` | List of extra `volume` and `volumeMount` to be mounted in User Sessions.  See the `values.yaml` file for examples. | `[]` |
| `deployment.skaha.sessions.gpuEnabled` | Enable GPU support for User Sessions.  Defaults to `false` | `false` |
| `deployment.skaha.sessions.nodeAffinity` | Kubernetes Node affinity for the Skaha User Session Pods | `{}` |
| `deployment.skaha.sessions.tolerations` | Array of tolerations to pass to Kubernetes for fine-grained Node targeting of the `skaha` User Sessions | `[]` |
| `deployment.skaha.sessions.prepareData.enabled` | Enable the Prepare Data volume mounting for the Indigo Prepare Data implementation | `false` |
| `deployment.skaha.sessions.prepareData.userDatasetsRootPath` | Dataset path | `false` |
| `deployment.skaha.extraEnv` | List of extra environment variables to be set in the Skaha service.  See the `values.yaml` file for examples. | `[]` |
| `deployment.skaha.resources` | Resource requests and limits for the Skaha API | `{}` |
| `deployment.skaha.extraPorts` | List of extra ports to expose in the Skaha service.  See the `values.yaml` file for examples. | `[]` |
| `deployment.skaha.extraVolumeMounts` | List of extra volume mounts to be mounted in the Skaha deployment.  See the `values.yaml` file for examples. | `[]` |
| `deployment.skaha.extraVolumes` | List of extra volumes to be mounted in the Skaha deployment.  See the `values.yaml` file for examples. | `[]` |
| `deployment.skaha.priorityClassName` | Name of the `priorityClass` for the Skaha API Pod used for pre-emption | `""` |
| `deployment.skaha.serviceAccountName` | Name of the Service Account for the Skaha API Pod | `"skaha"` |
| `deployment.skaha.identityManagerClass` | Java Class name for the [IdentityManager](https://github.com/opencadc/core/blob/main/cadc-util/src/main/java/ca/nrc/cadc/auth/IdentityManager.java) to use.  Defaults to [`org.opencadc.auth.StandardIdentityManager`](https://github.com/opencadc/ac/blob/main/cadc-gms/src/main/java/org/opencadc/auth/StandardIdentityManager.java) for use with bearer tokens (OIDC) | `"org.opencadc.auth.StandardIdentityManager"` |
| `secrets` | List of secrets to be mounted in the Skaha API defined as objects (i.e `secretName: {cert.pem: xxx}`) | `[]` |
| `storage.service.spec` | Storage class specification for the Skaha API.  Can be `persistentVolumeClaim` or a dynamic instantiation like `hostPath`.  See [Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/). | `{}` |
| `redis` | [Redis sub-chart configuration](https://github.com/bitnami/charts/tree/main/bitnami/redis) for Skaha's caching of Harbor Docker image metadata. | See [values.yaml](https://github.com/at88mph/deployments/blob/kueue-queue-discovery/helm/applications/skaha/values.yaml#L229) default. |

#### Notes on tolerations and nodeAffinity

Ensure that `tolerations` and `nodeAffinity` are at the expected indentation!  These are YAML configurations passed directly to Kubernetes, and the base `.tolerations` and `.deployment.skaha.nodeAffinity` values apply to the `skaha` API **only**, whereas the `.deployment.skaha.sessions.tolerations` and `.deployment.skaha.sessions.nodeAffinity` apply to _all_ User Session Pods.

### Integration with Kueue
Skaha leverages Kueue for efficient job queueing and management. Ensure that Kueue is properly installed and configured in your cluster. For detailed information on Kueue's features and setup, refer to the [Kueue documentation](https://kueue.sigs.k8s.io/docs/).

## Uninstallation
To remove the Skaha application from your cluster:

```bash
helm uninstall skaha-release
```

This command will delete all resources associated with the Skaha release.

## License
This project is licensed under the MIT License. For more information, refer to the LICENSE file in the repository.
