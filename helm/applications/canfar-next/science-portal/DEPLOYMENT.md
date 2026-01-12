# Deploying Science Portal to DigitalOcean Kubernetes

This guide walks you through deploying the Science Portal Next.js application to a DigitalOcean Kubernetes (DOKS) cluster using Helm.

## Prerequisites

Before you begin, ensure you have the following:

1. **DigitalOcean Account** with a Kubernetes cluster created
2. **kubectl** installed and configured to access your DOKS cluster
3. **Helm 3** installed (version 3.0 or higher)
4. **doctl** (DigitalOcean CLI) installed and authenticated
5. **Docker** for building container images
6. A **domain name** pointing to your cluster's load balancer

## Quick Start

```bash
# 1. Connect to your DOKS cluster
doctl kubernetes cluster kubeconfig save your-cluster-name

# 2. Verify connection
kubectl get nodes

# 3. Deploy using the deployment script
./helm/deploy.sh production
```

## Detailed Deployment Steps

### Step 1: Set Up DigitalOcean Container Registry

Create a container registry to store your Docker images:

```bash
# Create a container registry
doctl registry create science-portal-registry

# Authenticate Docker with the registry
doctl registry login
```

### Step 2: Build and Push Docker Image

Build your application and push it to the registry:

```bash
# Build the Docker image
docker build -t registry.digitalocean.com/science-portal-registry/science-portal-nextjs:1.0.0 .

# Push to registry
docker push registry.digitalocean.com/science-portal-registry/science-portal-nextjs:1.0.0

# Tag as latest
docker tag registry.digitalocean.com/science-portal-registry/science-portal-nextjs:1.0.0 \
  registry.digitalocean.com/science-portal-registry/science-portal-nextjs:latest
docker push registry.digitalocean.com/science-portal-registry/science-portal-nextjs:latest
```

### Step 3: Configure Kubernetes to Pull from Registry

Create an image pull secret:

```bash
# Generate and apply the registry secret
doctl registry kubernetes-manifest | kubectl apply -f -

# The secret will be named: registry-science-portal
```

### Step 4: Install Required Cluster Add-ons

#### Install NGINX Ingress Controller

```bash
# Add the ingress-nginx repository
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install NGINX Ingress Controller
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.publishService.enabled=true
```

Wait for the load balancer to be provisioned:

```bash
kubectl get svc -n ingress-nginx -w
```

Note the EXTERNAL-IP and configure your DNS to point your domain to this IP.

#### Install cert-manager for SSL/TLS

```bash
# Add the cert-manager repository
helm repo add jetstack https://charts.jetstack.io
helm repo update

# Install cert-manager
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true
```

Create a Let's Encrypt ClusterIssuer:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### Step 5: Configure Application Values

Edit the DigitalOcean-specific values file:

```bash
# Copy the DigitalOcean values template
cp helm/science-portal/values-digitalocean.yaml helm/science-portal/values-production.yaml

# Edit the values file
vim helm/science-portal/values-production.yaml
```

Update the following values:

1. **Image repository**: Update to your registry path
   ```yaml
   image:
     repository: registry.digitalocean.com/science-portal-registry/science-portal-nextjs
     tag: "1.0.0"
   ```

2. **Domain name**: Replace `science-portal.yourdomain.com` with your actual domain
   ```yaml
   ingress:
     hosts:
       - host: science-portal.yourdomain.com
   ```

3. **OIDC configuration**: Add your OIDC client credentials
   ```yaml
   oidc:
     clientId: "your-actual-client-id"
   ```

4. **Environment URLs**: Update all URLs in the `env` section

### Step 6: Create Kubernetes Secrets

Create the required secrets:

```bash
# Generate a secure random string for AUTH_SECRET
AUTH_SECRET=$(openssl rand -base64 32)

# Create the secrets (replace YOUR_OIDC_SECRET with actual value)
kubectl create secret generic science-portal-secrets \
  --from-literal=auth-secret="$AUTH_SECRET" \
  --from-literal=oidc-client-secret="YOUR_OIDC_SECRET"

# Verify the secret was created
kubectl get secret science-portal-secrets
```

### Step 7: Deploy with Helm

Deploy the application:

```bash
# Install the Helm chart
helm install science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-production.yaml \
  --namespace science-portal \
  --create-namespace

# Or upgrade if already installed
helm upgrade --install science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-production.yaml \
  --namespace science-portal \
  --create-namespace
```

### Step 8: Verify Deployment

Check the deployment status:

```bash
# Check pods
kubectl get pods -n science-portal

# Check services
kubectl get svc -n science-portal

# Check ingress
kubectl get ingress -n science-portal

# View logs
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal --tail=100 -f

# Check certificate status
kubectl get certificate -n science-portal
```

### Step 9: Access Your Application

Once the certificate is issued (may take 1-2 minutes), access your application:

```
https://science-portal.yourdomain.com
```

