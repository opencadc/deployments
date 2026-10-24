{{- define "argus.catalina.properties" -}}
{{- with .Values.application.uws }}
org.opencadc.argus.uws.maxActive = {{ .maxActive | default 2 }}
org.opencadc.argus.uws.url = {{ required "Set the URL for the UWS database (application.uws.url)" .url }}
org.opencadc.argus.uws.username = {{ required "Set the username for the UWS database (application.uws.username)" .username }}
org.opencadc.argus.uws.password = {{ required "Set the password for the UWS database (application.uws.password)" .password }}
{{- end }}
{{- with .Values.application.tapadm }}
org.opencadc.argus.tapadm.maxActive = {{ .maxActive | default 2 }}
org.opencadc.argus.tapadm.username = {{ required "Set the username for the TAPADM database (application.tapadm.username)" .username }}
org.opencadc.argus.tapadm.password = {{ required "Set the password for the TAPADM database (application.tapadm.password)" .password }}
org.opencadc.argus.tapadm.url = {{ required "Set the URL for the TAPADM database (application.tapadm.url)" .url }}
{{- end }}
{{- with .Values.application.query }}
org.opencadc.argus.query.maxActive = {{ .maxActive | default 2 }}
org.opencadc.argus.query.username = {{ required "Set the username for the QUERY database (application.query.username)" .username }}
org.opencadc.argus.query.password = {{ required "Set the password for the QUERY database (application.query.password)" .password }}
org.opencadc.argus.query.url = {{ required "Set the URL for the QUERY database (application.query.url)" .url }}
{{- end }}
{{- end -}}

{{- define "argus.app.properties" -}}
{{- with .Values.application.materializedViews }}
{{- if .enabled }}
org.opencadc.argus.enableMaterializedViews = {{ .enabled }}
{{- end }}
{{- end }}
{{- end -}}

{{- define "argus.tapTmp.properties" -}}
# specify implementation in case the DelegatingStorageManager is used
org.opencadc.tap.tmp.StorageManager = org.opencadc.tap.tmp.TempStorageManager

# TempStorageManager config
{{- $block := include "common.tomcatConnector" (dict "context" . "required" true) -}}
{{- $conn := $block | fromYaml -}}
org.opencadc.tap.tmp.TempStorageManager.baseURL = {{ $conn.scheme }}://{{ $conn.proxyName }}/argus/results
org.opencadc.tap.tmp.TempStorageManager.baseStorageDir = /tmp
{{- end -}}
