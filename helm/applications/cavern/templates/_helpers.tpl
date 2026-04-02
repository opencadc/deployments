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
Fail when UWS DB is configured without an existing Secret for credentials (Git-safe / Argo CD).
*/}}
{{- define "cavern.validateUwsDatabaseSecret" -}}
{{- $db := .Values.deployment.cavern.uws.db -}}
{{- $auth := $db.auth | default dict -}}
{{- if not $auth.existingSecret -}}
{{- fail "deployment.cavern.uws.db.auth.existingSecret must name a Kubernetes Secret (same namespace) with UWS DB credentials. Do not commit passwords in Git; use kubectl create secret, Sealed Secrets, or External Secrets. Default keys: username, password (override with auth.secretKeys)." -}}
{{- end -}}
{{- end -}}
