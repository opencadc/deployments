{{/*
Expand the name of the chart.
*/}}
{{- define "science-portal.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "science-portal.fullname" -}}
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
{{- define "science-portal.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "science-portal.labels" -}}
helm.sh/chart: {{ include "science-portal.chart" . }}
{{ include "science-portal.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "science-portal.selectorLabels" -}}
app.kubernetes.io/name: {{ include "science-portal.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "science-portal.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "science-portal.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Trim slashes from app.basePath for joining (NEXT_PUBLIC_BASE_PATH style).
*/}}
{{- define "science-portal.trimmedBasePath" -}}
{{- trimPrefix "/" (trimSuffix "/" (default "" .Values.app.basePath)) -}}
{{- end }}

{{/*
HTTP path for probes: app root (returns 200). Must match the URL prefix the app serves
(NEXT_PUBLIC_BASE_PATH / app.basePath). When basePath is unset, defaults to /science-portal.
*/}}
{{- define "science-portal.httpProbePath" -}}
{{- $b := include "science-portal.trimmedBasePath" . -}}
{{- if $b }}/{{ $b }}{{- else -}}/science-portal{{- end -}}
{{- end }}

{{- define "science-portal.healthPathLiveness" -}}
{{- include "science-portal.httpProbePath" . -}}
{{- end }}

{{- define "science-portal.healthPathReadiness" -}}
{{- include "science-portal.httpProbePath" . -}}
{{- end }}
