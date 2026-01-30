# Skaha Helm Chart

The Skaha Helm chart facilitates the deployment of the Skaha application within a Kubernetes cluster. This chart is designed to streamline the installation and management of Skaha, ensuring a seamless integration into your Kubernetes environment.

## Prerequisites
Before deploying the Skaha Helm chart, ensure that the following conditions are met:

- **Kubernetes Cluster**: A running Kubernetes cluster, version 1.27 or higher.
- **Helm**: Helm package manager, version 3, installed on your machine. Refer to the [official Helm documentation](https://helm.sh/docs/) for installation instructions.
- **Kueue**: Kueue is recommended to be installed in your cluster, as Skaha optionally integrates with Kueue for job queueing. Follow the [Kueue installation guide](https://kueue.sigs.k8s.io/docs/) to set it up.

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
helm --namespace skaha-system upgrade --install --values <your-skaha-values.yaml> skaha-release skaha-repo/skaha
```
Replace `skaha-release` with your desired release name.

## Configuration
The Skaha Helm chart comes with a default configuration suitable for most deployments. However, you can customize the installation by providing your own `values.yaml` file. This allows you to override default settings such as resource allocations, environment variables, and other parameters.

To customize the installation:

- **Create a `values.yaml` File**: Define your custom configurations in this file.
- **Install the Chart with Custom Values**:
```bash
helm --namespace skaha-system upgrade --install --values values.yaml skaha-release skaha-repo/skaha
```

### LimitRange
You can define a `LimitRange` for User Session Pods by modifying the `deployment.skaha.sessions.limitRange` section in your `values.yaml` file. This configuration allows you to set resource limits and requests for different session types.  The `min` clause is ignored due to hard-coded resources for Desktop and Firefly sessions.  This will go directly into a `LimitRange` object created in the Skaha workload Namespace, and, as such, supports the Kubernetes
units.

The `rbac` section allows you to create the necessary Role and RoleBinding for the LimitRange object.  If your organization does not permit the creation of RBAC objects, you can set `create` to `false` and manage the RBAC externally.

```yaml
deployment:
  skaha:
    sessions:
      limitRange:
        rbac:
          create: true
        limitSpec:
          max:
            # maximum resource limit to grow to, also used by the UI to limit selectable resources
            memory: "96Gi"
            cpu: "12"
          default:
            # actually refers to default limit
            memory: "32Gi"
            cpu: "8"
          defaultRequest:
            # default resource requests
            memory: "4Gi"
            cpu: "1"
```

### Flexible Session Pods
You can customize the User Session Pods by modifying the `deployment.skaha.sessions` section in your `values.yaml` file. This includes settings for resource requests, storage allocation, and more.

Flexible User sessions are created with a small amount of CPU and memory by default and are allowed to grow to a specified limit in the `LimitRange` configuration. You can adjust these minimum (request) settings as needed:
```yaml
deployment:
  skaha:
    sessions:
      flexResourceRequests:
        # The headless session type resource requests get slightly more resources to start.
        headless:
          memoryInGB: "2"
          cpuCores: "1"
        notebook:
          memoryInGB: "2"
          cpuCores: "0.5"
```

The `headless`, `notebook`, `desktop`, `contributed`, and `firefly` session types can all be customized individually.  Any session type not specified will use the values defined in the `LimitRange` configuration.

**Note** that Kubernetes resource units are not supported in this configuration; only floating point or integer numbers as strings are valid.  For example, for 100m of CPU, use `"0.1"`.

#### Notes on tolerations and nodeAffinity

Ensure that `tolerations` and `nodeAffinity` are at the expected indentation!  These are YAML configurations passed directly to Kubernetes, and the base `.tolerations` and `.deployment.skaha.nodeAffinity` values apply to the `skaha` API **only**, whereas the `.deployment.skaha.sessions.tolerations` and `.deployment.skaha.sessions.nodeAffinity` apply to _all_ User Session Pods.

## Kueue
Skaha leverages Kueue for efficient job queueing and management when properly installed and configured in your cluster. For detailed information on Kueue's features and setup, refer to the [Kueue documentation](https://kueue.sigs.k8s.io/docs/).

### Installation
https://kueue.sigs.k8s.io/docs/installation/#install-a-released-version

Will install the Kueue Chart, with a default `ClusterQueue`, and whatever defined `LocalQueues` were declared in the `deployment.skaha.sessions.kueue` section:
```yaml
deployment:
  skaha:
    sessions:
      kueue:
        notebook:
          queueName: some-local-queue
          priorityClass: med
```


To determine your cluster's allocatable resources, checkout a small Python utility (requires [`uv`](https://github.com/astral-sh/uv?tab=readme-ov-file#installation)):
https://github.com/opencadc/deployments/tree/main/configs/kueue/kueuer

Then run:
```bash
git clone https://github.com/opencadc/deployments.git
cd deployments/configs/kueue/kueuer
# if not using the default ~/.kube/config
export KUBECONFIG=/home/user/.kube/my-config

# 60% of cluster resources
uv run kr cluster resources -f allocatable -s 0.6

# 80% of cluster resources
uv run kr cluster resources -f allocatable -s 0.8
```

## Uninstallation
To remove the Skaha application from your cluster:

```bash
helm --namespace skaha-system uninstall skaha-release
```

This command will delete all resources associated with the Skaha release.

## License
This project is licensed under the MIT License. For more information, refer to the LICENSE file in the repository.

## Values Reference

--8<-- "helm/applications/skaha/README.md"
