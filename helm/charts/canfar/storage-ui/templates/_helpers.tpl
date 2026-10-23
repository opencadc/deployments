{{/*
Resolve the Kubernetes Secret name containing the OIDC client secret.

Preferred configuration (current):

  application.oidc.clientSecret:
    existingSecret: my-oidc-client
    secretKey: clientSecret   # optional, defaults to "clientSecret"

Backward compatible configuration (deprecated):

  application.oidc.existingSecretName: my-oidc-client

In the deprecated form the key is assumed to be "clientSecret".
*/}}
{{- define "storageui.oidc.clientSecret.existingSecret" -}}
{{- $oidc := .Values.application.oidc | default dict }}
{{- $cs := $oidc.clientSecret | default dict }}
{{- if and $cs $cs.existingSecret }}
{{- $cs.existingSecret }}
{{- else if $oidc.existingSecretName }}
{{- $oidc.existingSecretName }}
{{- end }}
{{- end }}

{{/*
Resolve the key within the OIDC client Secret which holds the client secret value.

When using the clientSecret object, the key defaults to "clientSecret" if not specified.
When using the deprecated existingSecretName, the key is always "clientSecret".
*/}}
{{- define "storageui.oidc.clientSecret.secretKey" -}}
{{- $oidc := .Values.application.oidc | default dict }}
{{- $cs := $oidc.clientSecret | default dict }}
{{- if and $cs $cs.existingSecret }}
{{- $cs.secretKey | default "clientSecret" }}
{{- else if $oidc.existingSecretName }}
{{- "clientSecret" -}}
{{- end }}
{{- end }}
