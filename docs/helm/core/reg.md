# IVOA Registry Helm Chart

The Registry (`reg`) Helm chart facilitates the deployment of the Registry application within a Kubernetes cluster. This chart is designed to streamline the installation and management of the Registry service, ensuring a seamless integration into your Kubernetes environment.

## Prerequisites
Before deploying the Registry Helm chart, ensure that the following conditions are met:

- **Kubernetes Cluster**: A running Kubernetes cluster, version 1.29 or higher.
- **Helm**: Helm package manager, version 3, installed on your machine. Refer to the [official Helm documentation](https://helm.sh/docs/) for installation instructions.

## Installation
To deploy the Registry application using the Helm chart, follow these steps:

1. **Add the Registry Helm Repository**:
```bash
helm repo add registry-repo https://images.opencadc.org/chartrepo/core
```

2. **Update Helm Repositories**:
```bash
helm repo update
```

3. **Install the Registry Chart**:
```bash
helm --namespace cadc-core upgrade --install --values <your-registry-values.yaml> registry-release registry-repo/reg
```
Replace `registry-release` with your desired release name.

## Configuration
The Registry Helm chart comes with a default configuration suitable for most deployments. However, you can customize the installation by providing your own `values.yaml` file. This allows you to override default settings such as resource allocations, environment variables, and other parameters.

To customize the installation:

- **Create a `values.yaml` File**: Define your custom configurations in this file.
- **Install the Chart with Custom Values**:
```bash
helm --namespace cadc-core upgrade --install --values values.yaml registry-release registry-repo/reg
```

This Helm Chart supports both Pod and Container level security contexts. You can enable or disable these features based on your cluster's security requirements.  The Registry service need not run as **root**, so it is recommended to enable these security contexts for enhanced security.

### Example `values.yaml` Configuration
```yaml
podSecurityContext:
  runAsNonRoot: true
  seccompProfile:
    type: RuntimeDefault

securityContext:
  runAsUser: 10000
  runAsGroup: 10000
  allowPrivilegeEscalation: false
  seccompProfile:
    type: RuntimeDefault

global:
  hostname: example.org

application:
  serviceEntries:
    - id: ivo://example.org/services/service-1
      url: https://example.org/services/service-1/capabilities
    - id: ivo://example.org/services/service-2
      url: https://example.org/services/service-2/capabilities

  authority: ivo://example.org/authority

# This section builds out the service account more information can be found here: https://kubernetes.io/docs/concepts/security/service-accounts/
serviceAccount:
  # Specifies whether a service account should be created
  create: false
  # Automatically mount a ServiceAccount's API credentials?
  automount: false
  # Annotations to add to the service account
  annotations: {}
  # The name of the service account to use.
  # If not set and create is true, a name is generated using the fullname template
  name: "example-registry-service-account"

# Ingress is an quick way to get up and running, but httpRoute is preferred to make use of the Kubernetes Gateway API.
# If using Ingress, ensure that your cluster has an Ingress controller installed and configured to handle the specified className.
ingress:
  enabled: true
  className: traefik
  hosts:
  - host: example.org
    paths:
      - backend:
          service:
            name: reg
            port:
              number: 8080
        path: /reg
        pathType: Prefix
```

## Uninstallation
To remove the Registry application from your cluster:

```bash
helm --namespace cadc-core uninstall registry-release
```

This command will delete all resources associated with the Registry release.

## License
This project is licensed under the MIT License. For more information, refer to the LICENSE file in the repository.

## Values Reference

--8<-- "helm/applications/reg/README.md"
