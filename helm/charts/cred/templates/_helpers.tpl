{{/*
Expand the name of the chart.
*/}}
{{- define "cred.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "cred.fullname" -}}
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
{{- define "cred.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "cred.labels" -}}
helm.sh/chart: {{ include "cred.chart" . }}
{{ include "cred.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "cred.selectorLabels" -}}
app.kubernetes.io/name: {{ include "cred.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "cred.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "cred.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Public hostname for Tomcat connector settings. Empty when the service is
ClusterIP-only (no HTTPRoute or Ingress hostname).
*/}}
{{- define "cred.hostname" -}}
{{- if .Values.httpRoute.enabled -}}
{{- if .Values.httpRoute.hostnames -}}
{{- index .Values.httpRoute.hostnames 0 -}}
{{- end -}}
{{- else if .Values.ingress.enabled -}}
{{- if .Values.ingress.hosts -}}
{{- (index .Values.ingress.hosts 0).host -}}
{{- end -}}
{{- end -}}
{{- end }}
