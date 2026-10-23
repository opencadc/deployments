# Science Platform Helm library (`common`)

The shared library chart lives at [`helm/library/common`](../../../helm/library/common/). It replaces the former `helm/applications/utils` chart.

See [common README](../../../helm/library/common/README.md) for dependencies and template helpers (`common.*`, `getSecretKeyValue`).

```yaml
dependencies:
  - name: common
    version: "0.2.0"
    repository: "file://../../library/common"
```

Legacy science-platform charts may omit `import-values` if they only use `common.extraConfig` or `common.image`.
