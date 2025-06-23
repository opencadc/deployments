# Kueue on Science Platform

_The documentation and design consideration are based on kueue v0.11+_

## Overview

Kueue is a kubernetes-native system to manages resources, quotas and queues for workloads in a kubernetes cluster. It is designed to alleviate the pressure from the kubernetes control plane and apiservers, while also providing a lot of flexibility in how workloads are managed.

When Kueue is enabled for a namespace, workloads within it are launched in a `Suspended` [Pod Phase](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase) rather than the nominal `Pending` state. This allows Kueue to manage the workload based on the resources, quotas, priority and queue rulesets created by the cluster administrator. When all conditions are met, Kueue injects the `nodeAffinity` and releases the workload into a `Pending` state, at which point the nominal control plane and apiservers take over the lifecycle management.

In short, **kueue intercepts the workload, and releases it when the cluster is ready to accept it**.

## Installation Guide

We recommend using the Helm chart published by the kubernetes-sigs/kueue project to install the system in your cluster from OCI Artifact Registry.

### Install from OCI Container Registry (Recommended)

This is the simplest method that doesn't require cloning the Kueue repository:

```bash

# Install Kueue using the OCI registry
cd configs/kueue/dev
helm install kueue oci://registry.k8s.io/kueue/charts/kueue:0.11.6 --values values.yaml --namespace kueue-system --create-namespace
```

Once Kueue is installed, you need to configure the system to manage workloads in the cluster. This is done by creating `ResourceFlavors`, `ClusterQueues`, `LocalQueues`, and `WorkloadPriorityClass` objects in the cluster. Sample configurations for these objects are provided in the `configs/kueue/dev/` and `configs/kueue/prod/` directories. To install them, you can use the following commands:

```bash
cd deployments/configs/kueue/dev/
kubectl apply -f clusterQueue.config.yaml  #Requires Cluster Admin Access
kubectl create namespace skaha-workload
kubectl create namespace canfar-b-workload
kubectl apply -f localQueue.config.yaml    #Does not require admin access
```

The default configurations are based on the following assumptions:
1. Homogenous infrastructure across the cluster.
2. Worker nodes are labelled as `skaha.opencadc.org/node-type=worker-node`. To label the nodes, run the following command:
   ```bash
   kubectl label nodes <node-name> skaha.opencadc.org/node-type=worker-node
   ```
   Set via `ResourceFlavor.spec.nodeLabels`
3. User workloads are launched in `skaha-workload` namespace.
    - Set via `ClusterQueue.spec.namespaceSelector.matchExpressions.values`
4. Supports resources set via `ClusterQueue.spec.resourceGroups.coveredResources`,
   - `cpu`
   - `memory`
   - `ephermeral-storage`
   - `nvidia.com/gpu`
5. There are three priority classes defined in the cluster, `high`, `medium`, and `low` described via `WorkloadPriorityClass` objects.

See detailed configuration guide below for more information on how to configure kueue for your cluster. We highly recommend customizing the configurations to suit your cluster environment and workload requirements.

## Kueue Configurations

Configurations for kueue are divided into two main categories: ***deployment* configuration** and ***controller* configuration**. The deployment configuration is the cluster environment in which the kueue system is deployed. The controller configuration is the behavior of the kueue system itself, which includes settings that govern how the kueue interacts with the cluster and manages workloads.

### Deployment Configuration

The kueue deployment configuration is the cluster environment in which the kueue system is deployed. Along with the controller configuration, all these are defined in the `values.yaml` file.

- Enable prometheus metrics for the kueue controller. This provides a lot of insight into the state of the controller and the queues.
  ```yaml
  enablePrometheus: true
  ```
- Teams can individually enable or disable any kueue `controllerManager.featureGates` as needed. For example, if you want to enable the `LocalQueueMetrics` feature gate, you can do so by adding the following to your helm values file:
  ```yaml
  featureGates:
    - name: LocalQueueMetrics
      enabled: true
  ```
### Controller Configuration

