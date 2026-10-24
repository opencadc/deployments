{{/*
OpenCADC CADC-Tomcat configuration file bodies.
Values: application.*, tomcat.*, ingress, httpRoute (from chart + library/common + env overlays).
*/}}

{{- define "common.tomcat.cadcRegistry.properties" -}}
{{- $ctx := .context | default . -}}
{{- $app := $ctx.Values.application | default dict -}}
{{- range $app.localAuthorities | default list }}
{{ required "localAuthorities[].standardId" .standardId }} = {{ required "localAuthorities[].authority" .authority }}
{{- end }}
{{- with $app.gmsId }}
ivo://ivoa.net/std/GMS#search-1.0 = {{ . }}
ivo://ivoa.net/std/GMS#search-0.1 = {{ . }}
ivo://ivoa.net/std/UMS#users-0.1 = {{ . }}
ivo://ivoa.net/std/UMS#login-0.1 = {{ . }}
ivo://ivoa.net/std/UMS#reqs-0.1 = {{ . }}
ivo://ivoa.net/std/UMS#resetpass-0.1 = {{ . }}
ivo://ivoa.net/std/UMS#whoami-0.1 = {{ . }}
ivo://ivoa.net/std/GMS#groups-0.1 = {{ . }}
ivo://ivoa.net/std/GMS#groups-1.0 = {{ . }}
ivo://ivoa.net/sso#tls-with-password = {{ . }}
{{- if not $app.oidcUri }}
ivo://ivoa.net/sso#OAuth = {{ . }}
ivo://ivoa.net/sso#OpenID = {{ . }}
{{- end }}
{{- end }}
{{- with $app.oidcUri }}
ivo://ivoa.net/sso#OAuth = {{ . }}
ivo://ivoa.net/sso#OpenID = {{ . }}
{{- end }}
{{- if $app.resourceId }}
ivo://ivoa.net/std/CDP#delegate-1.0 = {{ $app.resourceId }}
ivo://ivoa.net/std/CDP#proxy-1.0 = {{ $app.resourceId }}
{{- else if $app.cdpResourceId }}
ivo://ivoa.net/std/CDP#delegate-1.0 = {{ $app.cdpResourceId }}
ivo://ivoa.net/std/CDP#proxy-1.0 = {{ $app.cdpResourceId }}
{{- end }}
{{- range $app.registryUrls | default list }}
ca.nrc.cadc.reg.client.RegistryClient.baseURL = {{ . }}
{{- end }}
{{- end -}}

{{- define "common.tomcat.cadcLog.properties" -}}
{{- $ctx := .context | default . -}}
{{- $log := $ctx.Values.application.logging | default dict -}}
{{- $users := $log.users | default $log.userDistinguishedNames | default list -}}
{{- range $users }}
user = {{ . }}
{{- end }}
{{- range $log.usernames | default list }}
username = {{ . }}
{{- end }}
{{- range $log.groups | default list }}
group = {{ . }}
{{- end }}
{{- with $log.secret }}
secret = {{ . }}
{{- end }}
{{- end -}}

{{- define "common.tomcat.warRename.conf" -}}
{{- $ctx := .context | default . -}}
{{- $warBase := .warBaseName | default $ctx.Chart.Name -}}
{{- $deployName := $ctx.Values.application.applicationName | default $warBase -}}
{{- if and $deployName (ne $deployName $warBase) -}}
mv {{ $warBase }}.war {{ $deployName }}.war
{{- end -}}
{{- end -}}

{{- define "common.tomcat.catalina.properties" -}}
{{- $ctx := .context | default . -}}
{{- $app := $ctx.Values.application | default dict -}}
{{- $cat := index ($ctx.Values.tomcat | default dict) "catalina" | default dict -}}
{{- $includeTimeouts := true -}}
{{- if hasKey . "includeConnectionDefaults" -}}
{{- $includeTimeouts = .includeConnectionDefaults -}}
{{- end -}}
{{- $includePrincipal := true -}}
{{- if hasKey . "includePrincipalExtractorFlags" -}}
{{- $includePrincipal = .includePrincipalExtractorFlags -}}
{{- end -}}
{{- $includeLog4j := true -}}
{{- if hasKey . "includeLog4jMessageOnly" -}}
{{- $includeLog4j = .includeLog4jMessageOnly -}}
{{- end -}}
{{- if $includeTimeouts }}
tomcat.connector.connectionTimeout={{ $cat.connectionTimeout | default 180000 }}
tomcat.connector.keepAliveTimeout={{ $cat.keepAliveTimeout | default 180000 }}
{{- end }}
{{- $connectorProps := include "common.tomcatConnector.properties" (dict "context" $ctx) | trim -}}
{{- if $connectorProps }}
{{ $connectorProps }}
{{- end }}
{{- $identityManager := include "common.tomcat.catalina.identityManagerProperty" (dict "context" $ctx) | trim -}}
{{- if $identityManager }}
{{ $identityManager }}
{{- end }}
{{- if $includePrincipal -}}
{{- if hasKey $app "enableClientCertHeader" }}
ca.nrc.cadc.auth.PrincipalExtractor.enableClientCertHeader={{ $app.enableClientCertHeader }}
{{- end }}
{{- if hasKey $app "allowBasicAtp" }}
ca.nrc.cadc.auth.PrincipalExtractor.allowBasicATP={{ $app.allowBasicAtp }}
{{- end }}
{{- end -}}
{{- if $includeLog4j }}
ca.nrc.cadc.util.Log4jInit.messageOnly=true
{{- end -}}
{{- $extra := .extra | default $app.catalinaExtra | default "" | trim -}}
{{- if $extra }}
{{ $extra }}
{{- end -}}
{{- end -}}

{{- define "common.tomcat.catalina.identityManagerProperty" -}}
{{- $class := .class | default "" | trim -}}
{{- if not $class -}}
{{- $ctx := .context | default . -}}
{{- $class = $ctx.Values.application.identityManagerClass | default "" | trim -}}
{{- end -}}
{{- if $class -}}
ca.nrc.cadc.auth.IdentityManager={{ $class }}
{{- end -}}
{{- end -}}
