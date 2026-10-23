{{/*
Standard Helm naming and labels (helm create style).

All helpers take the chart root context $ or dict "context" $.
Optional dict key "serviceAccountNameSuffix" for serviceAccountName (default: use fullname).
*/}}
{{- define "common.name" -}}
{{- $ctx := .context | default . -}}
{{- default $ctx.Chart.Name $ctx.Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end -}}

{{- define "common.fullname" -}}
{{- $ctx := .context | default . -}}
{{- if $ctx.Values.fullnameOverride -}}
{{- $ctx.Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else -}}
{{- $name := default $ctx.Chart.Name $ctx.Values.nameOverride }}
{{- if contains $name $ctx.Release.Name -}}
{{- $ctx.Release.Name | trunc 63 | trimSuffix "-" }}
{{- else -}}
{{- printf "%s-%s" $ctx.Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "common.chart" -}}
{{- $ctx := .context | default . -}}
{{- printf "%s-%s" $ctx.Chart.Name $ctx.Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end -}}

{{- define "common.selectorLabels" -}}
{{- $ctx := .context | default . -}}
app.kubernetes.io/name: {{ include "common.name" $ctx }}
app.kubernetes.io/instance: {{ $ctx.Release.Name }}
{{- end -}}

{{- define "common.labels" -}}
{{- $ctx := .context | default . -}}
helm.sh/chart: {{ include "common.chart" $ctx }}
{{ include "common.selectorLabels" $ctx }}
{{- if $ctx.Chart.AppVersion }}
app.kubernetes.io/version: {{ $ctx.Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ $ctx.Release.Service }}
{{- end -}}

{{- define "common.serviceAccountName" -}}
{{- $ctx := .context | default . -}}
{{- if $ctx.Values.serviceAccount.create -}}
{{- default (include "common.fullname" $ctx) $ctx.Values.serviceAccount.name }}
{{- else -}}
{{- default "default" $ctx.Values.serviceAccount.name }}
{{- end -}}
{{- end -}}
