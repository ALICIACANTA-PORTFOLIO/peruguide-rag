#!/bin/bash
# Deploy PeruGuide RAG API to AWS ECS (Elastic Container Service)

set -e

echo "🚀 Deploying PeruGuide RAG to AWS ECS..."

# Configuration
AWS_REGION=${AWS_REGION:-"us-east-1"}
ECR_REPOSITORY=${ECR_REPOSITORY:-"peruguide-rag-api"}
ECS_CLUSTER=${ECS_CLUSTER:-"peruguide-cluster"}
ECS_SERVICE=${ECS_SERVICE:-"peruguide-service"}
TASK_FAMILY=${TASK_FAMILY:-"peruguide-task"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}

# Step 1: Create ECR Repository
echo "📦 Creating ECR repository..."
aws ecr create-repository \
  --repository-name $ECR_REPOSITORY \
  --region $AWS_REGION \
  || echo "Repository already exists"

# Step 2: Get ECR login
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com

# Step 3: Build Docker image
echo "🏗️  Building Docker image..."
docker build -t $ECR_REPOSITORY:$IMAGE_TAG .

# Step 4: Tag and push image
ECR_URI=$(aws ecr describe-repositories \
  --repository-names $ECR_REPOSITORY \
  --region $AWS_REGION \
  --query 'repositories[0].repositoryUri' \
  --output text)

echo "🏷️  Tagging image..."
docker tag $ECR_REPOSITORY:$IMAGE_TAG $ECR_URI:$IMAGE_TAG

echo "⬆️  Pushing image to ECR..."
docker push $ECR_URI:$IMAGE_TAG

# Step 5: Create ECS Cluster
echo "🌐 Creating ECS cluster..."
aws ecs create-cluster \
  --cluster-name $ECS_CLUSTER \
  --region $AWS_REGION \
  || echo "Cluster already exists"

# Step 6: Register Task Definition
echo "📝 Registering task definition..."
cat > task-definition.json <<EOF
{
  "family": "$TASK_FAMILY",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "peruguide-api",
      "image": "$ECR_URI:$IMAGE_TAG",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "LOG_LEVEL", "value": "info"}
      ],
      "secrets": [
        {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:ACCOUNT_ID:secret:openai-api-key"},
        {"name": "ANTHROPIC_API_KEY", "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:ACCOUNT_ID:secret:anthropic-api-key"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/peruguide",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "api"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/api/v1/health || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
EOF

aws ecs register-task-definition \
  --cli-input-json file://task-definition.json \
  --region $AWS_REGION

# Step 7: Create/Update ECS Service
echo "🚢 Creating ECS service..."
aws ecs create-service \
  --cluster $ECS_CLUSTER \
  --service-name $ECS_SERVICE \
  --task-definition $TASK_FAMILY \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}" \
  --region $AWS_REGION \
  || aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service $ECS_SERVICE \
    --task-definition $TASK_FAMILY \
    --region $AWS_REGION

echo "✅ Deployment complete!"
echo "📝 Clean up: rm task-definition.json"
echo "🔍 Check service: aws ecs describe-services --cluster $ECS_CLUSTER --services $ECS_SERVICE"
