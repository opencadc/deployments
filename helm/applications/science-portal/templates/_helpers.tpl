{{/*
Obtain a comma-delimited string of Experimental Features and a flag to set if any are enabled.
*/}}
{{- define "sciencePortal.experimentalFeatureGates" -}}
{{- $features := "" -}}
{{- $featureEnabled := false -}}

{{- with .Values.experimentalFeatures -}}

{{- if .enabled -}}
{{- range $feature, $map := . -}}

{{/* Skip the 'enabled' key itself */}}
{{- if and (ne $feature "enabled") (ne $feature "") -}}
{{- $thisMap := $map | default dict }}

{{- if or (not (hasKey $thisMap "enabled")) (not (kindIs "bool" $thisMap.enabled)) -}}
{{- fail ( printf "Feature gate '%s' must have 'enabled' (false | true) key" $feature ) -}}
{{- end }}

{{- if eq $features "" -}}
{{- $features = printf "%s=%t" $feature $thisMap.enabled -}}
{{- else -}}
{{- $features = printf "%s,%s=%t" $features $feature $thisMap.enabled -}}
{{- end -}}

{{- end -}}
{{/* End check for enabled key to skip */}}

{{- end -}}
{{/* End range */}}

{{- printf "%s" $features -}}

{{- end -}}
{{/* End global if enabled */}}

{{- end -}}
{{/* End with */}}

{{- end -}}
