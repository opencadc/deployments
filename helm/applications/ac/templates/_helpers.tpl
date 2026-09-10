{{/* Expand the chart name. */}}
{{- define "ac.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Create a fully qualified application name. */}}
{{- define "ac.fullname" -}}
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

{{/* Chart name and version label. */}}
{{- define "ac.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Common labels. */}}
{{- define "ac.labels" -}}
helm.sh/chart: {{ include "ac.chart" . }}
{{ include "ac.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/* Selector labels. */}}
{{- define "ac.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ac.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* Service account name. */}}
{{- define "ac.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "ac.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/* Public proxy hostname, preferring the first Ingress host. */}}
{{- define "ac.tomcatConnectorProxyName" -}}
{{- if .Values.tomcat.connector.proxyName -}}
{{- .Values.tomcat.connector.proxyName -}}
{{- else if and .Values.ingress.enabled .Values.ingress.hosts (gt (len .Values.ingress.hosts) 0) -}}
{{- (index .Values.ingress.hosts 0).host -}}
{{- else -}}
{{- fail "ac: set tomcat.connector.proxyName or enable ingress with at least one host" -}}
{{- end -}}
{{- end }}

{{/* Public proxy scheme. */}}
{{- define "ac.tomcatConnectorScheme" -}}
{{- .Values.tomcat.connector.scheme -}}
{{- end }}

{{/* Public proxy port. */}}
{{- define "ac.tomcatConnectorProxyPort" -}}
{{- .Values.tomcat.connector.proxyPort | toString -}}
{{- end }}
