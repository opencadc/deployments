{{- define "search.name" -}}
{{- include "common.name" . -}}
{{- end }}

{{- define "search.fullname" -}}
{{- include "common.fullname" . -}}
{{- end }}

{{- define "search.chart" -}}
{{- include "common.chart" . -}}
{{- end }}

{{- define "search.selectorLabels" -}}
{{- include "common.selectorLabels" . -}}
{{- end }}

{{- define "search.labels" -}}
{{- include "common.labels" . -}}
{{- end }}

{{- define "search.serviceAccountName" -}}
{{- include "common.serviceAccountName" . -}}
{{- end }}
