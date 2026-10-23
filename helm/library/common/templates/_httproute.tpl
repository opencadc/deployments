{{/*
Renders a gateway.networking.k8s.io/v1 HTTPRoute when .Values.httpRoute.enabled on context.

Required dict keys:
  context — chart root $
  name — metadata.name
  labels — rendered label string (no nindent)
  serviceName — backend Service name
  servicePort — backend Service port number

Optional:
  namespace — metadata.namespace
*/}}
{{- define "common.httpRoute" -}}
{{- $ctx := .context | required "common.httpRoute: context is required" -}}
{{- if $ctx.Values.httpRoute.enabled -}}
{{- $name := .name | required "common.httpRoute: name is required" -}}
{{- $labels := .labels | required "common.httpRoute: labels is required" -}}
{{- $serviceName := .serviceName | required "common.httpRoute: serviceName is required" -}}
{{- $servicePort := .servicePort | required "common.httpRoute: servicePort is required" -}}
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: {{ $name }}
  {{- with .namespace }}
  namespace: {{ . }}
  {{- end }}
  labels:
    {{- $labels | nindent 4 }}
  {{- with $ctx.Values.httpRoute.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  parentRefs:
    {{- with $ctx.Values.httpRoute.parentRefs }}
      {{- toYaml . | nindent 4 }}
    {{- end }}
  {{- with $ctx.Values.httpRoute.hostnames }}
  hostnames:
    {{- toYaml . | nindent 4 }}
  {{- end }}
  rules:
    {{- range $ctx.Values.httpRoute.rules }}
    {{- with .matches }}
    - matches:
      {{- toYaml . | nindent 8 }}
    {{- end }}
    {{- with .filters }}
      filters:
      {{- toYaml . | nindent 8 }}
    {{- end }}
      backendRefs:
        - name: {{ $serviceName }}
          port: {{ $servicePort }}
          weight: 1
    {{- end }}
{{- end -}}
{{- end -}}