The kueue controller configuration is defined under the `managerConfig.controllerManagerConfigYaml` key in the helm values file. The following changes are recommended to the default values provided by the kueue helm chart. These are also provided in a `configs/kueue/[dev|prod]/controller.yaml` file in this repository for reference.

- `groupKindConcurrency`: This is the number of concurrent reconciliations allowed for a controller. The default values are set to 1, which is not recommended for production environments. It is recommended to set the concurrency limits to a higher value, depending on the workload and resources available in your cluster. For example, shown below are the recommended concurrency limits for the kueue controller for the Science Platform.
  ```yaml
  controller:
  # Number of concurrent reconciliation allowed for a controller.
  groupKindConcurrency:
    Job.batch: 256
    Pod: 4
    Workload.kueue.x-k8s.io: 256
    LocalQueue.kueue.x-k8s.io: 256
    ClusterQueue.kueue.x-k8s.io: 256
    ResourceFlavor.kueue.x-k8s.io: 4
  ```

- Client Connections Details: This is the number of queries per second allowed for the kubernetes apiserver. The default values are set to 16, which is not recommended for production environments. It is recommended to set the qps and burst values to a higher value, depending on the workload and resources available in your cluster. For example, shown below are the recommended qps and burst values for the kueue controller for the Science Platform.
  ```yaml
  # Client connection details for the k8s_apiserver
  clientConnection:
    # queries/second allowed for k8s_apiserver
    qps: 64
    # extra queries to accumulate when a client is exceeding its rate.
    burst: 128
  ```


- Explicitly set the kueue controller to not manage jobs that do not have `kueue.x-k8s.io/queue-name` annotation set. This ensures that jobs that are not managed by kueue are not intercepted by the system.
  ```yaml
  manageJobsWithoutQueueName: false
  ```

- It is highly recommend enabling metrics for cluster queues, as this provides a lot of insight into the state of the cluster and the queues.
  ```yaml
  metrics.enableClusterQueueResources: true
  ```

- It is highly recommended to initially only enable kueue for `batch/job` workloads to be reconciled by kueue and disable it for workloads, e.g. `StatefulSet, Deployment, DaemonSet, etc`.
  ```yaml
  integrations:
    frameworks:
        - "batch/job"
  ```

- We recommend setting the `namespaceSelector` to exclude the `kube-system` and `kueue-system` namespaces, and include only `skaha-workload` namespace. Coupled with `integrations.framework`, this will ensure that only `batch/jobs` in the `skaha-workload` namespace are reconciled by kueue.
  ```yaml
  integrations:
    ...
    podOptions:
      namespaceSelector:
        matchExpressions:
          - key: kubernetes.io/metadata.name
            operator: NotIn
            values: [ kube-system, kueue-system ]
          - key: kubernetes.io/metadata.name
            operator: In
            values: [ skaha-workload ]
  ```

- In order to copy labels from the `batch/job` to the `kueue` workload, you can set the `labelKeysToCopy` to the labels you want to copy. This is useful for tracking and managing workloads in the cluster.
  ```yaml
    labelKeysToCopy:
      - canfar-net-sessionID
      - canfar-net-sessionName
      - canfar-net-sessionType
      - canfar-net-userid
      - batch.kubernetes.io/job-name
  ```

## Configuration Guide

There are four main components to configure in kueue before it can be used for the Science Platform:

1. `ResourceFlavors` are objects to specify hardware configurations of resources (e.g., CPU, memory) available in your cluster.
2. `ClusterQueues` are objects to manage and distribute resources among various workloads.
3. `LocalQueues` are objects to assign workloads to the appropriate `ClusterQueue` within specific namespaces.
4. `WorkloadPriorityClass` defines the prority of the workload without affecting the pod priority.
5. Science Platform Integration for kueue resource objects.

### [1. ResourceFlavors](https://kueue.sigs.k8s.io/docs/concepts/resource_flavor/)

