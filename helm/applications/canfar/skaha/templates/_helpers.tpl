{{/*
Expand the name of the chart.
*/}}
{{- define "skaha.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "skaha.fullname" -}}
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
{{- define "skaha.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "skaha.labels" -}}
helm.sh/chart: {{ include "skaha.chart" . }}
{{ include "skaha.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "skaha.selectorLabels" -}}
app.kubernetes.io/name: {{ include "skaha.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "skaha.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "skaha.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
USER SESSION TEMPLATE DEFINITIONS
*/}}

{{/*
The Home VOSpace Node URI (uses vos:// scheme) for the User Home directory in Cavern.
*/}}
{{- define "skaha.job.userStorage.homeURI" -}}
{{- $nodeURIPrefix := trimAll "/" (required ".Values.sessions.userStorage.nodeURIPrefix nodeURIPrefix is required." .Values.sessions.userStorage.nodeURIPrefix) -}}
{{- $homeDirectoryName := trimAll "/" (required ".Values.sessions.userStorage.homeDirectory home folder name is required." .Values.sessions.userStorage.homeDirectory) -}}
{{- printf "%s/%s" $nodeURIPrefix $homeDirectoryName -}}
{{- end -}}

{{/*
The Home Directory base absolute path.
*/}}
{{- define "skaha.job.userStorage.homeBaseDirectory" -}}
{{- $topLevelDirectory := trimAll "/" (required ".Values.sessions.userStorage.topLevelDirectory topLevelDirectory is required." .Values.sessions.userStorage.topLevelDirectory) -}}
{{- $homeDirectoryName := trimAll "/" (required ".Values.sessions.userStorage.homeDirectory home folder name is required." .Values.sessions.userStorage.homeDirectory) -}}
{{- printf "/%s/%s" $topLevelDirectory $homeDirectoryName -}}
{{- end -}}

{{/*
The Projects Directory base absolute path.
*/}}
{{- define "skaha.job.userStorage.projectsBaseDirectory" -}}
{{- $topLevelDirectory := trimAll "/" (required ".Values.sessions.userStorage.topLevelDirectory topLevelDirectory is required." .Values.sessions.userStorage.topLevelDirectory) -}}
{{- $projectsDirectoryName := trimAll "/" (required ".Values.sessions.userStorage.projectsDirectory projects folder name is required." .Values.sessions.userStorage.projectsDirectory) -}}
{{- printf "/%s/%s" $topLevelDirectory $projectsDirectoryName -}}
{{- end -}}
