# Science Portal Helm Chart

## Dependencies

- An existing Kubernetes cluster (1.29+).
- An IVOA Registry (See the [Current SKAO Registry](https://spsrc27.iaa.csic.es/reg))
- A working `skaha` web service deployed and registered in the IVOA Registry.

## Install

The Science Portal is a Single Page Application (SPA) with a rich Javascript client and DOM manager.  It uses React to power the various Dashboard elements, and is configurable for different OpenID Providers (OIdP).

### Minimum Helm configuration

See the full set of options in the [values.yaml](https://github.com/opencadc/science-platform/blob/SP-3544/deployment/helm/science-portal/values.yaml).  The deployed Redirect URI (`redirect_uri`) is `/science-portal/oidc-callback`, which handles
receiving the `code` as part of the authorization code flow, and obtaining a token to put into a cookie.

### Run with configured values

```bash
helm repo add science-platform https://images.opencadc.org/chartrepo/science-platform
helm repo update

helm install -n skaha-system --values my-science-portal-local-values-file.yaml science-portal science-platform/scienceportal

Release "science-portal" has been installed. Happy Helming!
NAME: science-portal
LAST DEPLOYED: Thu Oct 19 11:59:15 2024
NAMESPACE: skaha-system
STATUS: deployed
REVISION: 7
TEST SUITE: None
```

## Authentication & Authorization

A&A is handle by caching the Token Set server side and issuing a cookie to the browser to enable secure retrieval.  See the [Application Authentication Documentation](../../../docs/authentication/).

## Endpoints

The system will be available at the `/science-portal` endpoint, (i.e. https://example.com/science-portal).  Authenticating to the system is mandatory.

## Configuration

| Parameter                 | Description                                               | Default                |
| ------------------------- | --------------------------------------------------------- | ---------------------- |
| `kubernetesClusterDomain` | DNS domain of the Kubernetes cluster.                     | `cluster.local`        |
| `replicaCount`            | Number of replicas to run.                                | `1`                    |
| `securityContext`         | Optional container-level security context.                | `{}`                   |
| `podSecurityContext`      | Optional pod-level security context.                      | `{}`                   |
| `applicationName`         | Name of the application / WAR file.                       | *None* (commented out) |
| `deployment`              | Block containing Science Portal deployment configuration. | *N/A (object)*         |
| `experimentalFeatures.enabled`    | Enable/Disable all feature flags for unreleased or experimental UI features. | `false`       |
| `experimentalFeatures.slider.enabled`    | Enable/Disable the slider UI feature for Fixed jobs. | `false`       |
| `tolerations`             | List of Kubernetes tolerations added to the Pod spec.     | `[]`                   |
| `secrets`                 | Optional secrets (e.g., CA certificates).                 | *None* (commented out) |
| `redis`                   | Redis configuration for token caching.                    | *N/A (object)*         |
| `deployment.sciencePortal.image`                | Science Portal container image.                                 | `images.opencadc.org/platform/science-portal:1.2.3` |
| `deployment.sciencePortal.imagePullPolicy`      | Kubernetes image pull policy.                                   | `Always`                                            |
| `deployment.sciencePortal.tabLabels`            | List of exactly two UI tab labels.                              | `["Standard", "Advanced"]`                          |
| `deployment.sciencePortal.defaultProjectName`   | Default project selected for user sessions.                     | `"skaha"`                                           |
| `deployment.sciencePortal.extraEnv`             | Additional environment variables for the container.             | *None*                                              |
| `deployment.sciencePortal.extraPorts`           | Additional ports exposed by the container.                      | *None*                                              |
| `deployment.sciencePortal.resources`            | CPU and memory requests/limits.                                 | `requests: 750Mi/500m`, `limits: 1000Mi/1`          |
| `deployment.sciencePortal.skahaResourceID`      | IVOA Registry Resource ID for Skaha service.                    | *None*                                              |
| `deployment.sciencePortal.gmsID`                | URI of the GMS service.                                         | *None*                                              |
| `deployment.sciencePortal.oidc.uri`                | URL of the OpenID Provider (OIdP).                                                                                         | *None*  |
| `deployment.sciencePortal.oidc.clientID`           | Client ID registered with the OIdP.                                                                                        | *None*  |
| `deployment.sciencePortal.oidc.clientSecret`       | Client Secret issued by the OIdP.                                                                                          | *None*  |
| `deployment.sciencePortal.oidc.existingSecretName` | Name of an existing Kubernetes secret containing the `clientSecret` key. Alternative to providing `clientSecret` directly. | *None*  |
| `deployment.sciencePortal.oidc.redirectURI`        | URI to which the OIdP sends users after successful authentication.                                                         | *None*  |
| `deployment.sciencePortal.oidc.callbackURI`        | URI to redirect to after the OIDC callback completes (typically the `/science-portal` main page).                          | *None*  |
| `deployment.sciencePortal.oidc.scope`              | OpenID scopes requested during authentication (required).                                                                  | *None*  |
| `deployment.sciencePortal.registryURL`          | URL of the IVOA Registry server.                                | *None*                                              |
| `deployment.sciencePortal.nodeAffinity`         | Optional pod node affinity settings.                            | *None*                                              |
| `deployment.sciencePortal.identityManagerClass` | Class handling authentication.                                  | `org.opencadc.auth.StandardIdentityManager`         |
| `deployment.sciencePortal.extraVolumeMounts`    | Additional volume mounts (e.g., CA certs).                      | *None*                                              |
| `deployment.sciencePortal.extraVolumes`         | Additional volumes (paired with volume mounts).                 | *None*                                              |
| `deployment.sciencePortal.themeName`            | UI theme name.                                                  | *None*                                              |
| `deployment.sciencePortal.storageHomeURL`       | Base URL to the user’s home directories (for storage quota UI). | *None*                                              |
