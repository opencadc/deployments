{{/*
Expand the name of the chart.
*/}}
{{- define "doi.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "doi.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "doi.selectorLabels" -}}
app.kubernetes.io/name: {{ include "doi.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "doi.labels" -}}
helm.sh/chart: {{ include "doi.chart" . }}
{{ include "doi.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
DataCite credential Secret name.
*/}}
{{- define "doi.dataciteAuthSecretName" -}}
{{- required "deployment.doi.datacite.auth.existingSecret is required" .Values.deployment.doi.datacite.auth.existingSecret -}}
{{- end -}}

{{/*
PEM certificate Secret name.
*/}}
{{- define "doi.certificateSecretName" -}}
{{- required "deployment.doi.certificates.existingSecret is required" .Values.deployment.doi.certificates.existingSecret -}}
{{- end -}}
