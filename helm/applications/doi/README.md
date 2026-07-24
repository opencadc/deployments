# doi

Digital Object Identifier service Helm chart.

This chart deploys the CADC DOI Tomcat service. Non-secret configuration is rendered into a ConfigMap under `/config`; DataCite credentials and the required `doiadmin.pem` and `cadcproxy.pem` files are read from Kubernetes Secrets and merged into the runtime config by an init container.

## Required Secrets

Create a Secret for DataCite credentials:

```shell
kubectl create secret generic doi-datacite \
  --from-literal=username='<username>' \
  --from-literal=password='<password>'
```

Create a Secret for service certificates:

```shell
kubectl create secret generic doi-certs \
  --from-file=doiadmin.pem=./doiadmin.pem \
  --from-file=cadcproxy.pem=./cadcproxy.pem
```

Set:

```yaml
deployment:
  doi:
    datacite:
      auth:
        existingSecret: doi-datacite
    certificates:
      existingSecret: doi-certs
```

## Example Values

Start from `examples/values.example.yaml` and replace the example hostnames, registry IDs, VOSpace URI, DataCite account prefix, and Secret names.

## Test the Chart

Render and lint the chart with non-secret placeholder Secret names:

```shell
helm lint helm/applications/doi \
  --set deployment.doi.datacite.auth.existingSecret=doi-datacite \
  --set deployment.doi.certificates.existingSecret=doi-certs \
  --set deployment.doi.config.accountPrefix=10.5072

helm template doi helm/applications/doi \
  --namespace doi \
  --set deployment.doi.datacite.auth.existingSecret=doi-datacite \
  --set deployment.doi.certificates.existingSecret=doi-certs \
  --set deployment.doi.config.accountPrefix=10.5072
```

Dry-run against a cluster:

```shell
helm upgrade --install doi helm/applications/doi \
  --namespace doi \
  --create-namespace \
  --values helm/applications/doi/examples/values.example.yaml \
  --dry-run
```

Install after replacing the example values and creating the required Secrets:

```shell
helm upgrade --install doi helm/applications/doi \
  --namespace doi \
  --create-namespace \
  --values <your-values.yaml>
```

Check the workload:

```shell
kubectl -n doi get pods
kubectl -n doi logs deploy/doi-tomcat
kubectl -n doi port-forward svc/doi-tomcat-svc 18080:8080
curl http://localhost:18080/doi/availability
```
