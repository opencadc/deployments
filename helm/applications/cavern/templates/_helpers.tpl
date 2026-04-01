{{/*
Fail when UWS DB is configured without an existing Secret for credentials (Git-safe / Argo CD).
*/}}
{{- define "cavern.validateUwsDatabaseSecret" -}}
{{- $db := .Values.deployment.cavern.uws.db -}}
{{- $auth := $db.auth | default dict -}}
{{- if not $auth.existingSecret -}}
{{- fail "deployment.cavern.uws.db.auth.existingSecret must name a Kubernetes Secret (same namespace) with UWS DB credentials. Do not commit passwords in Git; use kubectl create secret, Sealed Secrets, or External Secrets. Default keys: username, password (override with auth.secretKeys)." -}}
{{- end -}}
{{- end -}}
