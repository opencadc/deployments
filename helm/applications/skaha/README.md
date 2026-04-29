# skaha

A Helm chart to install the Skaha web service of the CANFAR Science Platform

| Chart | AppVersion | Type |
|:-----:|:----------:|:----:|
|1.6.0<!-- x-release-please-version --> | 1.2.1 | application |

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| file://../utils | utils | ^0.1.0 |
| oci://registry-1.docker.io/bitnamicharts | redis | ^18.19.0 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| autoscaling.enabled | bool | `true` | Enable HorizontalPodAutoscaler for skaha-tomcat. Target and scaling behavior are intentionally chart-managed (CPU 65%). |
| autoscaling.maxReplicas | int | `6` | Maximum number of skaha-tomcat replicas. |
| autoscaling.minReplicas | int | `2` | Minimum number of skaha-tomcat replicas. |
| deployment.hostname | string | `"myhost.example.com"` | Public hostname for the Skaha API. |
| deployment.skaha.apiVersion | string | `"v1"` | Skaha API version path segment (for example, `v1` -> `/skaha/v1/...`). |
| deployment.skaha.defaultQuotaGB | string | `"10"` | Default user storage quota in GiB for first-time users. |
| deployment.skaha.headlessPriorityClass.create | bool | `false` |  |
| deployment.skaha.headlessPriorityClass.description | string | `"For high-priority headless jobs. Preempting."` |  |
| deployment.skaha.headlessPriorityClass.globalDefault | bool | `false` |  |
| deployment.skaha.headlessPriorityClass.name | string | `""` |  |
| deployment.skaha.headlessPriorityClass.preemptionPolicy | string | `"PreemptLowerPriority"` |  |
| deployment.skaha.headlessPriorityClass.value | int | `2000` |  |
| deployment.skaha.identityManagerClass | string | `"org.opencadc.auth.StandardIdentityManager"` | Java IdentityManager implementation used for authentication. |
| deployment.skaha.image | string | `"images.opencadc.org/platform/skaha:1.2.1"` | Container image for the Skaha API service. |
| deployment.skaha.imageCache.refreshSchedule | string | `"*/30 * * * *"` | Cron schedule used to refresh cached images. |
| deployment.skaha.imagePullPolicy | string | `"Always"` | Image pull policy for the Skaha API container. |
| deployment.skaha.init.image | string | `"busybox:1.37.0"` | Init container image used to bootstrap user storage paths. |
| deployment.skaha.init.imagePullPolicy | string | `"IfNotPresent"` | Image pull policy for the bootstrap init container. |
| deployment.skaha.posixMapperCacheTTLSeconds | string | `"86400"` | TTL in seconds for cached POSIX mapper entries. |
| deployment.skaha.priorityClass | object | `{"create":true,"description":"For high-priority user pods. Preempting.","globalDefault":false,"name":"uber-user-preempt-high","preemptionPolicy":"PreemptLowerPriority","value":2000}` | PriorityClass assigned to the Skaha API Pod. |
| deployment.skaha.registryHosts | string | `"images.canfar.net"` | Space-delimited list of image registry hosts allowed for sessions. |
| deployment.skaha.resources.limits.cpu | string | `"2000m"` | CPU limit for the Skaha API container. |
| deployment.skaha.resources.limits.memory | string | `"3Gi"` | Memory limit for the Skaha API container. |
| deployment.skaha.resources.requests.cpu | string | `"1000m"` | CPU request for the Skaha API container. |
| deployment.skaha.resources.requests.memory | string | `"2Gi"` | Memory request for the Skaha API container. |
| deployment.skaha.sessions | object | `{"authorization":{"group":{"enabled":false,"uri":""},"permissionsAPI":{"baseURL":"","enabled":false,"method":"","name":"skaha","route":"","type":"route","version":""}},"expirySeconds":"345600","flexResourceRequests":{"headless":{"cpuCores":"1","memoryInGB":"4"}},"imagePullPolicy":"Always","ingress":{"customResponseHeaders":{},"tls":{}},"initContainerImage":"redis:8.2.2-bookworm","kueue":{"rbac":{"create":false}},"limitRange":{"enabled":false},"maxCount":"5","maxEphemeralStorage":"200Gi","minEphemeralStorage":"20Gi","nodeLabelSelector":null,"tolerations":[],"userStorage":{"admin":{"auth":null},"homeDirectory":"home","projectsDirectory":"projects","spec":{},"topLevelDirectory":"/cavern"}}` | @deprecated Prefer deployment.skaha.sessions.authorization or deprecated usersGroup alone. Still honoured when sessions.authorization.group.enabled is false. The IVOA GMS Group URI to verify users against for permission to use the Science Platform. See https://www.ivoa.net/documents/GMS/20220222/REC-GMS-1.0.html#tth_sEc3.2 usersGroup: "ivo://example.org/gms?prototyping-groups/mini-src/platform-users" Group URI for users to ensure priority for their headless jobs. See https://www.ivoa.net/documents/GMS/20220222/REC-GMS-1.0.html#tth_sEc3.2 headlessPriorityGroup: "ivo://example.org/gms?skaha-priority-headless-users" Array of GMS Group URIs allowed to set the logging level.  If none set, then nobody can change the log level. See https://www.ivoa.net/documents/GMS/20220222/REC-GMS-1.0.html#tth_sEc3.2 for GMS Group URIs See https://github.com/opencadc/core/tree/main/cadc-log for Logging control loggingGroups:   - "ivo://example.org/gms?prototyping-groups/mini-src/platform-users" The Resource ID (URI) of the Service that contains the Posix Mapping information posixMapperResourceID: "ivo://example.org/posix-mapper" URI or URL of the OIDC (IAM) server.  Used to validate incoming tokens. oidcURI: https://iam.example.org/ The Resource ID (URI) of the GMS Service. gmsID: ivo://example.org/gms The absolute URL of the IVOA Registry where services are registered registryURL: https://spsrc27.iaa.csic.es/reg This applies to Skaha itself.  Meaning, this Pod will be scheduled as described by the nodeAffinity clause. Note the different indentation level compared to the sessions.nodeAffinity. See https://kubernetes.io/docs/tasks/configure-pod-container/assign-pods-nodes-using-node-affinity/ nodeAffinity: {} Settings for User Sessions.  Sensible defaults supplied, but can be overridden. For units of storage, see https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-memory. |
| deployment.skaha.sessions.authorization.group.enabled | bool | `false` | When true, SKAHA_USERS_GROUP is set from uri. Required uri when enabled (Helm validates). The Skaha service enforces mutually exclusive authorization modes at runtime. |
| deployment.skaha.sessions.authorization.permissionsAPI.baseURL | string | `""` | Required when enabled is true (Helm validates). |
| deployment.skaha.sessions.authorization.permissionsAPI.enabled | bool | `false` | When true, SKAHA_PERMISSIONS_API_*_ENABLED is set from baseURL, type, route, name, version, and method. Required baseURL when enabled (Helm validates). The Skaha service enforces mutually exclusive authorization modes at runtime. |
| deployment.skaha.sessions.expirySeconds | string | `"345600"` | Session lifetime in seconds before expiry and shutdown. |
| deployment.skaha.sessions.flexResourceRequests.headless.cpuCores | string | `"1"` | Default CPU request (cores) for flex headless sessions. |
| deployment.skaha.sessions.flexResourceRequests.headless.memoryInGB | string | `"4"` | Default memory request (GiB) for flex headless sessions. |
| deployment.skaha.sessions.imagePullPolicy | string | `"Always"` | Image pull policy applied to all user session containers. |
| deployment.skaha.sessions.ingress.customResponseHeaders | object | `{}` | Custom response headers added to user-session ingress responses. |
| deployment.skaha.sessions.ingress.tls | object | `{}` | TLS configuration for the user-session Traefik IngressRoute. |
| deployment.skaha.sessions.initContainerImage | string | `"redis:8.2.2-bookworm"` | Image used by the session init container that manages POSIX data. |
| deployment.skaha.sessions.kueue | object | `{"rbac":{"create":false}}` | Per-session-type Kueue configuration. |
| deployment.skaha.sessions.limitRange.enabled | bool | `false` | Enable creation of a LimitRange for session container resources. |
| deployment.skaha.sessions.maxCount | string | `"5"` | Maximum number of active sessions allowed per user. |
| deployment.skaha.sessions.maxEphemeralStorage | string | `"200Gi"` | Maximum ephemeral storage limit for sessions (non-desktop). |
| deployment.skaha.sessions.minEphemeralStorage | string | `"20Gi"` | Initial ephemeral storage request for new sessions (non-desktop). |
| deployment.skaha.sessions.nodeLabelSelector | string | `nil` | Node label selector used when discovering schedulable worker nodes. |
| deployment.skaha.sessions.tolerations | list | `[]` | Tolerations applied to user session Pods. |
| deployment.skaha.sessions.userStorage.admin.auth | string | `nil` | Authentication settings used for user-storage admin operations. |
| deployment.skaha.sessions.userStorage.homeDirectory | string | `"home"` | Relative path under topLevelDirectory for user home directories. |
| deployment.skaha.sessions.userStorage.projectsDirectory | string | `"projects"` | Relative path under topLevelDirectory for shared projects storage. |
| deployment.skaha.sessions.userStorage.topLevelDirectory | string | `"/cavern"` | Absolute mount path containing user home and projects directories. |
| experimentalFeatures.enabled | bool | `false` | Enable processing of experimental feature gates. |
| ingress.enabled | bool | `true` | Enable ingress routing for the Skaha API. |
| ingress.path | string | `"/skaha"` | Ingress path prefix routed to the Skaha API Service. |
| kubernetesClusterDomain | string | `"cluster.local"` | Kubernetes DNS domain used when building internal service hostnames. |
| podSecurityContext | object | `{}` |  |
| rbac.clusterRole.create | bool | `false` |  |
| rbac.create | bool | `true` |  |
| redis.architecture | string | `"standalone"` | Redis deployment architecture. |
| redis.auth.enabled | bool | `false` | Enable Redis authentication. |
| redis.image.repository | string | `"redis"` | Redis image repository used by the bundled chart dependency. |
| redis.image.tag | string | `"8.2.2-bookworm"` | Redis image tag used by the bundled chart dependency. |
| redis.master.containerSecurityContext.allowPrivilegeEscalation | bool | `false` | Disallow privilege escalation in the Redis master container. |
| redis.master.containerSecurityContext.capabilities.drop | list | `["ALL"]` | Linux capabilities dropped from the Redis master container. |
| redis.master.containerSecurityContext.readOnlyRootFilesystem | bool | `true` | Mount Redis master root filesystem as read-only. |
| redis.master.containerSecurityContext.runAsGroup | int | `1001` | Group ID for the Redis master container. |
| redis.master.containerSecurityContext.runAsNonRoot | bool | `true` | Require Redis master to run as a non-root user. |
| redis.master.containerSecurityContext.runAsUser | int | `1001` | User ID for the Redis master container. |
| redis.master.containerSecurityContext.seccompProfile.type | string | `"RuntimeDefault"` | Seccomp profile type for Redis master. |
| redis.master.persistence.enabled | bool | `false` | Enable persistence for the Redis master StatefulSet. |
| replicaCount | int | `1` | Number of skaha-tomcat replicas when autoscaling is disabled. |
| secrets | string | `nil` |  |
| securityContext | object | `{}` | Optional Pod-level security context for the Skaha API Deployment. |
| service.port | int | `8080` | Service port exposed for the Skaha API Service. |
| serviceAccount | object | `{"annotations":{},"automount":true,"create":true,"name":""}` | ServiceAccount used by the Skaha API Pod. |
| tolerations | list | `[]` | Tolerations applied to the Skaha API Pod. |
