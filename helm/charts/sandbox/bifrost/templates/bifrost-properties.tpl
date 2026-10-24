{{- define "bifrost.catalina.properties" -}}
{{- with .Values.application.uws }}
org.opencadc.bifrost.uws.maxActive = {{ .maxActive | default 2 }}
org.opencadc.bifrost.uws.url = {{ required "Set the URL for the UWS database (application.uws.url)" .url }}
org.opencadc.bifrost.uws.username = {{ required "Set the username for the UWS database (application.uws.username)" .username }}
org.opencadc.bifrost.uws.password = {{ required "Set the password for the UWS database (application.uws.password)" .password }}
{{- end }}
{{- end -}}

{{- define "bifrost.app.properties" -}}
# CAOM TAP service
org.opencadc.bifrost.queryService = {{ required "Set application.queryService for the CAOM TAP service" .Values.application.queryService }}

# artifact locator service
org.opencadc.bifrost.locatorService = {{ required "Set application.locatorService for the artifact locator service" .Values.application.locatorService }}

# read grant providers (optional)
org.opencadc.bifrost.readGrantProvider = {{ .Values.application.readGrantProvider }}
{{- end -}}
