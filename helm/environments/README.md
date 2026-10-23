# Environment value overlays

Deploy-time YAML merged with application chart values. Not part of the OCI chart package.

## Layout

```text
environments/<site-or-env>/
  _common.yaml    # ingress, registry, tomcat connector, shared application.* 
  cred.yaml       # optional cred-only overrides
  reg.yaml
```

## Example install

```bash
helm dependency build helm/charts/cred
helm upgrade --install cred helm/charts/cred \
  -f helm/environments/example-org/_common.yaml \
  -f helm/environments/example-org/cred.yaml \
  --namespace cred --create-namespace
```

Common keys are **top-level** (`ingress`, `application`, `tomcat`, …), matching `library/common`.
