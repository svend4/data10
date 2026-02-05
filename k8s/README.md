# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the Dynamic Content Blocks API to a Kubernetes cluster.

## Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Docker images built and pushed to registry
- cert-manager (for TLS certificates)
- NGINX Ingress Controller
- Metrics Server (for HPA)

## Architecture

```
┌─────────────────────────────────────────┐
│            Ingress (NGINX)              │
│     api.content-blocks.example.com      │
└──────────────────┬──────────────────────┘
                   │
          ┌────────┴─────────┐
          │                  │
┌─────────▼──────────┐  ┌───▼────────────┐
│  API Pods (3-10)   │  │   Monitoring   │
│  - FastAPI         │  │  - Prometheus  │
│  - JWT Auth        │  │  - Grafana     │
│  - Rate Limiting   │  │                │
└──────────┬─────────┘  └────────────────┘
           │
    ┌──────┴──────┐
    │             │
┌───▼────┐  ┌────▼────┐  ┌────────┐  ┌──────────┐
│MongoDB │  │  Neo4j  │  │ Redis  │  │Elasticsearch│
│(StatefulSet)│(StatefulSet)│(Deployment)│(StatefulSet)│
└────────┘  └─────────┘  └────────┘  └──────────┘
```

## Files

- `namespace.yaml`: Namespace configuration
- `configmap.yaml`: Application configuration
- `secrets.yaml`: Sensitive credentials (Base64 encoded)
- `api-deployment.yaml`: API deployment, service, and PVC
- `mongodb-statefulset.yaml`: MongoDB StatefulSet
- `ingress.yaml`: Ingress configuration with TLS
- `hpa.yaml`: Horizontal Pod Autoscaler

## Quick Start

### 1. Create Namespace

```bash
kubectl apply -f namespace.yaml
```

### 2. Create Secrets

**Important**: Update `secrets.yaml` with your actual credentials first!

```bash
# Generate base64 encoded secrets
echo -n 'your-mongodb-password' | base64
echo -n 'your-jwt-secret' | base64

# Edit secrets.yaml with actual values
vim secrets.yaml

# Apply secrets
kubectl apply -f secrets.yaml
```

### 3. Create ConfigMap

```bash
kubectl apply -f configmap.yaml
```

### 4. Deploy Databases

```bash
# MongoDB
kubectl apply -f mongodb-statefulset.yaml

# Wait for MongoDB to be ready
kubectl wait --for=condition=ready pod -l app=mongodb -n content-blocks --timeout=300s

# Verify
kubectl get pods -n content-blocks
```

### 5. Deploy API

```bash
# Build and push Docker image
docker build -t content-blocks-api:4.0.0 .
docker push your-registry/content-blocks-api:4.0.0

# Update image reference in api-deployment.yaml
sed -i 's|content-blocks-api:4.0.0|your-registry/content-blocks-api:4.0.0|' api-deployment.yaml

# Deploy API
kubectl apply -f api-deployment.yaml

# Wait for API to be ready
kubectl wait --for=condition=ready pod -l app=content-blocks-api -n content-blocks --timeout=300s
```

### 6. Deploy Autoscaler

```bash
kubectl apply -f hpa.yaml
```

### 7. Deploy Ingress

```bash
# Update host in ingress.yaml
vim ingress.yaml

# Apply ingress
kubectl apply -f ingress.yaml

# Get external IP
kubectl get ingress -n content-blocks
```

### 8. Verify Deployment

```bash
# Check all resources
kubectl get all -n content-blocks

# Check pod logs
kubectl logs -f deployment/content-blocks-api -n content-blocks

# Test API
curl https://api.content-blocks.example.com/health
```

## Configuration

### Environment Variables

Update `configmap.yaml` for non-sensitive configuration:

```yaml
data:
  MONGODB_URI: "mongodb://mongodb:27017"
  RATE_LIMIT_PER_MINUTE: "100"
  LOG_LEVEL: "INFO"
```

### Secrets

Update `secrets.yaml` for sensitive data (Base64 encoded):

