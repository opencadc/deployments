{{/*
Expand the name of the chart.
*/}}
{{- define "cavern.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "cavern.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "cavern.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "cavern.selectorLabels" -}}
app.kubernetes.io/name: {{ include "cavern.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "cavern.labels" -}}
helm.sh/chart: {{ include "cavern.chart" . }}
{{ include "cavern.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Kubernetes Secret name for UWS DB credentials: user-supplied existingSecret, or chart-generated name when using deprecated inline username/password.
*/}}
{{- define "cavern.uwsDbAuthSecretName" -}}
{{- $auth := .Values.deployment.cavern.uws.db.auth | default dict -}}
{{- if $auth.existingSecret -}}
{{- $auth.existingSecret -}}
{{- else -}}
{{- printf "%s-uws-db-creds" .Release.Name -}}
{{- end -}}
{{- end -}}

{{/*
Effective inline UWS DB username: auth.username, else legacy deployment.cavern.uws.db.username (2026.1-era values).
*/}}
{{- define "cavern.uwsDbInlineUsername" -}}
{{- $db := .Values.deployment.cavern.uws.db -}}
{{- $auth := $db.auth | default dict -}}
{{- default "" (coalesce $auth.username $db.username) -}}
{{- end -}}

{{/*
Effective inline UWS DB password: auth.password, else legacy deployment.cavern.uws.db.password.
*/}}
{{- define "cavern.uwsDbInlinePassword" -}}
{{- $db := .Values.deployment.cavern.uws.db -}}
{{- $auth := $db.auth | default dict -}}
{{- default "" (coalesce $auth.password $db.password) -}}
{{- end -}}

{{/*
Require either auth.existingSecret (recommended) or deprecated inline credentials (auth.username + auth.password, or legacy db.username + db.password; chart creates a Secret).
*/}}
{{- define "cavern.validateUwsDatabaseSecret" -}}
{{- $auth := .Values.deployment.cavern.uws.db.auth | default dict -}}
{{- $u := include "cavern.uwsDbInlineUsername" . | trim -}}
{{- $p := include "cavern.uwsDbInlinePassword" . | trim -}}
{{- if not (empty $auth.existingSecret) -}}
{{- else if and (not (empty $u)) (not (empty $p)) -}}
{{- else -}}
{{- fail "deployment.cavern.uws.db.auth: set existingSecret to a Kubernetes Secret in this namespace (recommended), or set non-empty username and password under auth (deprecated), or legacy db.username and db.password (deprecated; see NOTES.txt). Keys default to username/password (override with auth.secretKeys)." -}}
{{- end -}}
{{- end -}}

{{/*
Validate deployment.cavern.adminAPIKeys: each entry is either a string (deprecated) or a map with existingSecret and key.
*/}}
{{- define "cavern.validateAdminAPIKeys" -}}
{{- range $clientName, $spec := .Values.deployment.cavern.adminAPIKeys }}
{{- if kindIs "map" $spec }}
{{- $_ := $spec.existingSecret | required (printf "deployment.cavern.adminAPIKeys[%s].existingSecret is required when using a secret reference" $clientName) }}
{{- $_ := $spec.key | required (printf "deployment.cavern.adminAPIKeys[%s].key is required when using a secret reference (key field in the Kubernetes Secret)" $clientName) }}
{{- else if not (kindIs "string" $spec) }}
{{- fail (printf "deployment.cavern.adminAPIKeys[%s] must be a string (deprecated) or a map with existingSecret and key" $clientName) }}
{{- end }}
{{- end }}
{{- end -}}
