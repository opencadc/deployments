# Base Helm Chart

## Install

### Dependencies

Kubernetes 1.29 and up are supported.

### From source

The base install also installs the Traefik proxy, which is needed by the Ingress when the Science Platform services are installed.

```sh
$ git clone https://github.com/opencadc/science-platform.git
$ cd science-platform/deployment/helm
$ helm --namespace traefik upgrade --install --dependency-update --values ./base/values.yaml <name> ./base
```

Where `<name>` is the name of this installation.  Example:
```sh
$ helm --namespace traefik upgrade --install --dependency-update --values ./base/values.yaml base ./base
```
This will create the core namespace (`skaha-system`), and install the Traefik proxy dependency.  Expected output:
```
NAME: base
LAST DEPLOYED: <Timestamp e.g. Mon Jun 30 10:39:04 2025>
NAMESPACE: skaha-system
STATUS: deployed
REVISION: 4
TEST SUITE: None
```

### From the CANFAR repository

The Helm repository contains the current stable version as well.

```sh
$ helm repo add canfar-skaha-system https://images.opencadc.org/chartrepo/platform
$ helm repo update
$ helm --namespace traefik upgrade --install --dependency-update --values canfar-skaha-system/base/values.yaml canfar-science-platform-base canfar-skaha-system/base
```

## Verification

After the install, there should exist the necessary Namespaces and Objects.  See the Namespaces:

```sh
$ kubectl get namespaces
NAME                   STATUS   AGE
...
skaha-system           Active   28m
skaha-workload         Active   28m
```

## Proxy using Traefik

The [Traefik](https://traefik.io/traefik/) proxy server is also installed as a dependency, which handles SSL termination.  Helm options are under the `traefik` key in the `values.yaml` file.

You can create your own secrets to contain your self-signed server certificates to be used by
the SSL termination.  See the `values.yaml` file for more, and don't forget to `base64` encode
the values.

## Shared Storage

Shared Storage is handled by the `local` Persistent Volume types.

```yaml
...
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Delete
  storageClassName: local-storage
  local:
    path: /data/skaha-storage
...
```

### DNS on macOS

The Docker VM on macOS cannot mount the NFS by default as it cannot do name resolution in the cluster.  It first needs to know about the `kube-dns` IP.  e.g.:

```sh
$ kubectl --namespace kube-system get service kube-dns
NAME       TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)                  AGE
kube-dns   ClusterIP   10.96.0.10   <none>        53/UDP,53/TCP,9153/TCP   4d23h
```

The `ClusterIP` needs to be known to the Docker VM's name resolution.  A simple way to do this is to mount the Docker VM root and modify it.  It will take effect immediately:

```sh
$ docker run --rm --interactive --tty --volume /:/vm-root alpine sh
$ echo "nameserver 10.96.0.10" >> /vm-root/etc/resolv.conf
$ cat /vm-root/etc/resolv.conf
# DNS requests are forwarded to the host. DHCP DNS options are ignored.
nameserver 192.168.65.7
nameserver 10.96.0.10
```

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `kubernetesClusterDomain` | The DNS cluster domain | ` cluster.local` |
| `skaha.namespace` | The Namespace for the APIs (UIs and APIs) | `skaha-system` |
| `skahaWorkload.namespace` | The Namespace for the User Sessions | `skaha-workload` |
| `secrets` | Any secrets to be created at install. | `{}` |
| `traefik.install` | Whether to install Traefik | `false` |
| `traefik` | Traefik configuration options | See [Traefik Chart](https://doc.traefik.io/traefik/getting-started/install-traefik/#use-the-helm-chart) |
