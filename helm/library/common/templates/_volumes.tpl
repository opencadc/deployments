{{/*
Projected pod volume: ConfigMap plus optional Secret file mounts (cred/reg pattern).

Dict keys:
  volumeName (required)
  configMapName (required)
  defaultMode (optional) — default 0444
  secrets (optional) — list of:
      existingSecret (required)
      items (required) — list of { key, path }

Returns a single volumes[] entry (use with nindent on Deployment).

Example:
  volumes:
    {{- include "common.volumes.projectedConfig" (dict
        "volumeName" "config"
        "configMapName" (printf "%s-config" (include "cred.fullname" .))
        "secrets" (list
          (dict "existingSecret" "signing" "items" (list (dict "key" "signcert.pem" "path" "signcert.pem")))
        )
      ) | nindent 4 }}
*/}}
{{- define "common.volumes.projectedConfig" -}}
{{- $volumeName := .volumeName | required "common.volumes.projectedConfig: volumeName is required" -}}
{{- $configMapName := .configMapName | required "common.volumes.projectedConfig: configMapName is required" -}}
{{- $defaultMode := .defaultMode | default 0444 -}}
- name: {{ $volumeName }}
  projected:
    defaultMode: {{ $defaultMode }}
    sources:
      - configMap:
          name: {{ $configMapName }}
      {{- range .secrets | default list }}
      - secret:
          name: {{ .existingSecret | required "common.volumes.projectedConfig: secrets[].existingSecret is required" }}
          items:
            {{- range .items | required "common.volumes.projectedConfig: secrets[].items is required" }}
            - key: {{ .key | quote }}
              path: {{ .path | quote }}
            {{- end }}
      {{- end }}
{{- end -}}

{{/*
Simple config-only volume (reg without extra secrets).
*/}}
{{- define "common.volumes.configMap" -}}
{{- $volumeName := .volumeName | required "common.volumes.configMap: volumeName is required" -}}
{{- $configMapName := .configMapName | required "common.volumes.configMap: configMapName is required" -}}
- name: {{ $volumeName }}
  configMap:
    name: {{ $configMapName }}
{{- end -}}
