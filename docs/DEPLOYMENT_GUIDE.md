# Production Deployment Guide

**Dynamic Content Blocks System - Complete Deployment Instructions**

Version: 4.0.0
Last Updated: February 5, 2026

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [Docker Compose Deployment](#docker-compose-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Cloud Providers](#cloud-providers)
6. [Configuration](#configuration)
7. [Security Hardening](#security-hardening)
8. [Monitoring Setup](#monitoring-setup)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)
11. [Performance Tuning](#performance-tuning)
12. [Production Checklist](#production-checklist)

---

## Prerequisites

### System Requirements

**Minimum** (Development):
- CPU: 4 cores
- RAM: 8 GB
- Disk: 50 GB SSD
- OS: Linux/macOS/Windows with WSL2

**Recommended** (Production):
- CPU: 8+ cores
- RAM: 16+ GB
- Disk: 200+ GB SSD
- OS: Linux (Ubuntu 20.04+, CentOS 8+, Debian 11+)

### Software Requirements

- **Docker**: 24.0+
- **Docker Compose**: 2.20+
- **Kubernetes**: 1.24+ (for K8s deployment)
- **kubectl**: Latest version
- **Python**: 3.10+ (for local development)
- **Git**: 2.30+

### Network Requirements

- **Ports**:
  - 8000: API server
  - 27017: MongoDB
  - 7474, 7687: Neo4j
  - 9200: Elasticsearch
  - 6379: Redis
  - 9090: Prometheus
  - 3000: Grafana

- **Internet Access**: Required for:
  - Downloading Docker images
  - Installing Python packages
  - Downloading ML models (spaCy)
  - SSL certificate generation (Let's Encrypt)

---

## Deployment Options

### 1. Docker Compose (Recommended for Small-Medium Scale)

**Best for**:
- Development and testing
- Small production deployments (< 100 users)
- Single-server deployments
- Quick proof-of-concept

**Pros**:
- Easy setup
- Self-contained
- Good for development
- Quick iteration

**Cons**:
- Limited scalability
- No auto-scaling
- Single point of failure

### 2. Kubernetes (Recommended for Production)

**Best for**:
- Production deployments
- High availability requirements
- Multi-server deployments
- Auto-scaling needs

**Pros**:
- Highly scalable
- Auto-healing
- Rolling updates
- Load balancing
- Resource management

**Cons**:
- Complex setup
- Requires K8s knowledge
- Higher resource overhead

### 3. Cloud Managed Services

**Best for**:
- Rapid deployment
- Minimal DevOps overhead
- Enterprise deployments

**Options**:
- AWS EKS + managed databases
- Google GKE + Cloud SQL
- Azure AKS + Cosmos DB

---

## Docker Compose Deployment

### Step 1: Prepare Environment

```bash
# Clone repository
git clone https://github.com/yourusername/data10.git
cd data10

# Create .env file
cp .env.example .env

# Edit .env with your configuration
vim .env
```

### Step 2: Configure Environment Variables

```bash
# .env file
MONGODB_URI=mongodb://mongodb:27017
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-secure-password

ELASTICSEARCH_URL=http://elasticsearch:9200
REDIS_URL=redis://redis:6379

JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
API_VERSION=4.0.0
LOG_LEVEL=INFO

# Admin user (created on first run)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-secure-admin-password
```

### Step 3: Build and Start Services

```bash
# Build Docker images
docker-compose build

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Wait for services to be ready (~60 seconds)
sleep 60
```

### Step 4: Initialize Data

```bash
# Install Python dependencies (for scripts)
pip install -r requirements.txt

# Download NLP models
python scripts/setup_nlp_models.py

# Run quickstart (optional - creates sample data)
python scripts/quickstart.py
```

### Step 5: Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "services": {
#     "mongodb": {"status": "up"},
#     "neo4j": {"status": "up"},
#     "elasticsearch": {"status": "up"},
#     "redis": {"status": "up"}
#   }
# }

# Check API documentation
open http://localhost:8000/docs
```

### Step 6: Setup Monitoring (Optional)

```bash
# Start monitoring stack
cd monitoring
docker-compose -f docker-compose-monitoring.yml up -d

# Access Grafana
open http://localhost:3000
# Login: admin / admin

# Import dashboard
# Dashboard JSON: monitoring/grafana-dashboard.json
```

---

## Kubernetes Deployment

### Step 1: Prepare Cluster

```bash
# Verify kubectl access
kubectl cluster-info

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Verify namespace
kubectl get namespaces
```

### Step 2: Configure Secrets

```bash
# Generate secrets
export MONGODB_PASSWORD=$(openssl rand -base64 32)
export NEO4J_PASSWORD=$(openssl rand -base64 32)
export REDIS_PASSWORD=$(openssl rand -base64 32)
export JWT_SECRET=$(openssl rand -base64 64)
export ADMIN_PASSWORD=$(openssl rand -base64 24)

# Create base64 encoded secrets
echo -n "$MONGODB_PASSWORD" | base64
echo -n "$NEO4J_PASSWORD" | base64
echo -n "$REDIS_PASSWORD" | base64
echo -n "$JWT_SECRET" | base64
echo -n "$ADMIN_PASSWORD" | base64

# Update k8s/secrets.yaml with generated values
vim k8s/secrets.yaml

# Apply secrets
kubectl apply -f k8s/secrets.yaml
```

### Step 3: Apply ConfigMaps

```bash
# Review and update configuration
vim k8s/configmap.yaml

# Apply ConfigMap
kubectl apply -f k8s/configmap.yaml

# Verify
kubectl get configmap -n content-blocks
```

### Step 4: Deploy Databases

```bash
# Deploy MongoDB
kubectl apply -f k8s/mongodb-statefulset.yaml

# Wait for MongoDB to be ready
kubectl wait --for=condition=ready pod -l app=mongodb -n content-blocks --timeout=300s

# Deploy Neo4j (create file similar to MongoDB)
kubectl apply -f k8s/neo4j-statefulset.yaml

# Deploy Elasticsearch
kubectl apply -f k8s/elasticsearch-statefulset.yaml

# Deploy Redis
kubectl apply -f k8s/redis-deployment.yaml

# Verify all databases
kubectl get pods -n content-blocks
```

### Step 5: Build and Push Docker Image

```bash
# Build image
docker build -t your-registry/content-blocks-api:4.0.0 .

# Login to registry
docker login your-registry

# Push image
docker push your-registry/content-blocks-api:4.0.0

# Update deployment with your image
sed -i 's|content-blocks-api:4.0.0|your-registry/content-blocks-api:4.0.0|' k8s/api-deployment.yaml
```

### Step 6: Deploy API

```bash
# Apply deployment
kubectl apply -f k8s/api-deployment.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=content-blocks-api -n content-blocks --timeout=300s

# Check deployment
kubectl get deployments -n content-blocks
kubectl get pods -n content-blocks
```

### Step 7: Configure Ingress

```bash
# Install NGINX Ingress Controller (if not installed)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Install cert-manager for TLS (if not installed)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Update domain in ingress.yaml
vim k8s/ingress.yaml
# Change: api.content-blocks.example.com to your domain

# Apply ingress
kubectl apply -f k8s/ingress.yaml

# Get external IP
kubectl get ingress -n content-blocks
```

### Step 8: Setup Auto-Scaling

```bash
# Ensure metrics-server is installed
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Apply HPA
kubectl apply -f k8s/hpa.yaml

# Verify HPA
kubectl get hpa -n content-blocks
```

### Step 9: Verify Deployment

```bash
# Check all resources
kubectl get all -n content-blocks

# Check pod logs
kubectl logs -f deployment/content-blocks-api -n content-blocks

# Test API (replace with your domain)
curl https://api.content-blocks.example.com/health

# Access API docs
open https://api.content-blocks.example.com/docs
```

---

## Cloud Providers

### AWS Deployment

**Services**:
- EKS for Kubernetes
- RDS for MongoDB (DocumentDB)
- ElastiCache for Redis
- Amazon Elasticsearch Service
- ALB for Load Balancing
- Route 53 for DNS
- ACM for SSL Certificates

**Steps**:

```bash
# Create EKS cluster
eksctl create cluster \
  --name content-blocks \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type t3.large \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 10 \
  --managed

# Update kubeconfig
aws eks update-kubeconfig --region us-west-2 --name content-blocks

# Deploy as per Kubernetes steps above
```

### Google Cloud Platform

**Services**:
- GKE for Kubernetes
- Cloud SQL for PostgreSQL (or MongoDB Atlas)
- Cloud Memorystore for Redis
- Elasticsearch on Compute Engine
- Cloud Load Balancing
- Cloud DNS
- Google-managed SSL

**Steps**:

```bash
# Create GKE cluster
gcloud container clusters create content-blocks \
  --num-nodes=3 \
  --machine-type=n1-standard-4 \
  --region=us-central1 \
  --enable-autoscaling \
  --min-nodes=3 \
  --max-nodes=10

# Get credentials
gcloud container clusters get-credentials content-blocks --region=us-central1

# Deploy as per Kubernetes steps
```

### Azure

**Services**:
- AKS for Kubernetes
- Cosmos DB (MongoDB API)
- Azure Cache for Redis
- Elasticsearch on VMs
- Azure Load Balancer
- Azure DNS
- Azure SSL Certificates

**Steps**:

```bash
# Create resource group
az group create --name content-blocks-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group content-blocks-rg \
  --name content-blocks \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group content-blocks-rg --name content-blocks

# Deploy as per Kubernetes steps
```

---

## Configuration

### Application Configuration

**app/core/config.py**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API
    API_VERSION: str = "4.0.0"
    API_TITLE: str = "Dynamic Content Blocks API"

    # Databases
    MONGODB_URI: str
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    ELASTICSEARCH_URL: str
    REDIS_URL: str

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100

    # Audit
    AUDIT_LOG_ENABLED: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 90

    # ML
    SPACY_MODEL: str = "de_core_news_lg"
    TRANSFORMER_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"

    class Config:
        env_file = ".env"

settings = Settings()
```

### Environment-Specific Configuration

**Development (.env.dev)**:
```bash
LOG_LEVEL=DEBUG
RATE_LIMIT_PER_MINUTE=1000
AUDIT_LOG_ENABLED=false
```

**Staging (.env.staging)**:
```bash
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=500
AUDIT_LOG_ENABLED=true
MONGODB_URI=mongodb://staging-mongo:27017
```

**Production (.env.prod)**:
```bash
LOG_LEVEL=WARNING
RATE_LIMIT_PER_MINUTE=100
AUDIT_LOG_ENABLED=true
MONGODB_URI=mongodb://prod-mongo-0,prod-mongo-1,prod-mongo-2:27017/?replicaSet=rs0
```

---

## Security Hardening

### 1. Network Security

```bash
# Use firewall rules
ufw allow 443/tcp  # HTTPS
ufw allow 22/tcp   # SSH (restrict to your IP)
ufw deny 27017/tcp # Block MongoDB from external
ufw deny 7687/tcp  # Block Neo4j from external

# Enable firewall
ufw enable
```

### 2. Database Security

**MongoDB**:
```javascript
// Create admin user
use admin
db.createUser({
  user: "admin",
  pwd: "strong-password",
  roles: ["root"]
})

// Enable authentication in mongod.conf
security:
  authorization: enabled
```

**Neo4j**:
```bash
# neo4j.conf
dbms.security.auth_enabled=true
dbms.connector.bolt.tls_level=REQUIRED
```

### 3. Application Security

```python
# Use environment variables for secrets
# Never commit .env files
# Rotate JWT secret keys regularly
# Implement IP whitelisting for admin endpoints
# Use HTTPS only in production
# Enable CORS only for trusted domains
```

### 4. SSL/TLS Configuration

```bash
# Let's Encrypt with cert-manager (K8s)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

---

## Monitoring Setup

### Prometheus Configuration

See `monitoring/prometheus.yml` for full configuration.

**Key Metrics to Monitor**:
- HTTP request rate and latency
- Error rate (4xx, 5xx)
- Database connection pool usage
- Cache hit/miss ratio
- ML processing time
- Active user sessions
- Rate limit violations

### Grafana Dashboards

```bash
# Import dashboard
# 1. Login to Grafana (localhost:3000)
# 2. Go to Dashboards > Import
# 3. Upload: monitoring/grafana-dashboard.json
```

### Alerting Rules

**Critical Alerts**:
- API down (> 1 minute)
- Database connection failure
- High error rate (> 5%)
- High memory usage (> 90%)

**Warning Alerts**:
- Slow response time (P95 > 2s)
- Low cache hit rate (< 50%)
- High CPU usage (> 80%)

---

## Backup & Recovery

### MongoDB Backup

```bash
# Daily backup
mongodump --out /backup/$(date +%Y%m%d)

# Automated backup script
cat > /usr/local/bin/mongodb-backup.sh <<'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/mongodb/$DATE"
mongodump --out $BACKUP_DIR
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR
# Upload to S3
aws s3 cp $BACKUP_DIR.tar.gz s3://your-bucket/backups/
# Keep last 30 days
find /backup/mongodb -name "*.tar.gz" -mtime +30 -delete
EOF

chmod +x /usr/local/bin/mongodb-backup.sh

# Add to cron
crontab -e
0 2 * * * /usr/local/bin/mongodb-backup.sh
```

### Neo4j Backup

```bash
# Backup Neo4j database
neo4j-admin dump --database=neo4j --to=/backup/neo4j-$(date +%Y%m%d).dump
```

### Restore

```bash
# Restore MongoDB
mongorestore /backup/20260205

# Restore Neo4j
neo4j-admin load --from=/backup/neo4j-20260205.dump --database=neo4j --force
```

---

## Troubleshooting

### Common Issues

**1. MongoDB Connection Failed**
```bash
# Check MongoDB status
docker-compose logs mongodb
kubectl logs -n content-blocks mongodb-0

# Verify connection string
echo $MONGODB_URI

# Test connection
mongosh $MONGODB_URI
```

**2. High Memory Usage**
```bash
# Check pod memory
kubectl top pods -n content-blocks

# Increase memory limit in deployment
kubectl set resources deployment/content-blocks-api -n content-blocks --limits=memory=4Gi
```

**3. Slow API Responses**
```bash
# Check database latency
curl http://localhost:8000/health

# Review Prometheus metrics
open http://localhost:9090

# Check for slow queries
# MongoDB: db.currentOp()
# Neo4j: CALL dbms.listQueries()
```

**4. Certificate Issues**
```bash
# Check cert-manager
kubectl get certificates -n content-blocks
kubectl describe certificate content-blocks-tls -n content-blocks

# Force renewal
kubectl delete secret content-blocks-tls -n content-blocks
```

---

## Performance Tuning

### Database Optimization

**MongoDB**:
```javascript
// Create indexes
db.blocks.createIndex({type: 1, source: 1})
db.blocks.createIndex({tags: 1})
db.blocks.createIndex({"metadata.category": 1})

// Enable profiling
db.setProfilingLevel(1, {slowms: 100})
```

**Neo4j**:
```cypher
// Create indexes
CREATE INDEX block_id FOR (b:Block) ON (b.id);
CREATE INDEX block_type FOR (b:Block) ON (b.type);

// Check query plans
EXPLAIN MATCH (b:Block) WHERE b.type = 'paragraph' RETURN b;
```

**Elasticsearch**:
```bash
# Increase heap size
ES_JAVA_OPTS="-Xms4g -Xmx4g"

# Optimize indexing
curl -X PUT "localhost:9200/content_blocks/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "refresh_interval": "30s",
    "number_of_replicas": 1
  }
}'
```

### Application Tuning

**Increase Workers**:
```bash
# In production, use multiple workers
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

**Connection Pooling**:
```python
# MongoDB
MongoClient(max_pool_size=100)

# Redis
ConnectionPool(max_connections=50)
```

---

## Production Checklist

### Pre-Deployment

- [ ] Environment variables configured
- [ ] Secrets generated and stored securely
- [ ] SSL certificates obtained
- [ ] Domain DNS configured
- [ ] Firewall rules set
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] Load testing completed
- [ ] Security audit performed
- [ ] Documentation updated

### Deployment

- [ ] All services started successfully
- [ ] Health checks passing
- [ ] Database migrations applied
- [ ] Initial data loaded
- [ ] Admin user created
- [ ] SSL/TLS working
- [ ] Monitoring data flowing
- [ ] Logs collecting properly
- [ ] Alerts configured

### Post-Deployment

- [ ] Verify all endpoints working
- [ ] Run integration tests
- [ ] Check performance metrics
- [ ] Monitor error logs
- [ ] Verify backup jobs running
- [ ] Test disaster recovery
- [ ] Document known issues
- [ ] Train operations team

### Ongoing Maintenance

- [ ] Daily: Check monitoring dashboards
- [ ] Daily: Review error logs
- [ ] Weekly: Review performance metrics
- [ ] Weekly: Test backups
- [ ] Monthly: Security updates
- [ ] Monthly: Dependency updates
- [ ] Quarterly: Disaster recovery drill
- [ ] Quarterly: Capacity planning

---

**Status**: Production Deployment Guide Complete ✅
**Version**: 4.0.0
**Last Updated**: February 5, 2026
