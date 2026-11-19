# cred

![Version: 2.0.4](https://img.shields.io/badge/Version-2.0.4-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 2.0.3](https://img.shields.io/badge/AppVersion-2.0.3-informational?style=flat-square)

A Helm chart to deploy the Credential service to manage X509 client certificates.

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| application.allowBasicATP | bool | `true` |  |
| application.applicationName | string | `"cred"` |  |
| application.availabilityPath | string | `"/cred/availability"` |  |
| application.cadcproxy.existingSecret | string | `""` |  |
| application.cadcproxy.key | string | `"cadcproxy.pem"` |  |
| application.cookieSignaturePublicKey.existingSecret | string | `""` |  |
| application.cookieSignaturePublicKey.key | string | `"RsaSignaturePub.key"` |  |
| application.enableClientCertHeader | bool | `true` |  |
| application.gmsID | string | `""` |  |
| application.identityManagerClass | string | `"ca.nrc.cadc.ac.ACIdentityManager"` |  |
| application.maxDaysValid | string | `"30.0"` |  |
| application.oidcURI | string | `""` |  |
| application.registryURL | string | `""` |  |
| application.resourceID | string | `""` |  |
| application.signingCert.existingSecret | string | `"cred-signcert"` |  |
| application.signingCert.key | string | `"signcert.pem"` |  |
| application.superUsers | list | `[]` |  |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| env | list | `[]` |  |
| envFrom | list | `[]` |  |
| fullnameOverride | string | `""` |  |
| httpRoute | object | `{"annotations":{},"enabled":false,"hostnames":["chart-example.local"],"parentRefs":[{"name":"gateway","sectionName":"http"}],"rules":[{"matches":[{"path":{"type":"PathPrefix","value":"/cred"}}]}]}` | Expose the service via gateway-api HTTPRoute Requires Gateway API resources and suitable controller installed within the cluster (see: https://gateway-api.sigs.k8s.io/guides/) |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"images.opencadc.org/core/cred"` |  |
| image.tag | string | `"2.0.4-20260929T175724"` |  |
| imagePullSecrets | list | `[]` |  |
| ingress.annotations | object | `{}` |  |
| ingress.className | string | `""` |  |
| ingress.enabled | bool | `false` |  |
| ingress.hosts[0].host | string | `"chart-example.local"` |  |
| ingress.hosts[0].paths[0].path | string | `"/cred"` |  |
| ingress.hosts[0].paths[0].pathType | string | `"Prefix"` |  |
| ingress.tls | list | `[]` |  |
| livenessProbe.httpGet.path | string | `"/cred/availability"` |  |
| livenessProbe.httpGet.port | string | `"http"` |  |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` |  |
| podAnnotations | object | `{}` |  |
| podLabels | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| readinessProbe.httpGet.path | string | `"/cred/availability"` |  |
| readinessProbe.httpGet.port | string | `"http"` |  |
| replicaCount | int | `1` |  |
| resources | object | `{}` |  |
| securityContext | object | `{}` |  |
| service.port | int | `8080` |  |
| service.type | string | `"ClusterIP"` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.automount | bool | `true` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` |  |
| tolerations | list | `[]` |  |
| volumeMounts | list | `[]` |  |
| volumes | list | `[]` |  |
