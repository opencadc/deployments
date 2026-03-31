{{/*
Expand the name of the chart.
*/}}
{{- define "access.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "access.fullname" -}}
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
{{- define "access.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "access.labels" -}}
helm.sh/chart: {{ include "access.chart" . }}
{{ include "access.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "access.selectorLabels" -}}
app.kubernetes.io/name: {{ include "access.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "access.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "access.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Secret that holds RsaSignaturePub.key / RsaSignaturePriv.key (chart-created or existing).
*/}}
{{- define "access.rsaSignatureSecretName" -}}
{{- if .Values.rsaSignatureKeys.existingSecret -}}
{{- .Values.rsaSignatureKeys.existingSecret -}}
{{- else -}}
{{- printf "%s-rsa-signature-keys" (include "access.fullname" .) -}}
{{- end -}}
{{- end }}

{{/*
Fail the render unless either an existing Secret is set or both PEMs are provided for a chart Secret.
*/}}
{{- define "access.validateRsaSignatureKeys" -}}
{{- if .Values.rsaSignatureKeys.existingSecret -}}
{{- else if and .Values.rsaSignatureKeys.publicKey .Values.rsaSignatureKeys.privateKey -}}
{{- else -}}
{{- fail "access: set rsaSignatureKeys.existingSecret to a Secret containing RsaSignaturePub.key and RsaSignaturePriv.key, or set rsaSignatureKeys.publicKey and rsaSignatureKeys.privateKey (PEM) for a chart-managed Secret" -}}
{{- end -}}
{{- end }}

{{/*
Tomcat catalina.properties connector settings: prefer Ingress, then HTTPRoute, else optional
tomcat.connector overrides. tomcat and tomcat.connector may be omitted (see index/default fallbacks).
*/}}
{{- define "access.tomcatConnectorProxyName" -}}
{{- if and .Values.ingress.enabled .Values.ingress.hosts (gt (len .Values.ingress.hosts) 0) -}}
{{- (index .Values.ingress.hosts 0).host -}}
{{- else if and .Values.httpRoute.enabled .Values.httpRoute.hostnames (gt (len .Values.httpRoute.hostnames) 0) -}}
{{- index .Values.httpRoute.hostnames 0 -}}
{{- else -}}
{{- $conn := index (.Values.tomcat | default dict) "connector" | default dict -}}
{{- index $conn "proxyName" | default "hostname.example.com" -}}
{{- end -}}
{{- end }}

{{- define "access.tomcatConnectorScheme" -}}
{{- if and .Values.ingress.enabled .Values.ingress.hosts (gt (len .Values.ingress.hosts) 0) -}}
{{- if and .Values.ingress.tls (gt (len .Values.ingress.tls) 0) -}}https{{- else -}}http{{- end -}}
{{- else if and .Values.httpRoute.enabled .Values.httpRoute.hostnames (gt (len .Values.httpRoute.hostnames) 0) -}}
https
{{- else -}}
{{- $conn := index (.Values.tomcat | default dict) "connector" | default dict -}}
{{- index $conn "scheme" | default "https" -}}
{{- end -}}
{{- end }}

{{- define "access.tomcatConnectorProxyPort" -}}
{{- if and .Values.ingress.enabled .Values.ingress.hosts (gt (len .Values.ingress.hosts) 0) -}}
{{- if and .Values.ingress.tls (gt (len .Values.ingress.tls) 0) -}}443{{- else -}}80{{- end -}}
{{- else if and .Values.httpRoute.enabled .Values.httpRoute.hostnames (gt (len .Values.httpRoute.hostnames) 0) -}}
443
{{- else -}}
{{- $conn := index (.Values.tomcat | default dict) "connector" | default dict -}}
{{- index $conn "proxyPort" | default "443" | toString -}}
{{- end -}}
{{- end }}
