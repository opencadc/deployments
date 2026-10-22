# Environment overlays

Domain- or cluster-specific Helm values (no chart templates). See [SPECIFICATION.md](../SPECIFICATION.md) and [ADR 0003](../../docs/adr/0003-deployment-domains-via-environment-overlays.md).

Add one directory per deployment target, for example:

```text
environments/<domain-or-env>/
├── _common.yaml      # shared ingress, global.baseDomain, gateway refs
├── ac.yaml
├── cred.yaml
└── reg.yaml
```

Do not commit secrets; reference existing Kubernetes Secrets in value files.
