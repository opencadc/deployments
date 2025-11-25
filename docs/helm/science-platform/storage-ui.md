# Storage User Interface Helm Chart

## Dependencies

- An existing Kubernetes cluster (1.29+).
- An IVOA Registry (See the [Current SKAO Registry](https://spsrc27.iaa.csic.es/reg))
- A working Cavern (User Storage) system

## Install

The Storage UI is a browser application to interface with IVOA VOSpace services, with a rich Javascript client and DOM manager.  It uses vanilla JavaScript and jQuery with DataTables to power the listing table, and is configurable for different OpenID Providers (OIdP).

### Minimum Helm configuration

See the full set of options in the [values.yaml](./values.yaml).  The deployed Redirect URI (`redirect_uri`) is `/storage-ui/oidc-callback`, which handles
receiving the `code` as part of the authorization code flow, and obtaining a token to put into a cookie.

### Run with configured values

```bash
helm repo add science-platform-client https://images.opencadc.org/chartrepo/client
helm repo update

helm install -n skaha-system --values my-storage-ui-local-values-file.yaml storage-ui science-platform-client/storageui

Release "storage-ui" has been installed. Happy Helming!
NAME: storage-ui
LAST DEPLOYED: Thu Jan 12 17:01:07 2024
NAMESPACE: skaha-system
STATUS: deployed
REVISION: 3
TEST SUITE: None
```

## Authentication & Authorization

A&A is handle by caching the Token Set server side and issuing a cookie to the browser to enable secure retrieval.  See the [Application Authentication Documentation](./browser-authentication/).

## Endpoints

The system will be available at the `/storage` endpoint, (i.e. https://example.com/storage/list).  Authenticating to the system is optional.

## Configuration

| Parameter                 | Description                                                | Default                |
| ------------------------- | ---------------------------------------------------------- | ---------------------- |
| `kubernetesClusterDomain` | DNS domain for the Kubernetes cluster.                     | `cluster.local`        |
| `replicaCount`            | Number of Storage UI pod replicas.                         | `1`                    |
| `securityContext`         | Optional container-level security context.                 | *None (commented out)* |
| `applicationName`         | Application name used to rename the WAR file and endpoint. | `storage`              |
| `deployment`              | Block containing Storage UI deployment configuration.      | *N/A (object)*         |
| `tolerations`             | Pod-level tolerations for the Storage UI workload.         | `[]`                   |
| `secrets`                 | Optional secrets (e.g., CA certificates).                  | *None (commented out)* |
| `redis`                   | Redis configuration for token caching.                     | *N/A (object)*         |
| `deployment.storageUI.image`                     | Storage UI container image.                              | `images.opencadc.org/client/storage-ui:1.4.1` |
| `deployment.storageUI.imagePullPolicy`           | Image pull policy.                                       | `IfNotPresent`                                |
| `deployment.storageUI.extraEnv`                  | Optional extra environment variables (e.g., debug opts). | *None*                                        |
| `deployment.storageUI.extraPorts`                | Optional additional ports exposed from the container.    | *None*                                        |
| `deployment.storageUI.resources.requests.memory` | Memory requested by Storage UI.                          | `"500Mi"`                                     |
| `deployment.storageUI.resources.requests.cpu`    | CPU requested by Storage UI.                             | `"500m"`                                      |
| `deployment.storageUI.resources.limits.memory`   | Maximum memory allowed.                                  | `"1Gi"`                                       |
| `deployment.storageUI.resources.limits.cpu`      | Maximum CPU allowed.                                     | `"750m"`                                      |
| `deployment.storageUI.loggingGroups`             | Groups permitted to alter logging config.                | *None (commented out)*                        |
| `deployment.storageUI.backend`                   | Dictionary of VOSpace services described for UI usage.   | *None (commented out)*                        |
| `deployment.storageUI.gmsID`                     | Identifier (URI) for the GMS service.                    | *None*                                        |
| `deployment.storageUI.oidc.uri`                | URL of the OpenID Provider (OIdP).                                      | *None*  |
| `deployment.storageUI.oidc.clientID`           | Client ID registered with the OpenID Provider.                          | *None*  |
| `deployment.storageUI.oidc.clientSecret`       | Client Secret issued by the OIdP.                                       | *None*  |
| `deployment.storageUI.oidc.existingSecretName` | Name of a Kubernetes secret containing the `clientSecret` key.          | *None*  |
| `deployment.storageUI.oidc.redirectURI`        | Redirect URI after OIDC authentication.                                 | *None*  |
| `deployment.storageUI.oidc.callbackURI`        | URI to redirect after the callback completes (usually `/storage/list`). | *None*  |
| `deployment.storageUI.oidc.scope`              | OpenID scopes required for authentication.                              | *None*  |
| `deployment.storageUI.registryURL`               | URL of IVOA Registry service.                            | *None*                                        |
| `deployment.storageUI.nodeAffinity`              | Node affinity to influence scheduling.                   | *None*                                        |
| `deployment.storageUI.identityManagerClass`      | Class handling authentication.                           | `org.opencadc.auth.StandardIdentityManager`   |
| `deployment.storageUI.extraVolumeMounts`         | Optional extra volume mounts.                            | *None*                                        |
| `deployment.storageUI.extraVolumes`              | Optional extra volumes.                                  | *None*                                        |
| `deployment.storageUI.themeName`                 | UI theme (`src` or `canfar`).                            | *None*                                        |
