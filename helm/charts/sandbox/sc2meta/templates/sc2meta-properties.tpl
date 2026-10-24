{{- define "sc2meta.catalina.properties" -}}
{{- with .Values.application.uws }}
sc2meta.uws.maxActive = {{ .maxActive | default 2 }}
sc2meta.uws.url = {{ required "Set the URL for the UWS database (application.uws.url)" .url }}
sc2meta.uws.username = {{ required "Set the username for the UWS database (application.uws.username)" .username }}
sc2meta.uws.password = {{ required "Set the password for the UWS database (application.uws.password)" .password }}
{{- end }}
{{- end -}}
