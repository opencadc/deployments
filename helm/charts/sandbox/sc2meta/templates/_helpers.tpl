{{- define "sc2meta.name" -}}
{{- include "common.name" . -}}
{{- end }}

{{- define "sc2meta.fullname" -}}
{{- include "common.fullname" . -}}
{{- end }}

{{- define "sc2meta.chart" -}}
{{- include "common.chart" . -}}
{{- end }}

{{- define "sc2meta.selectorLabels" -}}
{{- include "common.selectorLabels" . -}}
{{- end }}

{{- define "sc2meta.labels" -}}
{{- include "common.labels" . -}}
{{- end }}

{{- define "sc2meta.serviceAccountName" -}}
{{- include "common.serviceAccountName" . -}}
{{- end }}