ResourceFlavors are objects that define the hardware configurations of resources available in your cluster. For example, shown below is a `ResourceFlavor` object that defines a GPU resource flavor mapping to a node label `instance-type: gpu`.

```yaml
apiVersion: kueue.x-k8s.io/v1beta1
kind: ResourceFlavor
metadata:
  name: "gpu"
spec:
  nodeLabels:
    instance-type: gpu
```

***NOTE:** Kueue only supports positive node labels. You cannot use negative node labels to define a `ResourceFlavor`. For example, you cannot use `nodeLabels: instance-type: !gpu` to define a `ResourceFlavor` for non-gpu nodes. This is a design decision made by the kueue team to ensure the complexity of the placement solution is kept to a minimum.*

You can can also create a `ResourceFlavor` fine-tuned to any specific hardware configuration. For example, shown below is a `ResourceFlavor` object that defines a `nvidia-gpu` resource flavor mapping to specific nodes which have `nvidia.com/gpu.product` with values `NVIDIA-A100-PCIE-40GB-MIG-3g.20gb` and `GRID-V100D-16C`.

```yaml
apiVersion: kueue.x-k8s.io/v1beta1
kind: ResourceFlavor
metadata:
  name: nvidia-gpu
spec:
  nodeLabels:
    matchExpressions:
      - key: nvidia.com/gpu.product
        operator: In
        values: [ NVIDIA-A100-PCIE-40GB-MIG-3g.20gb, GRID-V100D-16C ]
```

Alternatively, if your hardware is homogenous across the cluster, or if you no preferences for any specific hardware informed queuing, you can create a `ResourceFlavor` object that maps to all nodes in the cluster. For example, shown below is a `ResourceFlavor` object that defines a `default` resource flavor mapping to all nodes in the cluster.

```yaml
apiVersion: kueue.x-k8s.io/v1beta1
kind: ResourceFlavor
metadata:
  name: default
```

### [2. ClusterQueues](https://kueue.sigs.k8s.io/docs/concepts/cluster_queue/)

`ClusterQueues` govern resources defined by `ResourceFlavors` and distribute them among various workloads at a cluster level. A ClusterQueue can draw resources from multiple `ResourceFlavor` objects and share (borrow & lend) them amongst other `ClusterQueues` in the same cohort while respecting workload priorities, job ordering, preemption, and fairness.

#### Design Considerations

When designing the `ClusterQueue` objects, it is important to consider the following:
- **Cohorts**: `ClusterQueues` can be grouped into cohorts to share resources among themselves. This is useful for workloads that have similar resource requirements and can benefit from sharing resources.
- **Resources**: By default, administrators must specify all resources required by user jobs in the `ClusterQueues`. If you want to exclude some resources in the quota management and admission process, you **must** specify the resource prefixes to be excluded in a kueue configuration on the cluster level, otherwise the users jobs will not be admitted and forever remain in the `Suspended` state.
  ```yaml
  apiVersion: config.kueue.x-k8s.io/v1beta1
  kind: Configuration
  resources:
    excludeResourcePrefixes:
    - "memory"
  ```
- **nominalQuota**: When defining the `nominalQuota` for a cluster, it is important to consider that Kueue expects all resources within the nominal quota are availaible for use at all times. This means, if you have a cluster with non-kueue workloads, kueue will overcommit the resources in the cluster. Though this is not an inherent problem it can lead to a lot of `Pending` workloads in the cluster, and in some cases even `OutOfMemory` errors in the cluster. It is recommended to set the `nominalQuota` to a value that is less than the total resources available in the cluster. For example, if you have a cluster with 100 CPUs and 200GB of memory, you can set the `nominalQuota` to 90 CPUs and 180GB of memory, i.e. 90% of the total resources available in the cluster. This will ensure that kueue does not overcommit the resources in the cluster and can manage the workloads effectively.
-

For example, shown below are two `ClusterQueues` objects that use resources defined by the `ResourceFlavor` objects created in the previous step.

