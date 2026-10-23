{{- define "cred.name" -}}
{{- include "common.name" . -}}
{{- end }}

{{- define "cred.fullname" -}}
{{- include "common.fullname" . -}}
{{- end }}

{{- define "cred.chart" -}}
{{- include "common.chart" . -}}
{{- end }}

{{- define "cred.selectorLabels" -}}
{{- include "common.selectorLabels" . -}}
{{- end }}

{{- define "cred.labels" -}}
{{- include "common.labels" . -}}
{{- end }}

{{- define "cred.serviceAccountName" -}}
{{- include "common.serviceAccountName" . -}}
{{- end }}
