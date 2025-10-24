#!/bin/bash
# Local development with Docker

set -e

echo "🚀 Starting PeruGuide RAG API locally with Docker..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before proceeding."
    exit 1
fi

# Build the Docker image
echo "🏗️  Building Docker image..."
docker build -t peruguide-rag-api:latest .

# Run the container
echo "🚢 Starting container..."
docker run -d \
  --name peruguide-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  peruguide-rag-api:latest

echo "✅ Container started!"
echo "🌐 API URL: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/api/v1/health"
echo ""
echo "📊 View logs: docker logs -f peruguide-api"
echo "🛑 Stop container: docker stop peruguide-api"
echo "🗑️  Remove container: docker rm peruguide-api"
