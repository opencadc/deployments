{{/*
Tomcat reverse-proxy / catalina.properties connector helpers.

Values convention (all optional unless required mode):
  tomcat:
    connector:
      proxyName: ""
      scheme: ""
      proxyPort: ""

Public hostname resolution order (when proxyName unset):
  1. httpRoute.hostnames[0] when httpRoute.enabled
  2. ingress.hosts[0].host when ingress.enabled

common.tomcatConnector — dict keys:
  context (required): chart root $
  required (optional): if true, fail when hostname cannot be resolved

Returns YAML with proxyName, scheme, proxyPort, secure when proxyName resolves,
otherwise empty (unless required: true).
*/}}
{{- define "common.tomcatConnector" -}}
{{- $ctx := .context | default . -}}
{{- $required := .required | default false -}}
{{- $conn := index ($ctx.Values.tomcat | default dict) "connector" | default dict -}}
{{- if $ctx.Values.tomcat.connector -}}
{{- $conn = merge $conn $ctx.Values.tomcat.connector -}}
{{- end -}}
{{- $proxyName := $conn.proxyName | default "" -}}
{{- $scheme := $conn.scheme | default "" -}}
{{- $proxyPort := $conn.proxyPort | default "" -}}
{{- if not $proxyName -}}
{{- if and $ctx.Values.httpRoute.enabled $ctx.Values.httpRoute.hostnames (gt (len $ctx.Values.httpRoute.hostnames) 0) -}}
{{- $proxyName = index $ctx.Values.httpRoute.hostnames 0 -}}
{{- else if and $ctx.Values.ingress.enabled $ctx.Values.ingress.hosts (gt (len $ctx.Values.ingress.hosts) 0) -}}
{{- $proxyName = (index $ctx.Values.ingress.hosts 0).host -}}
{{- end -}}
{{- end -}}
{{- if not $proxyName -}}
{{- if $required -}}
{{- fail "common.tomcatConnector: set tomcat.connector.proxyName, or enable httpRoute.hostnames / ingress.hosts" -}}
{{- end -}}
{{- else -}}
{{- if not $scheme -}}
{{- if $ctx.Values.httpRoute.enabled -}}
{{- $scheme = "https" -}}
{{- else if $ctx.Values.ingress.enabled -}}
{{- if $ctx.Values.ingress.tls -}}
{{- $scheme = "https" -}}
{{- else -}}
{{- $scheme = "http" -}}
{{- end -}}
{{- else -}}
{{- $scheme = "https" -}}
{{- end -}}
{{- end -}}
{{- if not $proxyPort -}}
{{- if eq ($scheme | toString) "https" -}}
{{- $proxyPort = 443 -}}
{{- else -}}
{{- $proxyPort = 80 -}}
{{- end -}}
{{- end -}}
{{- $secure := $conn.secure -}}
{{- if eq ($secure | toString) "" -}}
{{- if eq ($scheme | toString) "https" -}}
{{- $secure = true -}}
{{- else -}}
{{- $secure = false -}}
{{- end -}}
{{- end -}}
proxyName: {{ $proxyName | quote }}
scheme: {{ $scheme | quote }}
proxyPort: {{ $proxyPort }}
secure: {{ $secure }}
{{- end -}}
{{- end -}}

{{/*
Emit catalina.properties connector lines (no leading spaces). Pipe into a properties file block.
*/}}
{{- define "common.tomcatConnector.properties" -}}
{{- $block := include "common.tomcatConnector" . -}}
{{- if $block -}}
{{- $conn := $block | fromYaml -}}
tomcat.connector.scheme={{ $conn.scheme }}
tomcat.connector.proxyName={{ $conn.proxyName }}
tomcat.connector.proxyPort={{ $conn.proxyPort }}
tomcat.connector.secure={{ $conn.secure }}
{{- end -}}
{{- end -}}
