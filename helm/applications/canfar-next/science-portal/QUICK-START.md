# Science Portal - Minimal Kubernetes Deployment

Quick start guide for deploying Science Portal Next.js to any Kubernetes cluster with Helm.

---

## Prerequisites

### Required Tools

```bash
kubectl version --client  # Kubernetes CLI
helm version              # Helm 3.x
docker --version          # For building images
```

### Required Access

- Kubernetes cluster with admin access
- Container registry (Docker Hub, DigitalOcean, AWS ECR, etc.)
- Domain name (optional, can use port-forward for testing)

---

## 5-Step Deployment

### Step 1: Connect to Cluster

```bash
# Verify cluster connection
kubectl cluster-info
kubectl get nodes

# Should see your cluster nodes
```

### Step 2: Build and Push Image

```bash
# Login to your registry
docker login  # or doctl registry login, aws ecr get-login, etc.

# Build image
docker build -t YOUR_REGISTRY/science-portal-nextjs:1.0.0 .

# Push image
docker push YOUR_REGISTRY/science-portal-nextjs:1.0.0
```

**Replace `YOUR_REGISTRY` with:**
- Docker Hub: `yourusername`
- DigitalOcean: `registry.digitalocean.com/your-registry`
- AWS ECR: `123456789012.dkr.ecr.us-west-2.amazonaws.com`
- GCR: `gcr.io/your-project-id`

### Step 3: Create Namespace and Secrets

```bash
# Create namespace
kubectl create namespace science-portal

# Create application secret
kubectl create secret generic science-portal-secrets \
  --from-literal=auth-secret=$(openssl rand -base64 32) \
  --namespace science-portal

# Create registry pull secret (if using private registry)
# For Docker Hub:
kubectl create secret docker-registry registry-secret \
  --docker-server=docker.io \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_PASSWORD \
  --docker-email=YOUR_EMAIL \
  --namespace science-portal

# For DigitalOcean:
doctl registry kubernetes-manifest | kubectl apply -f -
kubectl get secret registry-YOUR_REGISTRY -n kube-system -o yaml | \
  sed 's/namespace: kube-system/namespace: science-portal/' | \
  kubectl apply -f -
```

### Step 4: Configure Values

Create `helm/science-portal/values-minimal.yaml`:

```yaml
# Minimal configuration for Science Portal

replicaCount: 1

image:
  repository: YOUR_REGISTRY/science-portal-nextjs
  pullPolicy: IfNotPresent
  tag: "1.0.0"

# Update with your registry secret name
imagePullSecrets:
  - name: registry-secret  # or registry-YOUR_REGISTRY for DO

service:
  type: ClusterIP
  port: 80
  targetPort: 3000

# Disable ingress for minimal setup (use port-forward)
ingress:
  enabled: false

# Minimal resources
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 256Mi

# Disable autoscaling
autoscaling:
  enabled: false

# CANFAR authentication mode
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

  # CANFAR authentication mode
  - name: NEXT_USE_CANFAR
    value: "true"
  - name: NEXT_PUBLIC_USE_CANFAR
    value: "true"

  # NextAuth configuration
  - name: AUTH_TRUST_HOST
    value: "true"
  - name: NEXTAUTH_URL
    value: "http://localhost:3000"

# Secrets reference
secrets:
  existingSecret: "science-portal-secrets"
  keys:
    authSecret: "auth-secret"

# Disable network policies for simplicity
networkPolicy:
  enabled: false

# Disable pod disruption budget
podDisruptionBudget:
  enabled: false
```

**Important:** Update these values:
- `image.repository` - Your registry path
- `imagePullSecrets[0].name` - Your registry secret name

### Step 5: Deploy

```bash
# Deploy with Helm
helm install science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-minimal.yaml \
  --namespace science-portal \
  --wait

# Check deployment
kubectl get pods -n science-portal
```

---

## Access Application

### Option A: Port Forward (No Domain Required)

```bash
# Forward port to your local machine
kubectl port-forward -n science-portal svc/science-portal 3000:80

# Access at http://localhost:3000
```

### Option B: With Domain and Ingress

1. **Install NGINX Ingress Controller:**

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer
```

2. **Get LoadBalancer IP:**

```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller
# Note the EXTERNAL-IP
```

3. **Configure DNS:**

```
Create A record: your-domain.com → [EXTERNAL-IP]
```

4. **Enable Ingress:**

Update `values-minimal.yaml`:

```yaml
ingress:
  enabled: true
  className: "nginx"
  annotations: {}
  hosts:
    - host: your-domain.com
      paths:
        - path: /
          pathType: Prefix
  tls: []  # Add SSL later with cert-manager

env:
  # Update NEXTAUTH_URL
  - name: NEXTAUTH_URL
    value: "http://your-domain.com"
```

5. **Upgrade deployment:**

```bash
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-minimal.yaml \
  --namespace science-portal
```

---

## Verification

### Check Deployment Status

```bash
# View pods
kubectl get pods -n science-portal

