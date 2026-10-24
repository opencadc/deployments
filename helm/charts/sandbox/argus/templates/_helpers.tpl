{{- define "argus.name" -}}
{{- include "common.name" . -}}
{{- end }}

{{- define "argus.fullname" -}}
{{- include "common.fullname" . -}}
{{- end }}

{{- define "argus.chart" -}}
{{- include "common.chart" . -}}
{{- end }}

{{- define "argus.selectorLabels" -}}
{{- include "common.selectorLabels" . -}}
{{- end }}

{{- define "argus.labels" -}}
{{- include "common.labels" . -}}
{{- end }}

{{- define "argus.serviceAccountName" -}}
{{- include "common.serviceAccountName" . -}}
{{- end }}
