#!/bin/bash
# Deploy PeruGuide RAG API to Google Cloud Run

set -e

echo "🚀 Deploying PeruGuide RAG to Google Cloud Run..."

# Configuration
PROJECT_ID=${PROJECT_ID:-"peruguide-project"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"peruguide-api"}
IMAGE_NAME="gcr.io/$PROJECT_ID/peruguide-rag-api"
IMAGE_TAG=${IMAGE_TAG:-"latest"}

# Step 1: Set project
echo "📦 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Step 2: Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com

# Step 3: Build and push Docker image
echo "🏗️  Building Docker image with Cloud Build..."
gcloud builds submit \
  --tag $IMAGE_NAME:$IMAGE_TAG \
  --timeout=20m

# Step 4: Create secrets (if not exist)
echo "🔐 Setting up secrets..."
echo $OPENAI_API_KEY | gcloud secrets create openai-api-key --data-file=- || echo "Secret exists"
echo $ANTHROPIC_API_KEY | gcloud secrets create anthropic-api-key --data-file=- || echo "Secret exists"

# Step 5: Deploy to Cloud Run
echo "🚢 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME:$IMAGE_TAG \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --cpu 1 \
  --memory 2Gi \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --set-env-vars "ENVIRONMENT=production,LOG_LEVEL=info" \
  --set-secrets "OPENAI_API_KEY=openai-api-key:latest,ANTHROPIC_API_KEY=anthropic-api-key:latest"

# Step 6: Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)')

echo "✅ Deployment complete!"
echo "🌐 API URL: $SERVICE_URL"
echo "📖 API Docs: $SERVICE_URL/docs"
echo "🏥 Health Check: $SERVICE_URL/api/v1/health"

# Optional: Set up custom domain
# echo "🌍 Setting up custom domain..."
# gcloud run domain-mappings create \
#   --service $SERVICE_NAME \
#   --domain api.peruguide.com \
#   --region $REGION
