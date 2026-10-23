{{- define "common.tomcat.configmap" -}}
{{- $ctx := .context | required "common.tomcat.configmap: context is required" -}}
{{- $name := .name | required "common.tomcat.configmap: name is required" -}}
{{- $labels := .labels | required "common.tomcat.configmap: labels is required" -}}
{{- $includeWarRename := true -}}
{{- if hasKey . "includeWarRename" -}}
{{- $includeWarRename = .includeWarRename -}}
{{- end -}}
{{- $omitCadcLog := false -}}
{{- if hasKey . "omitCadcLog" -}}
{{- $omitCadcLog = .omitCadcLog -}}
{{- end -}}
{{- $catalinaArgs := dict "context" $ctx -}}
{{- range $k, $v := (.catalina | default dict) -}}
{{- $_ := set $catalinaArgs $k $v -}}
{{- end -}}
{{- $warRename := "" -}}
{{- if $includeWarRename -}}
{{- $warRename = include "common.tomcat.warRename.conf" (dict "context" $ctx "warBaseName" (.warBaseName | default "")) | trim -}}
{{- end -}}
{{- $catalina := include "common.tomcat.catalina.properties" $catalinaArgs | trim -}}
{{- $registry := include "common.tomcat.cadcRegistry.properties" (dict "context" $ctx) | trim -}}
{{- $cadcLog := include "common.tomcat.cadcLog.properties" (dict "context" $ctx) | trim -}}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ $name }}
  {{- with .namespace }}
  namespace: {{ . }}
  {{- end }}
  labels:
    {{- $labels | nindent 4 }}
{{- with .binaryData }}
binaryData:
  {{- range $key, $val := . }}
  {{ $key }}: {{ $val | quote }}
  {{- end }}
{{- end }}
data:
  catalina.properties: |-
{{ $catalina | nindent 4 }}
  cadc-registry.properties: |-
{{ $registry | nindent 4 }}
{{- if or (not $omitCadcLog) $cadcLog }}
  cadc-log.properties: |-
{{ $cadcLog | nindent 4 }}
{{- end }}
{{- if $warRename }}
  war-rename.conf: |-
{{ $warRename | nindent 4 }}
{{- end }}
{{- range $key, $content := .extraData | default dict }}
  {{ $key }}: |-
{{ $content | trim | nindent 4 }}
{{- end }}
{{- end -}}
