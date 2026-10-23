# common (library chart)

Shared **default values** and **templates** for OpenCADC Tomcat-style application charts. This chart installs no Kubernetes resources.

Location: `helm/library/common` (see [SPECIFICATION.md](../../SPECIFICATION.md)).

## Use in an application chart

```yaml
# Chart.yaml
dependencies:
  - name: common
    version: "0.2.0"
    repository: "file://../../library/common"
    import-values:
      - standard
```

After `helm dependency build`, keys under `exports.standard` are merged onto the **parent chart root** (`ingress`, `service`, `podSecurityContext`, shared `application.*`, etc.).

The application chart keeps **service-specific** keys in its own `values.yaml` (image, probes, secrets, etc.).

Deploy-time overlays: [environments/README.md](../../environments/README.md).

## Template helpers (`common.*`)

All helpers take chart root `$` or `dict "context" $`.

### Naming and labels

| Helper | Purpose |
| --- | --- |
| `common.name` | Short app name |
| `common.fullname` | Release-qualified name |
| `common.chart` | Chart label value |
| `common.selectorLabels` | Selector labels |
| `common.labels` | Recommended labels |
| `common.serviceAccountName` | SA name from `serviceAccount.*` |

### Tomcat

| Helper | Purpose |
| --- | --- |
| `common.tomcatConnector` | YAML: `proxyName`, `scheme`, `proxyPort`, `secure` (empty if internal-only) |
| `common.tomcatConnector.properties` | Lines for `catalina.properties` |
| `common.tomcat.configmap` | Full Tomcat ConfigMap manifest (catalina, registry, cadcLog, optional WAR rename) |

### Ingress / Gateway API

| Helper | Purpose |
| --- | --- |
| `common.ingress` | Ingress resource from `.Values.ingress` |
| `common.httpRoute` | HTTPRoute resource from `.Values.httpRoute` |

### Volumes

| Helper | Purpose |
| --- | --- |
| `common.volumes.projectedConfig` | ConfigMap + list of Secret item mounts |
| `common.volumes.configMap` | ConfigMap-only volume |

### Legacy (science-platform charts)

| Helper | Purpose |
| --- | --- |
| `common.util.merge` | Merge two YAML template fragments |
| `common.extraConfig` | Extra ConfigMap keys (`.key` suffix = base64 decode) |
| `common.image` | Image string from registry/repository/tag/digest object |
| `common.configmap` / `common.configmap.tpl` | ConfigMap merge base |
| `getSecretKeyValue` | Lookup Secret key (requires live cluster) |

## Lint

```bash
helm lint helm/library/common
```