## Updating the Deployment

### Update Application Code

```bash
# Build new version
docker build -t registry.digitalocean.com/science-portal-registry/science-portal-nextjs:1.0.1 .
docker push registry.digitalocean.com/science-portal-registry/science-portal-nextjs:1.0.1

# Update the deployment
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-production.yaml \
  --set image.tag=1.0.1 \
  --namespace science-portal
```

### Update Configuration

```bash
# Edit values file
vim helm/science-portal/values-production.yaml

# Apply changes
helm upgrade science-portal ./helm/science-portal \
  -f ./helm/science-portal/values-production.yaml \
  --namespace science-portal
```

## Monitoring and Troubleshooting

### View Application Logs

```bash
# Real-time logs
kubectl logs -n science-portal -l app.kubernetes.io/name=science-portal -f

# Logs from specific pod
kubectl logs -n science-portal <pod-name>

# Previous container logs (if pod restarted)
kubectl logs -n science-portal <pod-name> --previous
```

### Debug Pod Issues

```bash
# Describe pod to see events
kubectl describe pod -n science-portal <pod-name>

# Get pod details
kubectl get pod -n science-portal <pod-name> -o yaml

# Execute commands in pod
kubectl exec -n science-portal <pod-name> -it -- /bin/sh
```

### Check Ingress and Certificates

```bash
# Check ingress details
kubectl describe ingress -n science-portal

# Check certificate status
kubectl describe certificate -n science-portal science-portal-tls

# Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager -f
```

### Common Issues

#### 1. Pods not starting

Check image pull secrets and container registry access:

```bash
kubectl describe pod -n science-portal <pod-name>
```

#### 2. SSL/TLS certificate not issuing

Check cert-manager logs and DNS configuration:

```bash
kubectl get certificaterequest -n science-portal
kubectl describe certificaterequest -n science-portal <request-name>
```

#### 3. Application errors

Check environment variables and secrets:

```bash
kubectl get secret -n science-portal science-portal-secrets
kubectl exec -n science-portal <pod-name> -- env | grep -E 'NEXT_|AUTH_'
```

## Scaling

### Manual Scaling

```bash
# Scale to specific number of replicas
kubectl scale deployment -n science-portal science-portal --replicas=5
```

### Horizontal Pod Autoscaler

The HPA is enabled by default in the values file. Monitor it:

```bash
# Check HPA status
kubectl get hpa -n science-portal

# Describe HPA for details
kubectl describe hpa -n science-portal science-portal
```

## Backup and Disaster Recovery

### Export Current Configuration

```bash
# Export Helm values
helm get values science-portal -n science-portal > backup-values.yaml

# Export all Kubernetes resources
kubectl get all -n science-portal -o yaml > backup-resources.yaml

# Backup secrets (be careful with these!)
kubectl get secret -n science-portal science-portal-secrets -o yaml > backup-secrets.yaml
```

### Restore from Backup

```bash
# Restore secrets first
kubectl apply -f backup-secrets.yaml

# Reinstall with Helm
helm install science-portal ./helm/science-portal \
  -f backup-values.yaml \
  --namespace science-portal
```

## Uninstalling

To remove the application:

```bash
# Uninstall Helm release
helm uninstall science-portal -n science-portal

# Delete namespace (optional)
kubectl delete namespace science-portal

# Clean up secrets
kubectl delete secret science-portal-secrets -n science-portal
```

## Cost Optimization Tips

1. **Right-size your nodes**: Use `s-2vcpu-4gb` nodes for development, scale up for production
2. **Use autoscaling**: Let HPA manage replicas based on actual load
3. **Enable cluster autoscaler**: DOKS can automatically add/remove nodes
4. **Use ClusterIP + Ingress**: More cost-effective than multiple LoadBalancers
5. **Monitor resource usage**: Use DO monitoring to track actual resource consumption

## Security Best Practices

1. **Use secrets for sensitive data**: Never commit secrets to version control
2. **Enable network policies**: Restrict pod-to-pod communication
3. **Keep images updated**: Regularly rebuild and deploy updated images
4. **Use RBAC**: Configure proper role-based access control
5. **Enable pod security policies**: Use the security contexts defined in values
6. **Rotate secrets regularly**: Update AUTH_SECRET and OIDC secrets periodically

## Additional Resources

- [DigitalOcean Kubernetes Documentation](https://docs.digitalocean.com/products/kubernetes/)
- [Helm Documentation](https://helm.sh/docs/)
- [Next.js Deployment Documentation](https://nextjs.org/docs/deployment)
- [cert-manager Documentation](https://cert-manager.io/docs/)
- [NGINX Ingress Controller Documentation](https://kubernetes.github.io/ingress-nginx/)

## Support

For issues specific to:
- **Application**: Check application logs and environment configuration
- **Kubernetes**: Review DigitalOcean DOKS documentation
- **Helm Chart**: Review helm/science-portal/templates and values files
