{{- define "torkeep.name" -}}
{{- include "common.name" . -}}
{{- end }}

{{- define "torkeep.fullname" -}}
{{- include "common.fullname" . -}}
{{- end }}

{{- define "torkeep.chart" -}}
{{- include "common.chart" . -}}
{{- end }}

{{- define "torkeep.selectorLabels" -}}
{{- include "common.selectorLabels" . -}}
{{- end }}

{{- define "torkeep.labels" -}}
{{- include "common.labels" . -}}
{{- end }}

{{- define "torkeep.serviceAccountName" -}}
{{- include "common.serviceAccountName" . -}}
{{- end }}