```bash
# Encode secret
echo -n 'my-secret' | base64

# Decode secret (for verification)
echo 'bXktc2VjcmV0' | base64 -d
```

### Resource Limits

Update resource requests/limits in `api-deployment.yaml`:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

### Scaling

#### Manual Scaling

```bash
# Scale API pods
kubectl scale deployment/content-blocks-api --replicas=5 -n content-blocks
```

#### Auto-Scaling

Modify `hpa.yaml`:

```yaml
spec:
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          averageUtilization: 70
```

## Monitoring

### Prometheus Metrics

Pods are annotated for Prometheus scraping:

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

### View Metrics

```bash
# Port forward to API pod
kubectl port-forward deployment/content-blocks-api 8000:8000 -n content-blocks

# Access metrics
curl http://localhost:8000/metrics
```

### Grafana Dashboard

Deploy monitoring stack:

```bash
# From monitoring directory
kubectl create -f ../monitoring/docker-compose-monitoring.yml
```

## Health Checks

### Liveness Probe

Checks if pod is alive:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

### Readiness Probe

Checks if pod can accept traffic:

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n content-blocks

# Check logs
kubectl logs <pod-name> -n content-blocks

# Check events
kubectl get events -n content-blocks --sort-by='.lastTimestamp'
```

### Database Connection Issues

```bash
# Test MongoDB connection
kubectl exec -it mongodb-0 -n content-blocks -- mongosh -u admin -p password

# Check service DNS
kubectl exec -it <api-pod> -n content-blocks -- nslookup mongodb
```

### Ingress Not Working

```bash
# Check ingress
kubectl describe ingress content-blocks-ingress -n content-blocks

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# Verify TLS certificate
kubectl describe certificate content-blocks-tls -n content-blocks
```

### High Memory Usage

```bash
# Check resource usage
kubectl top pods -n content-blocks

# Increase memory limits
kubectl set resources deployment/content-blocks-api -n content-blocks --limits=memory=4Gi

# Check for memory leaks
kubectl exec -it <pod-name> -n content-blocks -- python -m memory_profiler app/main.py
```

## Backup & Restore

### MongoDB Backup

```bash
# Backup MongoDB
kubectl exec mongodb-0 -n content-blocks -- mongodump --out /tmp/backup

# Copy backup
kubectl cp content-blocks/mongodb-0:/tmp/backup ./backup
```

### Restore MongoDB

```bash
# Copy backup to pod
kubectl cp ./backup content-blocks/mongodb-0:/tmp/restore

# Restore
kubectl exec mongodb-0 -n content-blocks -- mongorestore /tmp/restore
```

## Updates & Rollouts

### Rolling Update

```bash
# Update image
kubectl set image deployment/content-blocks-api api=content-blocks-api:4.1.0 -n content-blocks

# Check rollout status
kubectl rollout status deployment/content-blocks-api -n content-blocks

# View rollout history
kubectl rollout history deployment/content-blocks-api -n content-blocks
```

### Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/content-blocks-api -n content-blocks

# Rollback to specific revision
kubectl rollout undo deployment/content-blocks-api --to-revision=2 -n content-blocks
```

## Security

### Network Policies

Create network policies to restrict traffic:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
  namespace: content-blocks
spec:
  podSelector:
    matchLabels:
      app: content-blocks-api
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: nginx-ingress
      ports:
        - protocol: TCP
          port: 8000
```

### Pod Security

Enable pod security standards:

```bash
kubectl label namespace content-blocks pod-security.kubernetes.io/enforce=restricted
```

## Production Checklist

- [ ] Update all secrets with strong, unique values
- [ ] Configure TLS certificates
- [ ] Set up monitoring and alerting
- [ ] Configure backups
- [ ] Set resource limits
- [ ] Enable network policies
- [ ] Configure log aggregation
- [ ] Set up CI/CD pipeline
- [ ] Test disaster recovery
- [ ] Document runbooks

## Support

For issues or questions:
- Check logs: `kubectl logs -n content-blocks`
- View events: `kubectl get events -n content-blocks`
- Health check: `curl https://api/health`
