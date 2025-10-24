# 🚀 Deployment Scripts

Deployment scripts for PeruGuide RAG API to various cloud platforms.

## 📋 Prerequisites

### All Platforms
- Docker installed
- API keys configured in `.env` file

### Azure
- Azure CLI (`az`) installed and authenticated
- `az login` completed

### AWS
- AWS CLI installed and configured
- IAM permissions for ECS, ECR, and Secrets Manager
- VPC, subnets, and security groups configured

### Google Cloud
- Google Cloud SDK (`gcloud`) installed
- `gcloud auth login` completed
- Project created and billing enabled

## 🐳 Local Development

### Linux/Mac
```bash
chmod +x run-local.sh
./run-local.sh
```

### Windows (PowerShell)
```powershell
.\run-local.ps1
```

### Docker Compose
```bash
docker-compose -f docker-compose.api.yml up -d
```

**Access the API:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

## ☁️ Cloud Deployment

### Azure Container Apps

```bash
# Set environment variables
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Deploy
chmod +x deploy-azure.sh
./deploy-azure.sh
```

**Features:**
- Auto-scaling (1-3 replicas)
- 1 CPU, 2GB memory
- Azure Container Registry
- HTTPS ingress enabled

### AWS ECS (Fargate)

```bash
# Configure AWS
export AWS_REGION="us-east-1"
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Note: Update VPC/subnet/security group IDs in script
chmod +x deploy-aws.sh
./deploy-aws.sh
```

**Features:**
- Fargate serverless compute
- 1 vCPU, 2GB memory
- ECR for container registry
- Secrets Manager for API keys
- CloudWatch logs

### Google Cloud Run

```bash
# Set project
export PROJECT_ID="your-project-id"
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Deploy
chmod +x deploy-gcp.sh
./deploy-gcp.sh
```

**Features:**
- Serverless auto-scaling (0-10 instances)
- 1 CPU, 2GB memory
- Container Registry
- Secret Manager for API keys
- Custom domain support

## 🔐 Environment Variables

Required environment variables:

```bash
# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://...
HUGGINGFACE_API_KEY=hf_...

# Application
ENVIRONMENT=production
LOG_LEVEL=info
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Logs (Docker)
```bash
docker logs -f peruguide-api
```

### Logs (Cloud)

**Azure:**
```bash
az containerapp logs show \
  --name peruguide-api \
  --resource-group peruguide-rg \
  --follow
```

**AWS:**
```bash
aws logs tail /ecs/peruguide --follow
```

**GCP:**
```bash
gcloud run services logs read peruguide-api \
  --region us-central1 \
  --follow
```

## 🛑 Cleanup

### Local
```bash
docker stop peruguide-api
docker rm peruguide-api
docker rmi peruguide-rag-api:latest
```

### Azure
```bash
az group delete --name peruguide-rg --yes
```

### AWS
```bash
aws ecs delete-service --cluster peruguide-cluster --service peruguide-service --force
aws ecs delete-cluster --cluster peruguide-cluster
aws ecr delete-repository --repository-name peruguide-rag-api --force
```

### GCP
```bash
gcloud run services delete peruguide-api --region us-central1 --quiet
gcloud container images delete gcr.io/$PROJECT_ID/peruguide-rag-api --quiet
```

## 💰 Cost Estimates

### Azure Container Apps
- ~$20-30/month (1 instance always on)
- Free tier: 180,000 vCPU-seconds + 360,000 GiB-seconds

### AWS ECS Fargate
- ~$30-40/month (1 task always on)
- 1 vCPU + 2GB: ~$0.04/hour

### Google Cloud Run
- Pay-per-use (very cost-effective for low traffic)
- Free tier: 2 million requests/month
- Estimated: $5-15/month for moderate use

## 🔒 Security Best Practices

1. **Never commit API keys** - Use environment variables or secrets managers
2. **Enable HTTPS** - All cloud platforms provide free SSL
3. **Rate limiting** - Implement in production (TODO)
4. **Authentication** - Add API key auth for production (TODO)
5. **Network security** - Use VPCs and security groups (AWS) or private networking
6. **Secrets rotation** - Rotate API keys regularly
7. **Logging** - Enable audit logs for compliance

## 📚 Documentation

- [Azure Container Apps Docs](https://learn.microsoft.com/azure/container-apps/)
- [AWS ECS Docs](https://docs.aws.amazon.com/ecs/)
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