```yaml
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
    name: "standard-queue"
spec:
  namespaceSelector: {} # match all.
  # Queueing strategy to use.
  queueingStrategy: BestEffortFifo
  # Collection of clusterQueues that can borrow/lend resources among themselves.
  cohort: "collective-cohort"
  # Resources governed by the clusterQueue.
  resourceGroups:
  - coveredResources: ["cpu", "memory", "pods"]
    flavors:
    # Draws resources from the default resource flavor.
    - name: "default"
      # Can use upto 10 CPUs.
      resources:
      - name: "cpu"
        nominalQuota: 10
        borowingLimit: 2
        lendingLimit: 2
  preemption:
    reclaimWithinCohort: Any
    borrowWithinCohort: Never
    withinClusterQueue: LowerPriority
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
    name: "gpu-queue"
spec:
  namespaceSelector: {} # match all.
  queueingStrategy: BestEffortFifo
  cohort: "collective-cohort"
  resourceGroups:
  - coveredResources: ["nvidia.com/gpu"]
    flavors:
    # Draws resources from the nvidia-gpu resource flavor.
    - name: "nvidia-gpu"
      # Can use upto 2 GPUs.
      resources:
      - name: "nvidia.com/gpu"
        nominalQuota: 10
        borowingLimit: 1
        lendingLimit: 1
  preemption:
    reclaimWithinCohort: Any
    borrowWithinCohort: Never
    withinClusterQueue: LowerPriority
```

In the example, both `ClusterQueues` objects are part of the same `cohort` and can borrow and lend resources among themselves.


### [3. LocalQueues](https://kueue.sigs.k8s.io/docs/concepts/local_queue/)

`LocalQueues` are simply a namespaces representation of the `ClusterQueue` objects. They assign workloads to the appropriate `ClusterQueue` within specific namespaces. For example, shown below is a `LocalQueue` object that assigns workloads in the `skaha-workload` namespace to the `collective-queue` `ClusterQueue` object.

```yaml
apiVersion: kueue.x-k8s.io/v1beta1
kind: LocalQueue
metadata:
  namespace: skaha-workload
  name: skaha-queue
spec:
  clusterQueue: standard-queue
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: LocalQueue
metadata:
  namespace: skaha-workload
  name: skaha-gpu-queue
spec:
  clusterQueue: gpu-queue
```

### [4. WorkloadPriorityClass](https://kueue.sigs.k8s.io/docs/concepts/workload_priority_class/)

`WorkloadPriorityClass` defines the priority of the workload without affecting the pod priority. For example, shown below is a `WorkloadPriorityClass` object that defines a `high` priority class with a `priority` of `1000`.

```yaml
apiVersion: kueue.x-k8s.io/v1beta1
kind: WorkloadPriorityClass
metadata:
  name: high
value: 10000
description: "high priority"
---
apiVersion: kueue.x-k8s.io/v1beta1
kind: WorkloadPriorityClass
metadata:
  name: low
value: 100
description: "low priority"
```

### 5. Science Platform Integration

In order to integrate kueue with the Science Platform's `Skaha` backend service, the following environment variables must be set for the `skaha` service pods,


```yaml
KUEUE_ENABLED: bool
```
Where `KUEUE_ENABLED` is a boolean value that blanket enables or disables kueue for the entirety of the `skaha-workload` namespace.

```yaml
KUEUE_CONFIG: {}
```
`KUEUE_CONFIG` is a dictionary where the key values are name of the possible kinds of workloads that can be submitted to the science platform, which currently are `headless`, `notebook`, `carta`, `desktop`, `contributed`, `firefly` or `default`. Both of these keys need an object defining the `localQueue` and `priorityClass` for the workload type.

For example, shown below is a `KUEUE_CONFIG` object that defines the `queueName` and `priorityClass` in the `KUEUE_CONFIG` object,

```yaml
KUEUE_CONFIG:
  default:
    queueName: "skaha-workload-local-queue"
    priorityClass: "high"
  headless:
    queueName: "skaha-workload-local-queue"
    priorityClass: "low"
```
