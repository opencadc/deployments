# Science Portal - Kubernetes Deployment

Essential deployment workflow for Science Portal Next.js to any Kubernetes cluster.

---

## Prerequisites

- `kubectl` configured for your cluster
- `helm` >= 3 installed
- `docker` installed
- Container registry access (Docker Hub, private registry, etc.)

---

## Deployment Workflow

### 1. Clone Repository

```bash
git clone https://github.com/your-org/science-portal-next.git
cd science-portal-next
```

### 2. Build Docker Image

**For CANFAR Mode:**
```bash
docker build \
  --build-arg NEXT_PUBLIC_USE_CANFAR=true \
  --build-arg NEXT_PUBLIC_EXPERIMENTAL=true \
  --build-arg NEXT_PUBLIC_LOGIN_API=https://ws-cadc.canfar.net/ac \
  --build-arg NEXT_PUBLIC_SKAHA_API=https://ws-uv.canfar.net/skaha \
  --build-arg NEXT_PUBLIC_SRC_SKAHA_API=https://src.canfar.net/skaha \
  --build-arg NEXT_PUBLIC_SRC_CAVERN_API=https://src.canfar.net/cavern \
  -t YOUR_REGISTRY/science-portal-nextjs:1.0.0 \
  .
```

**For OIDC Mode:**
```bash
docker build \
  --build-arg NEXT_PUBLIC_USE_CANFAR=false \
  --build-arg NEXT_PUBLIC_EXPERIMENTAL=true \
  --build-arg NEXT_PUBLIC_LOGIN_API=https://ws-cadc.canfar.net/ac \
  --build-arg NEXT_PUBLIC_SKAHA_API=https://ws-uv.canfar.net/skaha \
  --build-arg NEXT_PUBLIC_SRC_SKAHA_API=https://src.canfar.net/skaha \
  --build-arg NEXT_PUBLIC_SRC_CAVERN_API=https://src.canfar.net/cavern \
  -t YOUR_REGISTRY/science-portal-nextjs:1.1.0 \
  .
```

### 3. Push Image

```bash
# Login to registry
docker login YOUR_REGISTRY

# Push image
docker push YOUR_REGISTRY/science-portal-nextjs:1.0.0
```

### 4. Create Namespace and Secrets

```bash
# Create namespace
kubectl create namespace science-portal

# Create application secret
kubectl create secret generic science-portal-secrets \
  --from-literal=auth-secret=$(openssl rand -base64 32) \
  --from-literal=oidc-client-secret=YOUR_OIDC_SECRET \
  --namespace science-portal

# Create registry pull secret (if using private registry)
kubectl create secret docker-registry registry-secret \
  --docker-server=YOUR_REGISTRY \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_PASSWORD \
  --docker-email=YOUR_EMAIL \
  --namespace science-portal
```

### 5. Configure Helm Values

Create `helm/science-portal/values-custom.yaml`:

```yaml
replicaCount: 2

image:
  repository: YOUR_REGISTRY/science-portal-nextjs
  pullPolicy: IfNotPresent
  tag: "1.0.0"

imagePullSecrets:
  - name: registry-secret

service:
  type: ClusterIP
  port: 80
  targetPort: 3000

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: your-domain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: science-portal-tls
      hosts:
        - your-domain.com

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 6
  targetCPUUtilizationPercentage: 80

env:
  # Server-side APIs
  - name: SERVICE_STORAGE_API
    value: "https://ws-uv.canfar.net/arc/nodes/home/"
  - name: LOGIN_API
    value: "https://ws-cadc.canfar.net/ac"
  - name: SKAHA_API
    value: "https://ws-uv.canfar.net/skaha"
  - name: SRC_SKAHA_API
    value: "https://src.canfar.net/skaha"
  - name: SRC_CAVERN_API
    value: "https://src.canfar.net/cavern"
  - name: API_TIMEOUT
    value: "30000"

  # Client-side APIs
  - name: NEXT_PUBLIC_LOGIN_API
    value: "https://ws-cadc.canfar.net/ac"
  - name: NEXT_PUBLIC_SKAHA_API
    value: "https://ws-uv.canfar.net/skaha"
  - name: NEXT_PUBLIC_SRC_SKAHA_API
    value: "https://src.canfar.net/skaha"
  - name: NEXT_PUBLIC_SRC_CAVERN_API
    value: "https://src.canfar.net/cavern"
  - name: NEXT_PUBLIC_API_TIMEOUT
    value: "30000"
  - name: NEXT_PUBLIC_ENABLE_QUERY_DEVTOOLS
    value: "false"
  - name: NEXT_PUBLIC_EXPERIMENTAL
    value: "true"

  # Authentication mode (CANFAR)
  - name: NEXT_USE_CANFAR
    value: "true"
  - name: NEXT_PUBLIC_USE_CANFAR
    value: "true"

  # NextAuth
  - name: AUTH_TRUST_HOST
    value: "true"
  - name: NEXTAUTH_URL
    value: "https://your-domain.com"

secrets:
  existingSecret: "science-portal-secrets"
  keys:
    authSecret: "auth-secret"
    oidcClientSecret: "oidc-client-secret"

# OIDC Configuration (for OIDC mode)
oidc:
  uri: "https://ska-iam.stfc.ac.uk/"
  clientId: "YOUR_CLIENT_ID"
  callbackUri: "https://your-domain.com/science-portal"
  redirectUri: "https://your-domain.com/api/auth/callback/oidc"
  scope: "openid profile offline_access"

networkPolicy:
  enabled: false

podDisruptionBudget:
  enabled: true
  minAvailable: 1
```

### 6. Deploy with Helm

```bash
helm install science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-custom.yaml \
  --namespace science-portal \
  --wait
```

### 7. Verify Deployment

```bash
# Check pods
kubectl get pods -n science-portal

# Check all resources
kubectl get all -n science-portal

# View logs
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal -f
```

---

## Update Deployment

```bash
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-custom.yaml \
  --namespace science-portal
```

## Switch Authentication Mode

Update `values-custom.yaml`:
```yaml
image:
  tag: "1.1.0"  # OIDC mode

env:
  - name: NEXT_USE_CANFAR
    value: "false"
  - name: NEXT_PUBLIC_USE_CANFAR
    value: "false"
```

Then upgrade:
```bash
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-custom.yaml \
  --namespace science-portal
```

---

## Common Commands

```bash
# View logs
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal --tail=50

# Restart deployment
kubectl rollout restart deployment/science-portal -n science-portal

# Scale replicas
kubectl scale deployment science-portal --replicas=3 -n science-portal

# Port forward (testing without ingress)
kubectl port-forward -n science-portal svc/science-portal 3000:80

# Uninstall
helm uninstall science-portal -n science-portal
```

---

## Required Updates

Before deploying, update `values-custom.yaml`:

1. `image.repository` → Your registry path
2. `imagePullSecrets[0].name` → Your registry secret name
3. `ingress.hosts[0].host` → Your domain
4. `ingress.tls[0].hosts[0]` → Your domain
5. `env[*].NEXTAUTH_URL` → Your domain URL
6. `oidc.clientId` → Your OIDC client ID (if using OIDC mode)
7. `oidc.callbackUri` → Your domain callback (if using OIDC mode)
8. `oidc.redirectUri` → Your domain redirect (if using OIDC mode)
