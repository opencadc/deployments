# Science Portal Next.js - Kubernetes Deployment Guide

Complete guide for deploying the Science Portal Next.js application to any Kubernetes cluster using Helm.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Understanding the Architecture](#understanding-the-architecture)
4. [Cluster Setup](#cluster-setup)
5. [Project Structure](#project-structure)
6. [Container Registry Setup](#container-registry-setup)
7. [Building and Pushing Images](#building-and-pushing-images)
8. [Configuration Management](#configuration-management)
9. [Secrets Management](#secrets-management)
10. [Ingress and Load Balancing](#ingress-and-load-balancing)
11. [SSL/TLS Certificates](#ssltls-certificates)
12. [Deployment Process](#deployment-process)
13. [Monitoring and Logging](#monitoring-and-logging)
14. [Scaling Strategies](#scaling-strategies)
15. [Updates and Rollbacks](#updates-and-rollbacks)
16. [Authentication Modes](#authentication-modes)
17. [Troubleshooting](#troubleshooting)
18. [Security Best Practices](#security-best-practices)

---

## Introduction

This guide covers deploying the **Science Portal Next.js** application - a modern web interface for the CANFAR Science Platform, providing access to:

- **Skaha Sessions**: Interactive computing environments
- **Storage Management**: CANFAR and SRC Cavern file systems
- **User Authentication**: CANFAR credentials or OIDC (SKA IAM)
- **Session Monitoring**: Real-time logs and events

The deployment uses Helm for orchestration and works with any Kubernetes cluster (cloud or on-premises).

---

## Prerequisites

### Required Tools

```bash
# kubectl - Kubernetes CLI
kubectl version --client

# Helm 3 - Package manager for Kubernetes
helm version

# Docker - Container runtime
docker --version

# Optional: Cloud provider CLI (doctl, aws, gcloud, az)
```

### Installation Commands

**macOS:**
```bash
brew install kubectl helm docker
```

**Linux:**
```bash
# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# docker
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
```

### Required Information

Before deploying, gather:

- [ ] Kubernetes cluster access (kubeconfig)
- [ ] Container registry credentials
- [ ] Domain name for the application
- [ ] Email for SSL certificates
- [ ] Authentication credentials (CANFAR or OIDC)
- [ ] API endpoints (if different from defaults)

---

## Understanding the Architecture

### Application Components

```
science-portal-next/
├── Next.js Frontend        # React UI with Server-Side Rendering
├── API Routes              # Backend API for external services
├── Authentication Layer    # CANFAR or OIDC authentication
└── External APIs
    ├── Skaha API           # Session management
    ├── SRC Skaha API       # Alternative platform
    ├── Cavern API          # Storage service
    └── SRC Cavern API      # Alternative storage
```

### Kubernetes Resources

The Helm chart deploys:

- **Deployment**: Manages application pods (default: 2 replicas)
- **Service**: ClusterIP service for internal routing
- **Ingress**: HTTP/HTTPS external access with SSL
- **HPA**: Horizontal Pod Autoscaler (2-6 replicas)
- **ServiceAccount**: RBAC for pod permissions
- **ConfigMap**: Non-sensitive configuration
- **Secrets**: API keys and credentials
- **NetworkPolicy**: Network security rules
- **PodDisruptionBudget**: High availability guarantees

---

## Cluster Setup

### Option 1: DigitalOcean Kubernetes (DOKS)

```bash
# Install doctl
brew install doctl

# Authenticate
doctl auth init

# Create cluster
doctl kubernetes cluster create science-portal-cluster \
  --region tor1 \
  --version latest \
  --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=3;auto-scale=true;min-nodes=2;max-nodes=5"

# Get kubeconfig
doctl kubernetes cluster kubeconfig save science-portal-cluster

# Verify
kubectl get nodes
```

### Option 2: AWS EKS

```bash
# Install eksctl
brew install eksctl

# Create cluster
eksctl create cluster \
  --name science-portal-cluster \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5 \
  --managed

# Verify
kubectl get nodes
```

### Option 3: Google Kubernetes Engine (GKE)

```bash
# Set project
gcloud config set project your-project-id

# Create cluster
gcloud container clusters create science-portal-cluster \
  --region us-central1 \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 5

# Get credentials
gcloud container clusters get-credentials science-portal-cluster --region us-central1

# Verify
kubectl get nodes
```

### Option 4: Azure Kubernetes Service (AKS)

```bash
# Create resource group
az group create --name science-portal-rg --location eastus

# Create cluster
az aks create \
  --resource-group science-portal-rg \
  --name science-portal-cluster \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group science-portal-rg --name science-portal-cluster

# Verify
kubectl get nodes
```

---

## Project Structure

### Directory Layout

```
science-portal-next/
├── helm/
│   ├── science-portal/              # Helm chart
│   │   ├── Chart.yaml               # Chart metadata
│   │   ├── values.yaml              # Default values
│   │   ├── values-digitalocean.yaml # DigitalOcean config
│   │   ├── .helmignore
│   │   └── templates/
│   │       ├── _helpers.tpl
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       ├── ingress.yaml
│   │       ├── serviceaccount.yaml
│   │       ├── configmap.yaml
│   │       ├── hpa.yaml
│   │       ├── pdb.yaml
│   │       └── networkpolicy.yaml
│   ├── README.md
│   ├── DEPLOYMENT.md
│   └── deploy.sh                    # Deployment script
├── src/                             # Application source
├── Dockerfile                       # Multi-stage build
├── package.json
└── .env.local                       # Local environment vars
```

### Helm Chart Configuration

**Chart.yaml:**
```yaml
apiVersion: v2
name: science-portal
description: CANFAR Science Portal - Next.js application
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - science
  - canfar
  - skaha
home: https://www.canfar.net
sources:
  - https://github.com/opencadc/science-portal-next
maintainers:
  - name: CANFAR Team
    email: support@canfar.net
```

---

## Container Registry Setup

### DigitalOcean Container Registry

```bash
# Create registry
doctl registry create science-portal-registry

# Authenticate Docker
doctl registry login

# Registry URL format
# registry.digitalocean.com/science-portal-registry
```

### Docker Hub

```bash
# Login
docker login

# Push to Docker Hub
# username/science-portal-nextjs:1.0.0
```

### AWS ECR

```bash
# Create repository
aws ecr create-repository --repository-name science-portal-nextjs

# Authenticate
aws ecr get-login-password --region us-west-2 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-west-2.amazonaws.com
```

### Google Container Registry (GCR)

```bash
# Enable API
gcloud services enable containerregistry.googleapis.com

# Configure Docker
gcloud auth configure-docker

# Push to GCR
# gcr.io/project-id/science-portal-nextjs:1.0.0
```

### Creating Pull Secrets

**DigitalOcean:**
```bash
# Create in kube-system
doctl registry kubernetes-manifest | kubectl apply -f -

# Copy to application namespace
kubectl get secret registry-<name> -n kube-system -o yaml | \
  sed 's/namespace: kube-system/namespace: science-portal/' | \
  kubectl apply -f -
```

**Docker Hub:**
```bash
kubectl create secret docker-registry regcred \
  --docker-server=docker.io \
  --docker-username=<username> \
  --docker-password=<password> \
  --docker-email=<email> \
  --namespace science-portal
```

---

## Building and Pushing Images

### Dockerfile Overview

The project uses a multi-stage Dockerfile for optimization:

```dockerfile
# Stage 1: Dependencies
FROM node:22-alpine AS deps
# Installs production dependencies

# Stage 2: Builder
FROM node:22-alpine AS builder
# Builds Next.js application with standalone output

# Stage 3: Runner
FROM node:22-alpine AS runner
# Final minimal image with only runtime requirements
```

### Build Script

Create `build-and-push.sh`:

```bash
#!/bin/bash
set -e

# Configuration
REGISTRY="${REGISTRY:-registry.digitalocean.com/science-portal-registry}"
IMAGE_NAME="science-portal-nextjs"
VERSION="${1:-latest}"

echo "Building Science Portal Next.js ${VERSION}"

# Build image
docker build \
  --build-arg NEXT_PUBLIC_LOGIN_API=https://ws-cadc.canfar.net/ac \
  --build-arg NEXT_PUBLIC_SKAHA_API=https://ws-uv.canfar.net/skaha \
  --build-arg NEXT_PUBLIC_SRC_SKAHA_API=https://src.canfar.net/skaha \
  --build-arg NEXT_PUBLIC_SRC_CAVERN_API=https://src.canfar.net/cavern \
  --build-arg NEXT_PUBLIC_API_TIMEOUT=30000 \
  --build-arg NEXT_PUBLIC_USE_CANFAR=false \
  --build-arg NEXT_PUBLIC_ENABLE_QUERY_DEVTOOLS=false \
  -t ${REGISTRY}/${IMAGE_NAME}:${VERSION} \
  -t ${REGISTRY}/${IMAGE_NAME}:latest \
  .

# Push images
docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}
docker push ${REGISTRY}/${IMAGE_NAME}:latest

echo "Successfully pushed ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
```

### Usage

```bash
# Make executable
chmod +x build-and-push.sh

# Build and push specific version
./build-and-push.sh 1.0.0

# Build and push latest
./build-and-push.sh
```

### GitHub Actions CI/CD

Create `.github/workflows/build-deploy.yml`:

```yaml
name: Build and Deploy Science Portal

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

env:
  REGISTRY: registry.digitalocean.com/science-portal-registry
  IMAGE_NAME: science-portal-nextjs

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Log in to DigitalOcean registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ secrets.DO_REGISTRY_TOKEN }}
        password: ${{ secrets.DO_REGISTRY_TOKEN }}

    - name: Extract version
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}

    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        build-args: |
          NEXT_PUBLIC_LOGIN_API=https://ws-cadc.canfar.net/ac
          NEXT_PUBLIC_SKAHA_API=https://ws-uv.canfar.net/skaha
          NEXT_PUBLIC_SRC_SKAHA_API=https://src.canfar.net/skaha
          NEXT_PUBLIC_SRC_CAVERN_API=https://src.canfar.net/cavern
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Install kubectl and helm
      run: |
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        chmod +x kubectl && sudo mv kubectl /usr/local/bin/
        curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=./kubeconfig

    - name: Deploy with Helm
      run: |
        export KUBECONFIG=./kubeconfig
        helm upgrade --install science-portal ./helm/science-portal \
          -f ./helm/science-portal/values-production.yaml \
          --set image.tag=${{ github.ref_name }} \
          --namespace production \
          --create-namespace \
          --wait \
          --timeout=10m
```

---

## Configuration Management

### Environment-Specific Values

The project includes a base configuration template: `values-digitalocean.yaml`

#### Key Configuration Sections

**1. Image Configuration**
```yaml
image:
  repository: registry.digitalocean.com/science-portal-registry/science-portal-nextjs
  pullPolicy: IfNotPresent
  tag: "1.0.0"

imagePullSecrets:
  - name: registry-science-portal-registry
```

**2. API Endpoints**
```yaml
env:
  # Server-side API configuration
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

  # Client-side configuration
  - name: NEXT_PUBLIC_SKAHA_API
    value: "https://ws-uv.canfar.net/skaha"
  - name: NEXT_PUBLIC_SRC_SKAHA_API
    value: "https://src.canfar.net/skaha"
  - name: NEXT_PUBLIC_SRC_CAVERN_API
    value: "https://src.canfar.net/cavern"
```

**3. Authentication Mode**
```yaml
env:
  # CANFAR mode (username/password)
  - name: NEXT_USE_CANFAR
    value: "true"
  - name: NEXT_PUBLIC_USE_CANFAR
    value: "true"

  # Or OIDC mode (OAuth2)
  # - name: NEXT_USE_CANFAR
  #   value: "false"
```

**4. Domain Configuration**
```yaml
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: science-portal.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: science-portal-tls
      hosts:
        - science-portal.yourdomain.com

env:
  - name: NEXTAUTH_URL
    value: "https://science-portal.yourdomain.com"
```

### Creating Environment-Specific Files

**Development (values-development.yaml):**
```yaml
replicaCount: 1

image:
  tag: "dev"

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 256Mi

autoscaling:
  enabled: false

ingress:
  hosts:
    - host: dev-science-portal.yourdomain.com

env:
  - name: NEXT_PUBLIC_ENABLE_QUERY_DEVTOOLS
    value: "true"
```

**Production (values-production.yaml):**
```yaml
replicaCount: 3

image:
  repository: registry.digitalocean.com/science-portal-registry/science-portal-nextjs
  tag: "1.0.0"

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10

podDisruptionBudget:
  enabled: true
  minAvailable: 2

ingress:
  hosts:
    - host: science-portal.canfar.net
```

---

## Secrets Management

### Required Secrets

The Science Portal requires:

1. **AUTH_SECRET**: NextAuth.js session encryption key
2. **OIDC_CLIENT_SECRET**: OAuth client secret (if using OIDC mode)

### Creating Secrets

**Method 1: kubectl (Recommended)**

```bash
# Create namespace first
kubectl create namespace science-portal

# Generate secure AUTH_SECRET
AUTH_SECRET=$(openssl rand -base64 32)

# For CANFAR mode (no OIDC)
kubectl create secret generic science-portal-secrets \
  --from-literal=auth-secret="${AUTH_SECRET}" \
  --namespace science-portal

# For OIDC mode (with SKA IAM)
kubectl create secret generic science-portal-secrets \
  --from-literal=auth-secret="${AUTH_SECRET}" \
  --from-literal=oidc-client-secret="your-oidc-client-secret" \
  --namespace science-portal

# Verify secret
kubectl get secret science-portal-secrets -n science-portal
```

**Method 2: From .env.local**

```bash
# Extract values from .env.local
AUTH_SECRET=$(grep '^AUTH_SECRET=' .env.local | cut -d'=' -f2)
OIDC_SECRET=$(grep '^NEXT_OIDC_CLIENT_SECRET=' .env.local | cut -d'=' -f2)

# Create secret
kubectl create secret generic science-portal-secrets \
  --from-literal=auth-secret="${AUTH_SECRET}" \
  --from-literal=oidc-client-secret="${OIDC_SECRET}" \
  --namespace science-portal
```

**Method 3: Sealed Secrets (GitOps)**

```bash
# Install Sealed Secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Install kubeseal CLI
brew install kubeseal

# Create sealed secret
kubectl create secret generic science-portal-secrets \
  --from-literal=auth-secret="${AUTH_SECRET}" \
  --from-literal=oidc-client-secret="${OIDC_SECRET}" \
  --dry-run=client -o yaml | \
  kubeseal -o yaml > helm/science-portal/templates/sealed-secret.yaml

# Commit to Git (it's encrypted and safe)
git add helm/science-portal/templates/sealed-secret.yaml
```

### Using Secrets in Helm

The Helm chart references secrets:

```yaml
# values-digitalocean.yaml
secrets:
  existingSecret: "science-portal-secrets"
  keys:
    authSecret: "auth-secret"
    oidcClientSecret: "oidc-client-secret"
```

In deployment template:

```yaml
env:
- name: AUTH_SECRET
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secrets.existingSecret }}
      key: {{ .Values.secrets.keys.authSecret }}
- name: NEXT_OIDC_CLIENT_SECRET
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secrets.existingSecret }}
      key: {{ .Values.secrets.keys.oidcClientSecret }}
```

---

## Ingress and Load Balancing

### Installing NGINX Ingress Controller

```bash
# Add Helm repository
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install NGINX Ingress Controller
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.publishService.enabled=true

# Wait for LoadBalancer IP
kubectl get svc -n ingress-nginx -w

# Get the LoadBalancer IP
kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

### DNS Configuration

After getting the LoadBalancer IP:

```bash
# Example: LoadBalancer IP is 152.42.146.100
# Create DNS A record:

Type: A
Host: science-portal
Value: 152.42.146.100
TTL: 3600

# Result: science-portal.yourdomain.com -> 152.42.146.100
```

Verify DNS propagation:
```bash
dig +short science-portal.yourdomain.com
nslookup science-portal.yourdomain.com
```

### Ingress Configuration

The Helm chart includes production-ready Ingress configuration:

```yaml
# templates/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: science-portal
  annotations:
    # SSL/TLS
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"

    # Request limits
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"

    # Timeouts (important for long-running API calls)
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - science-portal.yourdomain.com
    secretName: science-portal-tls
  rules:
  - host: science-portal.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: science-portal
            port:
              number: 80
```

---

## SSL/TLS Certificates

### Installing cert-manager

```bash
# Add Helm repository
helm repo add jetstack https://charts.jetstack.io
helm repo update

# Install cert-manager with CRDs
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true
```

### Creating Let's Encrypt Issuer

**Production Issuer:**

```bash
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@domain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

**Staging Issuer (for testing):**

```bash
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: your-email@domain.com
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### Certificate Issuance

The Ingress annotation automatically triggers certificate creation:

```yaml
annotations:
  cert-manager.io/cluster-issuer: "letsencrypt-prod"
```

Check certificate status:

```bash
# View certificates
kubectl get certificate -n science-portal

# Check certificate details
kubectl describe certificate science-portal-tls -n science-portal

# View certificate requests
kubectl get certificaterequest -n science-portal

# Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager --tail=100
```

---

## Deployment Process

### Pre-Deployment Checklist

- [ ] Kubernetes cluster is running and accessible
- [ ] kubectl context is set to correct cluster
- [ ] Helm 3 is installed
- [ ] Docker image is built and pushed to registry
- [ ] Registry pull secret is created in `science-portal` namespace
- [ ] Application secrets are created
- [ ] DNS A record points to LoadBalancer IP
- [ ] NGINX Ingress Controller is installed
- [ ] cert-manager is installed
- [ ] Let's Encrypt ClusterIssuer is created
- [ ] Values file is configured with your domain and settings

### Step 1: Verify Cluster Access

```bash
# Check cluster info
kubectl cluster-info

# Check nodes
kubectl get nodes

# Verify Helm
helm version

# Create namespace
kubectl create namespace science-portal
```

### Step 2: Create Secrets

```bash
# Create application secrets
kubectl create secret generic science-portal-secrets \
  --from-literal=auth-secret=$(openssl rand -base64 32) \
  --from-literal=oidc-client-secret="your-oidc-secret-if-needed" \
  --namespace science-portal

# Create/copy registry pull secret
doctl registry kubernetes-manifest | kubectl apply -f -
kubectl get secret registry-<name> -n kube-system -o yaml | \
  sed 's/namespace: kube-system/namespace: science-portal/' | \
  kubectl apply -f -
```

### Step 3: Configure Values File

Edit `helm/science-portal/values-digitalocean.yaml`:

```yaml
# Update image repository and tag
image:
  repository: registry.digitalocean.com/your-registry/science-portal-nextjs
  tag: "1.0.0"

# Update pull secret name
imagePullSecrets:
  - name: registry-your-registry

# Update domain
ingress:
  hosts:
    - host: science-portal.yourdomain.com
  tls:
    - secretName: science-portal-tls
      hosts:
        - science-portal.yourdomain.com

# Update NEXTAUTH_URL
env:
  - name: NEXTAUTH_URL
    value: "https://science-portal.yourdomain.com"

# Update OIDC URIs (if using OIDC mode)
oidc:
  clientId: "your-oidc-client-id"
  callbackUri: "https://science-portal.yourdomain.com/science-portal"
  redirectUri: "https://science-portal.yourdomain.com/api/auth/callback/oidc"
```

### Step 4: Validate Helm Chart

```bash
# Lint the chart
helm lint ./helm/science-portal

# Template and review output
helm template science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --namespace science-portal

# Dry-run deployment
helm install science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --namespace science-portal \
  --dry-run --debug
```

### Step 5: Deploy Application

```bash
# Deploy with Helm
helm install science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --namespace science-portal \
  --wait \
  --timeout=10m

# Or use the deployment script
./helm/deploy.sh production
```

### Step 6: Verify Deployment

```bash
# Check release status
helm status science-portal -n science-portal

# Check all resources
kubectl get all -n science-portal

# Watch pods come up
kubectl get pods -n science-portal -w

# Check ingress
kubectl get ingress -n science-portal

# Check certificate
kubectl get certificate -n science-portal

# View application logs
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal --tail=50 -f
```

### Step 7: Access Application

```bash
# Get ingress hostname
kubectl get ingress -n science-portal \
  -o jsonpath='{.items[0].spec.rules[0].host}'

# Access in browser
# https://science-portal.yourdomain.com
```

### Using the Deployment Script

The project includes `helm/deploy.sh`:

```bash
# Deploy to production
NAMESPACE=production VALUES_FILE=./helm/science-portal/values-production.yaml ./helm/deploy.sh

# Deploy to staging
NAMESPACE=staging VALUES_FILE=./helm/science-portal/values-staging.yaml ./helm/deploy.sh

# With custom release name
RELEASE_NAME=science-portal-v2 ./helm/deploy.sh
```

---

## Monitoring and Logging

### Viewing Application Logs

```bash
# Real-time logs from all pods
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal -f

# Logs from specific pod
kubectl logs -n science-portal <pod-name> -f

# Previous container logs (if pod restarted)
kubectl logs -n science-portal <pod-name> --previous

# Last 100 lines
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal --tail=100

# Logs with timestamps
kubectl logs -n science-portal <pod-name> --timestamps
```

### Application Log Format

The Science Portal logs structured JSON for production:

```json
{
  "timestamp": "2025-10-27T18:31:45.128Z",
  "level": "info",
  "message": "SKAHA API REQUEST",
  "method": "GET",
  "url": "https://ws-uv.canfar.net/skaha/v1/session",
  "duration": "367ms",
  "status": 200
}
```

### Key Log Patterns

**Authentication:**
```bash
# CANFAR login events
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal | grep "api/auth/login"

# OIDC authentication
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal | grep "OIDC"

# Authentication errors
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal | grep "ERROR.*auth"
```

**API Calls:**
```bash
# Skaha API calls
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal | grep "SKAHA API"

# Failed API calls
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal | grep "ERROR.*API"
```

### Installing Prometheus & Grafana

```bash
# Add Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus & Grafana stack
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set grafana.adminPassword=admin

# Access Grafana
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80

# Login: admin/admin (change immediately)
```

### Exposing Application Metrics

Add metrics endpoint to Science Portal (if not present):

```javascript
// Example metrics endpoint in Next.js
import { NextResponse } from 'next/server';

export async function GET() {
  const metrics = {
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    timestamp: new Date().toISOString()
  };

  return NextResponse.json(metrics);
}
```

### Resource Monitoring

```bash
# Install metrics-server (if not already installed)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# View resource usage
kubectl top nodes
kubectl top pods -n science-portal
kubectl top pods -n science-portal --containers

# Watch resource usage
watch kubectl top pods -n science-portal
```

---

## Scaling Strategies

### Horizontal Pod Autoscaler (HPA)

The Science Portal includes HPA configuration:

```yaml
# In values-digitalocean.yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 6
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

Monitor HPA:

```bash
# Check HPA status
kubectl get hpa -n science-portal

# Detailed HPA info
kubectl describe hpa science-portal -n science-portal

# Watch HPA in action
watch kubectl get hpa -n science-portal
```

### Manual Scaling

```bash
# Scale to specific replica count
kubectl scale deployment science-portal --replicas=5 -n science-portal

# Or using Helm
helm upgrade science-portal ./helm/science-portal \
  --set replicaCount=5 \
  --reuse-values \
  -n science-portal
```

### Cluster Autoscaling

**DigitalOcean:**
```bash
doctl kubernetes cluster node-pool update <cluster-name> <pool-name> \
  --auto-scale=true \
  --min-nodes=2 \
  --max-nodes=10
```

**AWS EKS:**
```bash
eksctl scale nodegroup --cluster=science-portal-cluster \
  --name=standard-workers \
  --nodes=5 \
  --nodes-min=2 \
  --nodes-max=10
```

**GKE:**
```bash
gcloud container clusters update science-portal-cluster \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=10
```

### Resource Requests and Limits

Adjust based on actual usage:

```yaml
# Conservative (development)
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 256Mi

# Balanced (production)
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 512Mi

# High-performance
resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi
```

---

## Updates and Rollbacks

### Updating the Application

**Method 1: Update Image Tag**

```bash
# Build and push new version
docker build -t registry.digitalocean.com/your-registry/science-portal-nextjs:1.1.0 .
docker push registry.digitalocean.com/your-registry/science-portal-nextjs:1.1.0

# Update deployment
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --set image.tag=1.1.0 \
  --namespace science-portal \
  --wait

# Monitor rollout
kubectl rollout status deployment/science-portal -n science-portal
```

**Method 2: Update Configuration**

```bash
# Edit values file
vim helm/science-portal/values-digitalocean.yaml

# Apply changes
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --namespace science-portal \
  --wait
```

### Rolling Updates

Kubernetes performs zero-downtime rolling updates:

```yaml
# In deployment.yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # 1 extra pod during update
      maxUnavailable: 0  # No downtime
```

Watch pods being replaced:
```bash
kubectl get pods -n science-portal -w
```

### Rollback

**Helm Rollback:**

```bash
# View release history
helm history science-portal -n science-portal

# Rollback to previous version
helm rollback science-portal -n science-portal

# Rollback to specific revision
helm rollback science-portal 3 -n science-portal

# Verify rollback
kubectl get pods -n science-portal
helm status science-portal -n science-portal
```

**Kubernetes Rollback:**

```bash
# View deployment history
kubectl rollout history deployment/science-portal -n science-portal

# Rollback deployment
kubectl rollout undo deployment/science-portal -n science-portal

# Rollback to specific revision
kubectl rollout undo deployment/science-portal --to-revision=2 -n science-portal
```

### Testing Before Full Rollout

```bash
# Pause rollout
kubectl rollout pause deployment/science-portal -n science-portal

# Test the new version

# Resume if satisfied
kubectl rollout resume deployment/science-portal -n science-portal

# Or rollback if issues found
kubectl rollout undo deployment/science-portal -n science-portal
```

---

## Authentication Modes

The Science Portal supports two authentication modes:

### CANFAR Mode (Username/Password)

Traditional CANFAR authentication using username and password.

**Configuration:**

```yaml
# In values file
env:
  - name: NEXT_USE_CANFAR
    value: "true"
  - name: NEXT_PUBLIC_USE_CANFAR
    value: "true"
```

**Required Secrets:**
- `AUTH_SECRET`: Session encryption key

**APIs Used:**
- Login API: `https://ws-cadc.canfar.net/ac/login`
- User validation: Token-based

**Switching to CANFAR Mode:**

```bash
# Update values file
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --set env[0].name=NEXT_USE_CANFAR \
  --set env[0].value="true" \
  --set env[1].name=NEXT_PUBLIC_USE_CANFAR \
  --set env[1].value="true" \
  --namespace science-portal \
  --wait
```

### OIDC Mode (OAuth2/OpenID Connect)

Modern OAuth2 authentication via SKA IAM.

**Configuration:**

```yaml
# In values file
env:
  - name: NEXT_USE_CANFAR
    value: "false"
  - name: NEXT_PUBLIC_USE_CANFAR
    value: "false"

oidc:
  uri: "https://ska-iam.stfc.ac.uk/"
  clientId: "your-client-id"
  callbackUri: "https://science-portal.yourdomain.com/science-portal"
  redirectUri: "https://science-portal.yourdomain.com/api/auth/callback/oidc"
  scope: "openid profile offline_access"
```

**Required Secrets:**
- `AUTH_SECRET`: Session encryption key
- `OIDC_CLIENT_SECRET`: OAuth client secret

**Switching to OIDC Mode:**

```bash
# Update values file and secrets
kubectl create secret generic science-portal-secrets \
  --from-literal=auth-secret=$(openssl rand -base64 32) \
  --from-literal=oidc-client-secret="your-oidc-secret" \
  --namespace science-portal \
  --dry-run=client -o yaml | kubectl apply -f -

# Deploy with OIDC configuration
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-oidc.yaml \
  --namespace science-portal \
  --wait
```

### Verifying Authentication Mode

Check logs:
```bash
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal | grep -i "mode"
```

Look for:
- CANFAR mode: `Mode: CANFAR`
- OIDC mode: `OIDC mode, using SRC Cavern API`

---

## Troubleshooting

### Common Issues

#### 1. ImagePullBackOff

**Symptoms:**
```bash
kubectl get pods -n science-portal
# NAME                              READY   STATUS             RESTARTS   AGE
# science-portal-xxx                0/1     ImagePullBackOff   0          2m
```

**Diagnosis:**
```bash
kubectl describe pod <pod-name> -n science-portal
```

**Solutions:**

a) Verify image exists:
```bash
docker pull registry.digitalocean.com/your-registry/science-portal-nextjs:1.0.0
```

b) Check pull secret exists:
```bash
kubectl get secret -n science-portal | grep registry
```

c) Recreate pull secret:
```bash
doctl registry kubernetes-manifest | kubectl apply -f -
kubectl get secret registry-<name> -n kube-system -o yaml | \
  sed 's/namespace: kube-system/namespace: science-portal/' | \
  kubectl apply -f -
```

d) Verify image name in values file matches registry.

#### 2. CrashLoopBackOff

**Symptoms:**
```bash
kubectl get pods -n science-portal
# NAME                              READY   STATUS             RESTARTS   AGE
# science-portal-xxx                0/1     CrashLoopBackOff   5          5m
```

**Diagnosis:**
```bash
# Check current logs
kubectl logs <pod-name> -n science-portal

# Check previous logs
kubectl logs <pod-name> -n science-portal --previous

# Check events
kubectl describe pod <pod-name> -n science-portal
```

**Common Causes:**

a) Missing environment variables:
```bash
# Check if secrets exist
kubectl get secret science-portal-secrets -n science-portal
```

b) Invalid API endpoints:
```bash
# Test API connectivity from pod
kubectl run test --image=curlimages/curl -it --rm -- \
  curl -I https://ws-uv.canfar.net/skaha/v1/session
```

c) Authentication mode mismatch - see logs for:
```
Invalid JWT token format
```
Solution: Ensure `NEXT_USE_CANFAR` matches authentication method.

#### 3. Authentication Errors

**CANFAR Mode Issues:**

Check logs for:
```bash
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal | grep "auth/login"
```

Look for:
- `ERROR.*login` - Login API issues
- `Invalid credentials` - Wrong username/password
- `timeout` - Network issues to CANFAR APIs

**OIDC Mode Issues:**

Check logs for:
```bash
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal | grep -i "oidc"
```

Common errors:
- `Invalid JWT token format` - Using CANFAR login in OIDC mode
- `OIDC callback failed` - Incorrect redirect URI
- `Invalid client` - Wrong OIDC client ID or secret

Verify OIDC configuration:
```bash
kubectl get secret science-portal-secrets -n science-portal -o jsonpath='{.data.oidc-client-secret}' | base64 -d
```

#### 4. Certificate Not Issuing

**Diagnosis:**
```bash
# Check certificate
kubectl get certificate -n science-portal
kubectl describe certificate science-portal-tls -n science-portal

# Check certificate request
kubectl get certificaterequest -n science-portal

# Check challenges
kubectl get challenges -n science-portal
kubectl describe challenge <challenge-name> -n science-portal

# Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager --tail=100
```

**Common Causes:**

a) DNS not pointing to LoadBalancer:
```bash
# Get LoadBalancer IP
kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Verify DNS
dig +short science-portal.yourdomain.com
```

b) HTTP-01 challenge blocked:
```bash
# Test from outside cluster
curl -I http://science-portal.yourdomain.com/.well-known/acme-challenge/test
```

c) ClusterIssuer not created:
```bash
kubectl get clusterissuer
```

#### 5. Ingress Not Working

**Diagnosis:**
```bash
# Check ingress
kubectl get ingress -n science-portal
kubectl describe ingress science-portal -n science-portal

# Check service endpoints
kubectl get endpoints science-portal -n science-portal

# Check ingress controller
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx --tail=100
```

**Solutions:**

a) Service selector mismatch:
```bash
# Compare pod labels
kubectl get pods -n science-portal --show-labels

# Check service selector
kubectl get service science-portal -n science-portal -o yaml | grep selector -A 5
```

b) Ingress controller not installed:
```bash
kubectl get pods -n ingress-nginx
```

#### 6. High Memory Usage / OOMKilled

**Diagnosis:**
```bash
# Check resource usage
kubectl top pods -n science-portal

# Check events for OOMKilled
kubectl get events -n science-portal --sort-by='.lastTimestamp'
```

**Solutions:**

Increase memory limits:
```yaml
resources:
  limits:
    memory: 2Gi  # Increased from 1Gi
  requests:
    memory: 1Gi  # Increased from 512Mi
```

Apply changes:
```bash
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-updated.yaml \
  --namespace science-portal
```

### Debug Tools

**Interactive Shell:**
```bash
# Exec into running pod
kubectl exec -it <pod-name> -n science-portal -- /bin/sh

# Or use busybox for debugging
kubectl run debug --image=busybox -it --rm --restart=Never -- sh
```

**Network Testing:**
```bash
# Test from within cluster
kubectl run nettest --image=nicolaka/netshoot -it --rm -- bash

# Inside pod:
curl -I http://science-portal.science-portal.svc.cluster.local
dig science-portal.science-portal.svc.cluster.local
```

**Port Forwarding:**
```bash
# Forward to pod
kubectl port-forward <pod-name> 3000:3000 -n science-portal

# Forward to service
kubectl port-forward svc/science-portal 8080:80 -n science-portal

# Access at http://localhost:8080
```

### Getting Help

If issues persist:

1. Collect diagnostic information:
```bash
# Save to file
kubectl get all -n science-portal > diagnostics.txt
kubectl describe pods -n science-portal >> diagnostics.txt
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal --tail=200 >> diagnostics.txt
```

2. Check Science Portal GitHub issues
3. Contact CANFAR support: support@canfar.net

---

## Security Best Practices

### Pod Security

The Helm chart includes security configurations:

```yaml
# Pod security context
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1001
  fsGroup: 1001

# Container security context
securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
  readOnlyRootFilesystem: false  # Next.js needs write access for .next
```

### Network Policies

Network policies are enabled by default:

```yaml
networkPolicy:
  enabled: true
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # Only allow ingress controller
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 3000
  egress:
    # Allow external API calls
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: TCP
          port: 443  # HTTPS
        - protocol: TCP
          port: 53   # DNS
        - protocol: UDP
          port: 53   # DNS
```

### Secrets Security

1. **Never commit secrets to Git**
```bash
# Add to .gitignore
echo "values-*-secrets.yaml" >> .gitignore
```

2. **Use Sealed Secrets or External Secrets** for GitOps

3. **Rotate secrets regularly**
```bash
# Rotate AUTH_SECRET
kubectl create secret generic science-portal-secrets \
  --from-literal=auth-secret=$(openssl rand -base64 32) \
  --from-literal=oidc-client-secret="..." \
  --namespace science-portal \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to use new secret
kubectl rollout restart deployment/science-portal -n science-portal
```

### Image Security

1. **Scan images for vulnerabilities**
```bash
# Using Trivy
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image \
  registry.digitalocean.com/your-registry/science-portal-nextjs:1.0.0
```

2. **Use specific image tags** (not `latest`)
```yaml
image:
  tag: "1.0.0"  # Good
  # tag: "latest"  # Bad
```

3. **Keep base images updated**
```bash
# Rebuild regularly with latest node:22-alpine
docker build --no-cache -t science-portal-nextjs:1.0.1 .
```

### RBAC

The Helm chart creates a ServiceAccount with minimal permissions:

```yaml
serviceAccount:
  create: true
  name: science-portal
  # Only add annotations if needed for cloud provider integrations
  annotations: {}
```

### Monitoring Security

1. **Monitor failed authentication attempts**
```bash
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal | \
  grep -i "ERROR.*auth"
```

2. **Monitor unusual API activity**
```bash
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal | \
  grep -i "ERROR.*API"
```

---

## Conclusion

This guide provides comprehensive instructions for deploying the Science Portal Next.js application to any Kubernetes cluster. Key points:

- **Flexible Deployment**: Works with any Kubernetes cluster (cloud or on-premises)
- **Production-Ready**: Includes HA, SSL, monitoring, security
- **Two Auth Modes**: CANFAR (username/password) or OIDC (OAuth2)
- **Easy Updates**: Helm-based with rollback support
- **Well-Documented**: Troubleshooting and best practices included

### Quick Reference

**Deploy:**
```bash
helm install science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --namespace science-portal \
  --create-namespace \
  --wait
```

**Update:**
```bash
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-digitalocean.yaml \
  --namespace science-portal
```

**Rollback:**
```bash
helm rollback science-portal -n science-portal
```

**Check Status:**
```bash
kubectl get all -n science-portal
helm status science-portal -n science-portal
```

### Additional Resources

- [Science Portal Documentation](https://www.canfar.net/en/docs/)
- [CANFAR Platform](https://www.canfar.net)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)

### Support

- **Email**: support@canfar.net
- **GitHub Issues**: https://github.com/opencadc/science-portal-next/issues

---

**Last Updated**: October 2025
**Version**: 1.0.0
**Applicable to**: Science Portal Next.js v1.x
