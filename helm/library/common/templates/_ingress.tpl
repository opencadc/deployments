{{/*
Renders a networking.k8s.io/v1 Ingress when .Values.ingress.enabled on context.

Required dict keys:
  context — chart root $
  name — metadata.name
  labels — rendered label string (no nindent); e.g. (include "reg.labels" .)
  serviceName — backend Service name
  servicePort — backend Service port number

Optional:
  namespace — metadata.namespace (omit for release namespace)
*/}}
{{- define "common.ingress" -}}
{{- $ctx := .context | required "common.ingress: context is required" -}}
{{- if $ctx.Values.ingress.enabled -}}
{{- $name := .name | required "common.ingress: name is required" -}}
{{- $labels := .labels | required "common.ingress: labels is required" -}}
{{- $serviceName := .serviceName | required "common.ingress: serviceName is required" -}}
{{- $servicePort := .servicePort | required "common.ingress: servicePort is required" -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ $name }}
  {{- with .namespace }}
  namespace: {{ . }}
  {{- end }}
  labels:
    {{- $labels | nindent 4 }}
  {{- with $ctx.Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  {{- with $ctx.Values.ingress.className }}
  ingressClassName: {{ . }}
  {{- end }}
  {{- if $ctx.Values.ingress.tls }}
  tls:
    {{- range $ctx.Values.ingress.tls }}
    - hosts:
        {{- range .hosts }}
        - {{ . | quote }}
        {{- end }}
      secretName: {{ .secretName }}
    {{- end }}
  {{- end }}
  rules:
    {{- range $ctx.Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            {{- with .pathType }}
            pathType: {{ . }}
            {{- end }}
            backend:
              service:
                name: {{ $serviceName }}
                port:
                  number: {{ $servicePort }}
          {{- end }}
    {{- end }}
{{- end -}}
{{- end -}}
