# Science Portal - Authentication Modes Deployment Guide

Complete guide for building, deploying, and switching between CANFAR and OIDC authentication modes.

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication Modes](#authentication-modes)
3. [Building Images](#building-images)
4. [Deployment Configuration](#deployment-configuration)
5. [OIDC Setup and Redirect URIs](#oidc-setup-and-redirect-uris)
6. [Switching Between Modes](#switching-between-modes)
7. [Current Deployment Details](#current-deployment-details)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Science Portal supports two authentication methods:

- **CANFAR Mode**: Traditional username/password authentication
- **OIDC Mode**: Modern OAuth2/OpenID Connect authentication via SKA IAM

Each mode requires a **different Docker image** because authentication mode is baked into the Next.js build at compile time via `NEXT_PUBLIC_USE_CANFAR` environment variable.

---

## Authentication Modes

### CANFAR Mode

**Description:** Users log in with CANFAR username and password.

**Features:**
- Direct login form
- Token-based authentication with CANFAR APIs
- No external OAuth provider needed

**APIs Used:**
- Login: `https://ws-cadc.canfar.net/ac/login`
- Session validation via token

**Required Secrets:**
- `AUTH_SECRET` - NextAuth session encryption key

**User Experience:**
```
User visits site → Enters username/password → Direct login → Access granted
```

### OIDC Mode

**Description:** Users authenticate via SKA IAM using OAuth2/OpenID Connect.

**Features:**
- OAuth2 standard flow
- Single Sign-On (SSO) capability
- Token refresh support
- Federated identity

**APIs Used:**
- OIDC Provider: `https://ska-iam.stfc.ac.uk/`
- Authorization, token, and userinfo endpoints

**Required Secrets:**
- `AUTH_SECRET` - NextAuth session encryption key
- `OIDC_CLIENT_SECRET` - OAuth client secret from SKA IAM

**User Experience:**
```
User visits site → Clicks "Sign in with OIDC" → Redirects to SKA IAM →
User logs in at SKA IAM → Redirects back to app → Access granted
```

---

## Building Images

### Why Different Images?

The `NEXT_PUBLIC_USE_CANFAR` variable determines authentication mode at **build time**. This value is embedded in the compiled JavaScript bundle and cannot be changed at runtime.

```dockerfile
# In Dockerfile
ARG NEXT_PUBLIC_USE_CANFAR=true
ENV NEXT_PUBLIC_USE_CANFAR=$NEXT_PUBLIC_USE_CANFAR
RUN npm run build  # This bakes the value into the build
```

### Build CANFAR Mode Image

```bash
# Build with CANFAR mode enabled
docker build \
  --build-arg NEXT_PUBLIC_USE_CANFAR=true \
  --build-arg NEXT_PUBLIC_LOGIN_API=https://ws-cadc.canfar.net/ac \
  --build-arg NEXT_PUBLIC_SKAHA_API=https://ws-uv.canfar.net/skaha \
  --build-arg NEXT_PUBLIC_SRC_SKAHA_API=https://src.canfar.net/skaha \
  --build-arg NEXT_PUBLIC_SRC_CAVERN_API=https://src.canfar.net/cavern \
  --build-arg NEXT_PUBLIC_API_TIMEOUT=30000 \
  --build-arg NEXT_PUBLIC_ENABLE_QUERY_DEVTOOLS=false \
  -t registry.digitalocean.com/ice-image/science-portal-nextjs:1.0.0 \
  -t registry.digitalocean.com/ice-image/science-portal-nextjs:canfar \
  .

# Push to registry
docker push registry.digitalocean.com/ice-image/science-portal-nextjs:1.0.0
docker push registry.digitalocean.com/ice-image/science-portal-nextjs:canfar
```

**Verification during build:**
```
🔍 Server config - CANFAR mode, using CANFAR Storage API
🔍 Server config - CANFAR mode, using CANFAR Skaha API
```

### Build OIDC Mode Image

```bash
# Build with OIDC mode enabled
docker build \
  --build-arg NEXT_PUBLIC_USE_CANFAR=false \
  --build-arg NEXT_PUBLIC_LOGIN_API=https://ws-cadc.canfar.net/ac \
  --build-arg NEXT_PUBLIC_SKAHA_API=https://ws-uv.canfar.net/skaha \
  --build-arg NEXT_PUBLIC_SRC_SKAHA_API=https://src.canfar.net/skaha \
  --build-arg NEXT_PUBLIC_SRC_CAVERN_API=https://src.canfar.net/cavern \
  --build-arg NEXT_PUBLIC_API_TIMEOUT=30000 \
  --build-arg NEXT_PUBLIC_ENABLE_QUERY_DEVTOOLS=false \
  -t registry.digitalocean.com/ice-image/science-portal-nextjs:1.1.0 \
  -t registry.digitalocean.com/ice-image/science-portal-nextjs:1.0.1-oidc \
  -t registry.digitalocean.com/ice-image/science-portal-nextjs:oidc \
  .

# Push to registry
docker push registry.digitalocean.com/ice-image/science-portal-nextjs:1.1.0
docker push registry.digitalocean.com/ice-image/science-portal-nextjs:1.0.1-oidc
docker push registry.digitalocean.com/ice-image/science-portal-nextjs:oidc
```

**Verification during build:**
```
🔍 Server config - OIDC mode, using SRC Cavern API
🔍 Server config - OIDC mode, using SRC Skaha API
⚠️ OIDC config missing - using dummy values (build time)
```

### Build Script

Create `build-mode-images.sh`:

```bash
#!/bin/bash
set -e

REGISTRY="${REGISTRY:-registry.digitalocean.com/ice-image}"
IMAGE_NAME="science-portal-nextjs"
VERSION="${1:-1.0.0}"

echo "Building Science Portal images for both auth modes..."

# Build CANFAR mode
echo "🔨 Building CANFAR mode image..."
docker build \
  --build-arg NEXT_PUBLIC_USE_CANFAR=true \
  --build-arg NEXT_PUBLIC_LOGIN_API=https://ws-cadc.canfar.net/ac \
  --build-arg NEXT_PUBLIC_SKAHA_API=https://ws-uv.canfar.net/skaha \
  --build-arg NEXT_PUBLIC_SRC_SKAHA_API=https://src.canfar.net/skaha \
  --build-arg NEXT_PUBLIC_SRC_CAVERN_API=https://src.canfar.net/cavern \
  --build-arg NEXT_PUBLIC_API_TIMEOUT=30000 \
  --build-arg NEXT_PUBLIC_ENABLE_QUERY_DEVTOOLS=false \
  -t ${REGISTRY}/${IMAGE_NAME}:${VERSION}-canfar \
  -t ${REGISTRY}/${IMAGE_NAME}:canfar \
  .

# Build OIDC mode
echo "🔨 Building OIDC mode image..."
docker build \
  --build-arg NEXT_PUBLIC_USE_CANFAR=false \
  --build-arg NEXT_PUBLIC_LOGIN_API=https://ws-cadc.canfar.net/ac \
  --build-arg NEXT_PUBLIC_SKAHA_API=https://ws-uv.canfar.net/skaha \
  --build-arg NEXT_PUBLIC_SRC_SKAHA_API=https://src.canfar.net/skaha \
  --build-arg NEXT_PUBLIC_SRC_CAVERN_API=https://src.canfar.net/cavern \
  --build-arg NEXT_PUBLIC_API_TIMEOUT=30000 \
  --build-arg NEXT_PUBLIC_ENABLE_QUERY_DEVTOOLS=false \
  -t ${REGISTRY}/${IMAGE_NAME}:${VERSION}-oidc \
  -t ${REGISTRY}/${IMAGE_NAME}:oidc \
  .

# Push both
echo "📤 Pushing images to registry..."
docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}-canfar
docker push ${REGISTRY}/${IMAGE_NAME}:canfar
docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}-oidc
docker push ${REGISTRY}/${IMAGE_NAME}:oidc

echo "✅ Both images built and pushed successfully!"
echo ""
echo "CANFAR mode: ${REGISTRY}/${IMAGE_NAME}:${VERSION}-canfar"
echo "OIDC mode:   ${REGISTRY}/${IMAGE_NAME}:${VERSION}-oidc"
```

**Usage:**
```bash
chmod +x build-mode-images.sh
./build-mode-images.sh 1.0.0
```

### Image Tagging Strategy

| Tag | Mode | Purpose |
|-----|------|---------|
| `1.0.0` | CANFAR | Specific version (legacy/default) |
| `1.1.0` | OIDC | Specific version |
| `1.0.0-canfar` | CANFAR | Explicit mode tag |
| `1.0.1-oidc` | OIDC | Explicit mode tag |
| `canfar` | CANFAR | Latest CANFAR mode |
| `oidc` | OIDC | Latest OIDC mode |

---

## Deployment Configuration

### CANFAR Mode Configuration

**Values file:** `helm/science-portal/values-digitalocean.yaml`

```yaml
# Image - CANFAR mode
image:
  repository: registry.digitalocean.com/ice-image/science-portal-nextjs
  pullPolicy: IfNotPresent
  tag: "1.0.0"  # or "canfar"

# Environment variables
env:
  # Authentication mode - CANFAR
  - name: NEXT_USE_CANFAR
    value: "true"
  - name: NEXT_PUBLIC_USE_CANFAR
    value: "true"

  # Server-side APIs
  - name: SERVICE_STORAGE_API
    value: "https://ws-uv.canfar.net/arc/nodes/home/"
  - name: LOGIN_API
    value: "https://ws-cadc.canfar.net/ac"
  - name: SKAHA_API
    value: "https://ws-uv.canfar.net/skaha"

  # Client-side APIs
  - name: NEXT_PUBLIC_LOGIN_API
    value: "https://ws-cadc.canfar.net/ac"
  - name: NEXT_PUBLIC_SKAHA_API
    value: "https://ws-uv.canfar.net/skaha"

  # NextAuth
  - name: AUTH_TRUST_HOST
    value: "true"
  - name: NEXTAUTH_URL
    value: "https://science-portal-next.testapp.ca"

# Secrets (only AUTH_SECRET needed)
secrets:
  existingSecret: "science-portal-secrets"
  keys:
    authSecret: "auth-secret"
```

**Create secrets:**
```bash
kubectl create secret generic science-portal-secrets \
  --from-literal=auth-secret=$(openssl rand -base64 32) \
  --namespace science-portal
```

**Deploy:**
```bash
helm upgrade --install science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --namespace science-portal \
  --create-namespace \
  --wait
```

### OIDC Mode Configuration

**Values file:** `helm/science-portal/values-digitalocean.yaml`

```yaml
# Image - OIDC mode
image:
  repository: registry.digitalocean.com/ice-image/science-portal-nextjs
  pullPolicy: IfNotPresent
  tag: "1.1.0"  # or "oidc"

# Environment variables
env:
  # Authentication mode - OIDC
  - name: NEXT_USE_CANFAR
    value: "false"
  - name: NEXT_PUBLIC_USE_CANFAR
    value: "false"

  # Server-side APIs (same as CANFAR)
  - name: SERVICE_STORAGE_API
    value: "https://ws-uv.canfar.net/arc/nodes/home/"
  - name: SKAHA_API
    value: "https://ws-uv.canfar.net/skaha"
  - name: SRC_SKAHA_API
    value: "https://src.canfar.net/skaha"
  - name: SRC_CAVERN_API
    value: "https://src.canfar.net/cavern"

  # Client-side APIs
  - name: NEXT_PUBLIC_SKAHA_API
    value: "https://ws-uv.canfar.net/skaha"
  - name: NEXT_PUBLIC_SRC_SKAHA_API
    value: "https://src.canfar.net/skaha"
  - name: NEXT_PUBLIC_SRC_CAVERN_API
    value: "https://src.canfar.net/cavern"

  # NextAuth
  - name: AUTH_TRUST_HOST
    value: "true"
  - name: NEXTAUTH_URL
    value: "https://science-portal-next.testapp.ca"

# OIDC Configuration
oidc:
  uri: "https://ska-iam.stfc.ac.uk/"
  clientId: "83b50c08-25a7-460e-9d03-42500d4f88cb"
  callbackUri: "https://science-portal-next.testapp.ca/science-portal"
  redirectUri: "https://science-portal-next.testapp.ca/api/auth/callback/oidc"
  scope: "openid profile offline_access"

# Secrets (AUTH_SECRET + OIDC_CLIENT_SECRET)
secrets:
  existingSecret: "science-portal-secrets"
  keys:
    authSecret: "auth-secret"
    oidcClientSecret: "oidc-client-secret"
```

**Create secrets:**
```bash
kubectl create secret generic science-portal-secrets \
  --from-literal=auth-secret=$(openssl rand -base64 32) \
  --from-literal=oidc-client-secret="YOUR_OIDC_CLIENT_SECRET" \
  --namespace science-portal
```

**Deploy:**
```bash
helm upgrade --install science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --namespace science-portal \
  --create-namespace \
  --wait
```

---

## OIDC Setup and Redirect URIs

### Overview

OIDC authentication requires proper configuration in **two places**:

1. **Application configuration** (Helm values) ✅
2. **OIDC Provider configuration** (SKA IAM) ⚠️ **YOU MUST DO THIS**

### Redirect URI Flow

```
1. User clicks "Sign in with OIDC"
   ↓
2. App redirects to SKA IAM with:
   redirect_uri=https://science-portal-next.testapp.ca/api/auth/callback/oidc
   ↓
3. User logs in at SKA IAM
   ↓
4. SKA IAM validates redirect_uri against allowed list
   ↓
5. SKA IAM redirects back to:
   https://science-portal-next.testapp.ca/api/auth/callback/oidc?code=...
   ↓
6. App exchanges code for token
   ↓
7. User authenticated and redirected to:
   https://science-portal-next.testapp.ca/science-portal
```

### Required URIs for Current Deployment

**For production (science-portal-next.testapp.ca):**
```
Callback URI:  https://science-portal-next.testapp.ca/science-portal
Redirect URI:  https://science-portal-next.testapp.ca/api/auth/callback/oidc
```

**For local development:**
```
Callback URI:  http://localhost:3000/science-portal
Redirect URI:  http://localhost:3000/api/auth/callback/oidc
```

### Configuring SKA IAM

#### Step 1: Access SKA IAM

1. Go to: https://ska-iam.stfc.ac.uk/
2. Log in with admin credentials
3. Navigate to **Clients** or **Applications**
4. Find your client: `83b50c08-25a7-460e-9d03-42500d4f88cb`

#### Step 2: Update Redirect URIs

Add these URIs to the **Allowed Redirect URIs** list:

```
https://science-portal-next.testapp.ca/science-portal
https://science-portal-next.testapp.ca/api/auth/callback/oidc
http://localhost:3000/science-portal
http://localhost:3000/api/auth/callback/oidc
```

**Important Notes:**
- ✅ URIs must match **exactly** (including protocol, domain, port, and path)
- ✅ Include both production and development URIs
- ✅ Don't include trailing slashes
- ❌ Wildcards are typically not allowed

#### Step 3: Save Configuration

Save the changes in SKA IAM admin panel.

#### Step 4: Verify Configuration

Test OIDC login:

```bash
# Access your application
open https://science-portal-next.testapp.ca

# Click "Sign in with OIDC"
# Should redirect to SKA IAM
# After successful login, should redirect back to your app
```

**Check logs:**
```bash
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal -f | grep -i "oidc\|callback"
```

**Success indicators:**
```
✅ OIDC callback received
✅ Token exchange successful
✅ User authenticated
```

**Error indicators:**
```
❌ redirect_uri_mismatch
❌ Invalid redirect URI
❌ Unauthorized redirect_uri
```

### Multiple Environments

If you deploy to multiple domains, add all redirect URIs to SKA IAM:

```
# Production
https://science-portal.canfar.net/science-portal
https://science-portal.canfar.net/api/auth/callback/oidc

# Staging
https://staging-science-portal.canfar.net/science-portal
https://staging-science-portal.canfar.net/api/auth/callback/oidc

# Test
https://science-portal-next.testapp.ca/science-portal
https://science-portal-next.testapp.ca/api/auth/callback/oidc

# Development
http://localhost:3000/science-portal
http://localhost:3000/api/auth/callback/oidc
```

### Updating Redirect URIs

**When you change the domain:**

1. Update Helm values file:
```yaml
env:
  - name: NEXTAUTH_URL
    value: "https://NEW-DOMAIN.com"

oidc:
  callbackUri: "https://NEW-DOMAIN.com/science-portal"
  redirectUri: "https://NEW-DOMAIN.com/api/auth/callback/oidc"
```

2. Add new URIs to SKA IAM client configuration

3. Deploy with new configuration:
```bash
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --namespace science-portal
```

---

## Switching Between Modes

### Method 1: Using Helm Values File

Edit `helm/science-portal/values-digitalocean.yaml` and change:

**Switch to CANFAR:**
```yaml
image:
  tag: "1.0.0"  # or "canfar"

env:
  - name: NEXT_USE_CANFAR
    value: "true"
  - name: NEXT_PUBLIC_USE_CANFAR
    value: "true"
```

**Switch to OIDC:**
```yaml
image:
  tag: "1.1.0"  # or "oidc"

env:
  - name: NEXT_USE_CANFAR
    value: "false"
  - name: NEXT_PUBLIC_USE_CANFAR
    value: "false"
```

Then deploy:
```bash
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --namespace science-portal \
  --wait
```

### Method 2: Using Helm Set Flags

**Switch to CANFAR:**
```bash
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --set image.tag=1.0.0 \
  --set env[0].value="true" \
  --set env[1].value="true" \
  --namespace science-portal \
  --wait
```

**Switch to OIDC:**
```bash
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --set image.tag=1.1.0 \
  --set env[0].value="false" \
  --set env[1].value="false" \
  --namespace science-portal \
  --wait
```

### Method 3: Dedicated Values Files

Create separate values files for each mode:

**helm/science-portal/values-canfar.yaml:**
```yaml
image:
  tag: "canfar"

env:
  - name: NEXT_USE_CANFAR
    value: "true"
  - name: NEXT_PUBLIC_USE_CANFAR
    value: "true"
  # ... other env vars
```

**helm/science-portal/values-oidc.yaml:**
```yaml
image:
  tag: "oidc"

env:
  - name: NEXT_USE_CANFAR
    value: "false"
  - name: NEXT_PUBLIC_USE_CANFAR
    value: "false"
  # ... other env vars

oidc:
  # ... oidc config
```

**Deploy CANFAR mode:**
```bash
helm upgrade --install science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-canfar.yaml \
  --namespace science-portal
```

**Deploy OIDC mode:**
```bash
helm upgrade --install science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-oidc.yaml \
  --namespace science-portal
```

### Verification After Switch

**Check deployed image:**
```bash
kubectl get deployment science-portal -n science-portal \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
```

**Check environment variables:**
```bash
kubectl get deployment science-portal -n science-portal \
  -o jsonpath='{.spec.template.spec.containers[0].env}' | \
  jq -r '.[] | select(.name | contains("USE_CANFAR"))'
```

**Check logs:**
```bash
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal --tail=20
```

**Look for:**
- CANFAR mode: `🔍 Server config - CANFAR mode`
- OIDC mode: `🔍 Server config - OIDC mode`

---

## Current Deployment Details

### Cluster Information

| Component | Details |
|-----------|---------|
| **Provider** | DigitalOcean Kubernetes (DOKS) |
| **Region** | Toronto (tor1) |
| **Cluster Name** | science-portal-next |
| **Node Pool** | 1 node (s-2vcpu-4gb) |
| **Kubernetes Version** | v1.33.1 |

### Deployment Information

| Component | Details |
|-----------|---------|
| **Namespace** | science-portal |
| **Release Name** | science-portal |
| **Chart** | ./helm/science-portal |
| **Values File** | values-digitalocean.yaml |
| **Replicas** | 2 |
| **HPA** | Enabled (min: 2, max: 6) |

### Network Configuration

| Component | Details |
|-----------|---------|
| **Domain** | science-portal-next.testapp.ca |
| **LoadBalancer IP** | 152.42.146.100 |
| **Ingress Controller** | NGINX (ingress-nginx) |
| **SSL/TLS** | Let's Encrypt (letsencrypt-prod) |
| **Certificate Status** | Valid |

### Container Registry

| Component | Details |
|-----------|---------|
| **Registry** | DigitalOcean Container Registry |
| **Registry Name** | ice-image |
| **Image Path** | registry.digitalocean.com/ice-image/science-portal-nextjs |
| **Pull Secret** | registry-ice-image |

### Available Images

| Tag | Mode | Build Date | Status |
|-----|------|------------|--------|
| **1.0.0** | **CANFAR** | 2025-10-27 | ✅ **Currently Deployed** |
| 1.1.0 | OIDC | 2025-10-27 | Available |
| 1.0.1-oidc | OIDC | 2025-10-27 | Available |

### OIDC Configuration

| Parameter | Value |
|-----------|-------|
| **Provider** | SKA IAM |
| **Provider URI** | https://ska-iam.stfc.ac.uk/ |
| **Client ID** | 83b50c08-25a7-460e-9d03-42500d4f88cb |
| **Callback URI** | https://science-portal-next.testapp.ca/science-portal |
| **Redirect URI** | https://science-portal-next.testapp.ca/api/auth/callback/oidc |
| **Scope** | openid profile offline_access |

### Secrets

| Secret Name | Keys | Namespace |
|-------------|------|-----------|
| science-portal-secrets | auth-secret, oidc-client-secret | science-portal |
| registry-ice-image | .dockerconfigjson | science-portal |

### API Endpoints

| API | Endpoint |
|-----|----------|
| CANFAR Login | https://ws-cadc.canfar.net/ac |
| Skaha (CANFAR) | https://ws-uv.canfar.net/skaha |
| Skaha (SRC) | https://src.canfar.net/skaha |
| Cavern (CANFAR) | https://ws-uv.canfar.net/arc/nodes/home/ |
| Cavern (SRC) | https://src.canfar.net/cavern |

### Deployment History

| Revision | Date | Image | Mode | Status |
|----------|------|-------|------|--------|
| 1 | 2025-10-27 11:28 | 1.0.0 | CANFAR | Initial deployment |
| 2 | 2025-10-27 11:35 | 1.0.0 | CANFAR | Auth mode fix |
| 3 | 2025-10-27 12:50 | 1.1.0 | OIDC | Switched to OIDC |
| 4 | 2025-10-27 13:10 | 1.0.0 | CANFAR | Switched back to CANFAR |

### Quick Access Commands

**View deployment:**
```bash
kubectl get all -n science-portal
```

**View logs:**
```bash
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal -f
```

**Check Helm status:**
```bash
helm status science-portal -n science-portal
```

**View deployment history:**
```bash
helm history science-portal -n science-portal
```

**Access application:**
```
https://science-portal-next.testapp.ca
```

---

## Troubleshooting

### Image Mode Mismatch

**Symptom:** Logs show CANFAR mode but you expect OIDC (or vice versa).

**Cause:** Wrong image deployed.

**Solution:**
```bash
# Check deployed image
kubectl get deployment science-portal -n science-portal \
  -o jsonpath='{.spec.template.spec.containers[0].image}'

# If wrong, upgrade with correct image
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --set image.tag=1.1.0 \
  --namespace science-portal
```

### Environment Variable Not Taking Effect

**Symptom:** Changed `NEXT_USE_CANFAR` but mode didn't change.

**Cause:** Environment variables at runtime **don't change** the compiled build. You must use the correct **image** built for that mode.

**Solution:** Deploy the correct image (see [Building Images](#building-images)).

### OIDC Redirect URI Mismatch

**Symptom:**
```
❌ redirect_uri_mismatch
❌ Invalid redirect URI
```

**Cause:** Redirect URI in app doesn't match allowed URIs in SKA IAM.

**Diagnosis:**
```bash
# Check configured URIs
kubectl get deployment science-portal -n science-portal \
  -o jsonpath='{.spec.template.spec.containers[0].env}' | \
  jq -r '.[] | select(.name | contains("REDIRECT") or contains("CALLBACK"))'
```

**Solution:**
1. Note the URIs in your deployment
2. Add those exact URIs to SKA IAM client configuration
3. Make sure there are no trailing slashes or typos

### OIDC Client Secret Missing

**Symptom:**
```
❌ OIDC authentication failed
❌ Invalid client credentials
```

**Cause:** Missing or incorrect OIDC client secret.

**Solution:**
```bash
# Check if secret exists
kubectl get secret science-portal-secrets -n science-portal \
  -o jsonpath='{.data}' | jq 'keys'

# Should show: ["auth-secret", "oidc-client-secret"]

# If missing, recreate with OIDC secret
kubectl create secret generic science-portal-secrets \
  --from-literal=auth-secret=$(openssl rand -base64 32) \
  --from-literal=oidc-client-secret="YOUR_OIDC_SECRET" \
  --namespace science-portal \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods
kubectl rollout restart deployment/science-portal -n science-portal
```

### Authentication Not Working After Mode Switch

**Symptom:** Users can't log in after switching modes.

**Cause:** Browser cached old authentication state.

**Solution:**
- Clear browser cookies for the domain
- Use incognito/private browsing mode
- Wait for session to expire (~24 hours)

### Pods Failing to Start

**Symptom:**
```
CrashLoopBackOff or ImagePullBackOff
```

**Diagnosis:**
```bash
# Check pod status
kubectl get pods -n science-portal

# Check pod events
kubectl describe pod <pod-name> -n science-portal

# Check logs
kubectl logs <pod-name> -n science-portal
```

**Common causes:**
- Image not found in registry → Check image tag
- Missing secrets → Recreate secrets
- Wrong pull secret → Check imagePullSecrets

### SSL Certificate Issues

**Symptom:** Certificate not issuing or expired.

**Diagnosis:**
```bash
# Check certificate status
kubectl get certificate -n science-portal
kubectl describe certificate science-portal-tls -n science-portal

# Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager --tail=100
```

**Solution:**
- Verify DNS points to LoadBalancer IP
- Check ClusterIssuer exists
- Check cert-manager is running

---

## Summary

### Key Takeaways

1. **Two Images Required**: CANFAR and OIDC modes need separate Docker images
2. **Build-Time Decision**: Authentication mode is baked into the build via `NEXT_PUBLIC_USE_CANFAR`
3. **Runtime Configuration**: Environment variables control server-side behavior but don't change the compiled frontend
4. **OIDC Requires Setup**: Must configure redirect URIs in both app and SKA IAM
5. **Easy Switching**: Use Helm upgrade with different image tags to switch modes

### Quick Reference

**Build both images:**
```bash
./build-mode-images.sh 1.0.0
```

**Deploy CANFAR mode:**
```bash
helm upgrade --install science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --set image.tag=1.0.0 \
  --namespace science-portal
```

**Deploy OIDC mode:**
```bash
helm upgrade --install science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --set image.tag=1.1.0 \
  --namespace science-portal
```

**Check mode:**
```bash
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal --tail=20 | grep mode
```

---

**Last Updated:** October 27, 2025
**Version:** 1.0.0
**Deployment:** science-portal-next.testapp.ca
**Cluster:** DigitalOcean DOKS (Toronto)
