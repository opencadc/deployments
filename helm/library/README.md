# Library charts

Helm charts with `type: library` (not installable). See [SPECIFICATION.md](../SPECIFICATION.md).

| Chart | Role |
| --- | --- |
| [common](common/) | Shared **default values** (`exports.standard`) and **templates** (Tomcat ConfigMap, ingress, HTTPRoute, naming, volumes) |

Application charts depend on **common** once:

```yaml
dependencies:
  - name: common
    version: "0.2.0"
    repository: "file://../../library/common"
    import-values:
      - standard
```

Legacy charts that only need `extraConfig` or `common.image` may omit `import-values`.

Deploy-time site settings: [environments/README.md](../environments/README.md).
