{{- define "bifrost.name" -}}
{{- include "common.name" . -}}
{{- end }}

{{- define "bifrost.fullname" -}}
{{- include "common.fullname" . -}}
{{- end }}

{{- define "bifrost.chart" -}}
{{- include "common.chart" . -}}
{{- end }}

{{- define "bifrost.selectorLabels" -}}
{{- include "common.selectorLabels" . -}}
{{- end }}

{{- define "bifrost.labels" -}}
{{- include "common.labels" . -}}
{{- end }}

{{- define "bifrost.serviceAccountName" -}}
{{- include "common.serviceAccountName" . -}}
{{- end }}