# Should show:
# NAME                              READY   STATUS    RESTARTS   AGE
# science-portal-xxxxxxxxxx-xxxxx   1/1     Running   0          2m

# View logs
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal --tail=50

# Check all resources
kubectl get all -n science-portal
```

### Test Application

```bash
# Port forward (if not using ingress)
kubectl port-forward -n science-portal svc/science-portal 3000:80

# Test in browser
open http://localhost:3000

# Or test with curl
curl http://localhost:3000/api/health
```

---

## Common Commands

### View Logs

```bash
# Real-time logs
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal -f

# Logs from specific pod
kubectl logs -n science-portal <pod-name>
```

### Update Deployment

```bash
# After changing values-minimal.yaml
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-minimal.yaml \
  --namespace science-portal
```

### Scale Application

```bash
# Scale to 3 replicas
kubectl scale deployment science-portal --replicas=3 -n science-portal

# Or update values file and helm upgrade
```

### Restart Application

```bash
kubectl rollout restart deployment/science-portal -n science-portal
```

### Uninstall

```bash
# Remove deployment
helm uninstall science-portal -n science-portal

# Delete namespace
kubectl delete namespace science-portal
```

---

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n science-portal

# Common issues:
# - ImagePullBackOff: Check registry credentials
# - CrashLoopBackOff: Check logs for errors
```

### Check Secrets

```bash
# Verify secret exists
kubectl get secret science-portal-secrets -n science-portal

# View secret keys (not values)
kubectl describe secret science-portal-secrets -n science-portal
```

### Test Network Connectivity

```bash
# Test from within cluster
kubectl run test --image=curlimages/curl -it --rm -- \
  curl http://science-portal.science-portal.svc.cluster.local

# Test external APIs
kubectl run test --image=curlimages/curl -it --rm -- \
  curl -I https://ws-uv.canfar.net/skaha/v1/session
```

---

## Next Steps

Once basic deployment works:

1. **Add SSL/TLS** - Install cert-manager and configure HTTPS
2. **Enable Autoscaling** - Set `autoscaling.enabled: true`
3. **Add Monitoring** - Install Prometheus/Grafana
4. **Configure OIDC** - Switch to OIDC authentication mode
5. **Production Hardening** - Enable network policies, resource limits

See [KUBERNETES-DEPLOYMENT-GUIDE.md](./KUBERNETES-DEPLOYMENT-GUIDE.md) for comprehensive configuration.

---

## Minimal Values Reference

```yaml
# Absolute minimum configuration
replicaCount: 1

image:
  repository: YOUR_REGISTRY/science-portal-nextjs
  tag: "1.0.0"

imagePullSecrets:
  - name: registry-secret

ingress:
  enabled: false

autoscaling:
  enabled: false

networkPolicy:
  enabled: false

secrets:
  existingSecret: "science-portal-secrets"
  keys:
    authSecret: "auth-secret"

env:
  - name: NEXT_USE_CANFAR
    value: "true"
  - name: NEXT_PUBLIC_USE_CANFAR
    value: "true"
  - name: AUTH_TRUST_HOST
    value: "true"
```

---

## Quick Deployment Script

Create `deploy-minimal.sh`:

```bash
#!/bin/bash
set -e

# Configuration
NAMESPACE="science-portal"
REGISTRY="YOUR_REGISTRY"
IMAGE_TAG="1.0.0"

echo "🚀 Minimal Science Portal Deployment"

# Step 1: Create namespace
echo "📦 Creating namespace..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Step 2: Create secrets
echo "🔐 Creating secrets..."
kubectl create secret generic science-portal-secrets \
  --from-literal=auth-secret=$(openssl rand -base64 32) \
  --namespace $NAMESPACE \
  --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Deploy with Helm
echo "📊 Deploying with Helm..."
helm upgrade --install science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-minimal.yaml \
  --set image.repository=$REGISTRY/science-portal-nextjs \
  --set image.tag=$IMAGE_TAG \
  --namespace $NAMESPACE \
  --wait

# Step 4: Verify
echo "✅ Checking deployment..."
kubectl get pods -n $NAMESPACE

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Access the application:"
echo "kubectl port-forward -n $NAMESPACE svc/science-portal 3000:80"
echo "Then open: http://localhost:3000"
```

Usage:
```bash
chmod +x deploy-minimal.sh
./deploy-minimal.sh
```

---

## Summary

**Minimal deployment requires:**

1. ✅ Kubernetes cluster
2. ✅ kubectl and helm installed
3. ✅ Docker image in registry
4. ✅ One secret (auth-secret)
5. ✅ Registry pull secret (if private)
6. ✅ Minimal values file with your registry

**You can skip:**
- Ingress (use port-forward)
- SSL certificates
- Autoscaling
- Network policies
- Monitoring
- Pod disruption budgets

**Time to deploy:** ~5 minutes

---

**For production deployments, see:** [KUBERNETES-DEPLOYMENT-GUIDE.md](./KUBERNETES-DEPLOYMENT-GUIDE.md)
