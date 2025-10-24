#!/bin/bash
# Deploy PeruGuide RAG API to Azure Container Apps

set -e

echo "🚀 Deploying PeruGuide RAG to Azure Container Apps..."

# Configuration
RESOURCE_GROUP=${RESOURCE_GROUP:-"peruguide-rg"}
LOCATION=${LOCATION:-"eastus"}
CONTAINER_APP_ENV=${CONTAINER_APP_ENV:-"peruguide-env"}
CONTAINER_APP_NAME=${CONTAINER_APP_NAME:-"peruguide-api"}
CONTAINER_REGISTRY=${CONTAINER_REGISTRY:-"peruguideacr"}
IMAGE_NAME="peruguide-rag-api"
IMAGE_TAG=${IMAGE_TAG:-"latest"}

# Step 1: Create Resource Group
echo "📦 Creating resource group..."
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Step 2: Create Container Registry
echo "🐳 Creating Azure Container Registry..."
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_REGISTRY \
  --sku Basic \
  --admin-enabled true

# Step 3: Build and push Docker image
echo "🏗️  Building Docker image..."
az acr build \
  --registry $CONTAINER_REGISTRY \
  --image $IMAGE_NAME:$IMAGE_TAG \
  --file Dockerfile \
  .

# Step 4: Create Container App Environment
echo "🌐 Creating Container App Environment..."
az containerapp env create \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Step 5: Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $CONTAINER_REGISTRY --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $CONTAINER_REGISTRY --query passwords[0].value -o tsv)
ACR_LOGIN_SERVER=$(az acr show --name $CONTAINER_REGISTRY --query loginServer -o tsv)

# Step 6: Deploy Container App
echo "🚢 Deploying Container App..."
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_APP_ENV \
  --image $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 1.0 \
  --memory 2.0Gi \
  --env-vars \
    "ENVIRONMENT=production" \
    "LOG_LEVEL=info" \
    "OPENAI_API_KEY=$OPENAI_API_KEY" \
    "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"

# Step 7: Get the app URL
APP_URL=$(az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)

echo "✅ Deployment complete!"
echo "🌐 API URL: https://$APP_URL"
echo "📖 API Docs: https://$APP_URL/docs"
echo "🏥 Health Check: https://$APP_URL/api/v1/health"
