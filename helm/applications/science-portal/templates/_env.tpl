{{/*
Container env entries derived from structured app configuration.
Call as: include "science-portal.generatedEnv" (dict "root" . "skipNames" $skipDict)
skipNames: map of env var names already set in .Values.env (those win; chart skips duplicates).
*/}}
{{- define "science-portal.generatedEnv" }}
{{- $root := .root }}
{{- $skip := default dict .skipNames }}
{{- if and $root.Values.app.basePath (ne $root.Values.app.basePath "") }}
{{- if not (hasKey $skip "NEXT_PUBLIC_BASE_PATH") }}
- name: NEXT_PUBLIC_BASE_PATH
  value: {{ $root.Values.app.basePath | quote }}
{{- end }}
{{- end }}
{{- if kindIs "bool" $root.Values.app.useCanfar }}
{{- if not (hasKey $skip "NEXT_USE_CANFAR") }}
- name: NEXT_USE_CANFAR
  value: {{ ternary "true" "false" $root.Values.app.useCanfar | quote }}
{{- end }}
{{- if not (hasKey $skip "NEXT_PUBLIC_USE_CANFAR") }}
- name: NEXT_PUBLIC_USE_CANFAR
  value: {{ ternary "true" "false" $root.Values.app.useCanfar | quote }}
{{- end }}
{{- end }}
{{- with $root.Values.app.api }}
{{- if and .storage (not (hasKey $skip "SERVICE_STORAGE_API")) }}
- name: SERVICE_STORAGE_API
  value: {{ .storage | quote }}
{{- end }}
{{- if and .login (not (hasKey $skip "LOGIN_API")) }}
- name: LOGIN_API
  value: {{ .login | quote }}
{{- end }}
{{- if and .skaha (not (hasKey $skip "SKAHA_API")) }}
- name: SKAHA_API
  value: {{ .skaha | quote }}
{{- end }}
{{- if and .srcSkaha (not (hasKey $skip "SRC_SKAHA_API")) }}
- name: SRC_SKAHA_API
  value: {{ .srcSkaha | quote }}
{{- end }}
{{- if and .srcCavern (not (hasKey $skip "SRC_CAVERN_API")) }}
- name: SRC_CAVERN_API
  value: {{ .srcCavern | quote }}
{{- end }}
{{- if and (hasKey . "timeoutMs") (ne (toString .timeoutMs) "") (not (hasKey $skip "API_TIMEOUT")) }}
- name: API_TIMEOUT
  value: {{ .timeoutMs | toString | quote }}
{{- end }}
{{- end }}
{{- $legacyPublicApi := $root.Values.app.publicApi | default dict }}
{{- $pub := $root.Values.app.public | default dict }}
{{- $pubApi := merge ($pub.api | default dict) $legacyPublicApi }}
{{- with $pubApi }}
{{- if and .login (not (hasKey $skip "NEXT_PUBLIC_LOGIN_API")) }}
- name: NEXT_PUBLIC_LOGIN_API
  value: {{ .login | quote }}
{{- end }}
{{- if and .skaha (not (hasKey $skip "NEXT_PUBLIC_SKAHA_API")) }}
- name: NEXT_PUBLIC_SKAHA_API
  value: {{ .skaha | quote }}
{{- end }}
{{- if and .srcSkaha (not (hasKey $skip "NEXT_PUBLIC_SRC_SKAHA_API")) }}
- name: NEXT_PUBLIC_SRC_SKAHA_API
  value: {{ .srcSkaha | quote }}
{{- end }}
{{- if and .srcCavern (not (hasKey $skip "NEXT_PUBLIC_SRC_CAVERN_API")) }}
- name: NEXT_PUBLIC_SRC_CAVERN_API
  value: {{ .srcCavern | quote }}
{{- end }}
{{- if and (hasKey . "timeoutMs") (ne (toString .timeoutMs) "") (not (hasKey $skip "NEXT_PUBLIC_API_TIMEOUT")) }}
- name: NEXT_PUBLIC_API_TIMEOUT
  value: {{ .timeoutMs | toString | quote }}
{{- end }}
{{- end }}
{{- with ($pub.services | default dict) }}
{{- if and .storageManagement (not (hasKey $skip "NEXT_PUBLIC_SERVICE_STORAGE_MANAGEMENT_URL")) }}
- name: NEXT_PUBLIC_SERVICE_STORAGE_MANAGEMENT_URL
  value: {{ .storageManagement | quote }}
{{- end }}
{{- if and .groupManagement (not (hasKey $skip "NEXT_PUBLIC_SERVICE_GROUP_MANAGEMENT_URL")) }}
- name: NEXT_PUBLIC_SERVICE_GROUP_MANAGEMENT_URL
  value: {{ .groupManagement | quote }}
{{- end }}
{{- if and .dataPublication (not (hasKey $skip "NEXT_PUBLIC_SERVICE_DATA_PUBLICATION_URL")) }}
- name: NEXT_PUBLIC_SERVICE_DATA_PUBLICATION_URL
  value: {{ .dataPublication | quote }}
{{- end }}
{{- if and .sciencePortal (not (hasKey $skip "NEXT_PUBLIC_SERVICE_SCIENCE_PORTAL_URL")) }}
- name: NEXT_PUBLIC_SERVICE_SCIENCE_PORTAL_URL
  value: {{ .sciencePortal | quote }}
{{- end }}
{{- if and .cadcSearch (not (hasKey $skip "NEXT_PUBLIC_SERVICE_CADC_SEARCH_URL")) }}
- name: NEXT_PUBLIC_SERVICE_CADC_SEARCH_URL
  value: {{ .cadcSearch | quote }}
{{- end }}
{{- if and .openstackCloud (not (hasKey $skip "NEXT_PUBLIC_SERVICE_OPENSTACK_CLOUD_URL")) }}
- name: NEXT_PUBLIC_SERVICE_OPENSTACK_CLOUD_URL
  value: {{ .openstackCloud | quote }}
{{- end }}
{{- end }}
{{- if and (kindIs "bool" $root.Values.app.experimental) (not (hasKey $skip "NEXT_PUBLIC_EXPERIMENTAL")) }}
- name: NEXT_PUBLIC_EXPERIMENTAL
  value: {{ ternary "true" "false" $root.Values.app.experimental | quote }}
{{- end }}
{{- if and (kindIs "bool" $root.Values.app.enableQueryDevtools) (not (hasKey $skip "NEXT_PUBLIC_ENABLE_QUERY_DEVTOOLS")) }}
- name: NEXT_PUBLIC_ENABLE_QUERY_DEVTOOLS
  value: {{ ternary "true" "false" $root.Values.app.enableQueryDevtools | quote }}
{{- end }}
{{- if and $root.Values.app.oidc.enabled $root.Values.app.oidc.uri }}
{{- $o := $root.Values.app.oidc }}
{{- if not (hasKey $skip "NEXT_OIDC_URI") }}
- name: NEXT_OIDC_URI
  value: {{ $o.uri | quote }}
{{- end }}
{{- if not (hasKey $skip "NEXT_PUBLIC_OIDC_URI") }}
- name: NEXT_PUBLIC_OIDC_URI
  value: {{ $o.uri | quote }}
{{- end }}
{{- if and $o.clientId (not (hasKey $skip "NEXT_OIDC_CLIENT_ID")) }}
- name: NEXT_OIDC_CLIENT_ID
  value: {{ $o.clientId | quote }}
{{- end }}
{{- if and $o.clientId (not (hasKey $skip "NEXT_PUBLIC_OIDC_CLIENT_ID")) }}
- name: NEXT_PUBLIC_OIDC_CLIENT_ID
  value: {{ $o.clientId | quote }}
{{- end }}
{{- if and $o.callbackUri (not (hasKey $skip "NEXT_OIDC_CALLBACK_URI")) }}
- name: NEXT_OIDC_CALLBACK_URI
  value: {{ $o.callbackUri | quote }}
{{- end }}
{{- if and $o.callbackUri (not (hasKey $skip "NEXT_PUBLIC_OIDC_CALLBACK_URI")) }}
- name: NEXT_PUBLIC_OIDC_CALLBACK_URI
  value: {{ $o.callbackUri | quote }}
{{- end }}
{{- if and $o.redirectUri (not (hasKey $skip "NEXT_OIDC_REDIRECT_URI")) }}
- name: NEXT_OIDC_REDIRECT_URI
  value: {{ $o.redirectUri | quote }}
{{- end }}
{{- if and $o.redirectUri (not (hasKey $skip "NEXT_PUBLIC_OIDC_REDIRECT_URI")) }}
- name: NEXT_PUBLIC_OIDC_REDIRECT_URI
  value: {{ $o.redirectUri | quote }}
{{- end }}
{{- if and $o.scope (not (hasKey $skip "NEXT_OIDC_SCOPE")) }}
- name: NEXT_OIDC_SCOPE
  value: {{ $o.scope | quote }}
{{- end }}
{{- if and $o.scope (not (hasKey $skip "NEXT_PUBLIC_OIDC_SCOPE")) }}
- name: NEXT_PUBLIC_OIDC_SCOPE
  value: {{ $o.scope | quote }}
{{- end }}
{{- if and $o.clientSecret.existingSecret $o.clientSecret.secretKey (not (hasKey $skip "NEXT_OIDC_CLIENT_SECRET")) }}
- name: NEXT_OIDC_CLIENT_SECRET
  valueFrom:
    secretKeyRef:
      name: {{ $o.clientSecret.existingSecret | quote }}
      key: {{ $o.clientSecret.secretKey | quote }}
{{- end }}
{{- end }}
{{- with $root.Values.app.auth }}
{{- if and (kindIs "bool" .trustHost) (not (hasKey $skip "AUTH_TRUST_HOST")) }}
- name: AUTH_TRUST_HOST
  value: {{ ternary "true" "false" .trustHost | quote }}
{{- end }}
{{- if and .nextauthUrl (not (hasKey $skip "NEXTAUTH_URL")) }}
- name: NEXTAUTH_URL
  value: {{ .nextauthUrl | quote }}
{{- end }}
{{- if and .authSecret.existingSecret .authSecret.secretKey (not (hasKey $skip "AUTH_SECRET")) }}
- name: AUTH_SECRET
  valueFrom:
    secretKeyRef:
      name: {{ .authSecret.existingSecret | quote }}
      key: {{ .authSecret.secretKey | quote }}
{{- end }}
{{- end }}
{{- end }}
