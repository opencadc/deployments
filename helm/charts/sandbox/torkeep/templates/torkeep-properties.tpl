{{- define "torkeep.catalina.properties" -}}
{{- with .Values.application.caom2Metadata }}
org.opencadc.torkeep.caom2.maxActive = {{ .maxActive | default 2 }}
org.opencadc.torkeep.caom2.url = {{ required "Set the URL for the CAOM-2 database (application.caom2Metadata.url)" .url }}
org.opencadc.torkeep.caom2.username = {{ required "Set the username for the CAOM-2 database (application.caom2Metadata.username)" .username }}
org.opencadc.torkeep.caom2.password = {{ required "Set the password for the CAOM-2 database (application.caom2Metadata.password)" .password }}
{{- end }}
{{- end -}}

{{- define "torkeep.app.properties" -}}
# permission services (one per line) that provide read and write grants
{{- range .Values.application.grantProviders }}
org.opencadc.torkeep.grantProvider = {{ . }}
{{- end }}

# collection name and one or more collection properties
{{- range .Values.application.collections }}
org.opencadc.torkeep.collection = {{ required "Set the collection name" .name }}
{{ .name }}.basePublisherID = {{ required (printf "Set the basePublisherID for collection %s" .name) .basePublisherID }}
{{ .name }}.computeMetadata = {{ required (printf "Set the computeMetadata flag {true | false} for collection %s" .name) .computeMetadata }}
{{ .name }}.proposalGroup = {{ required (printf "Set the proposalGroup flag {true | false} for collection %s" .name) .proposalGroup }}
{{- end }}
{{- end -}}
