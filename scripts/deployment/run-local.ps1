# PowerShell script for local Docker deployment on Windows

Write-Host "🚀 Starting PeruGuide RAG API locally with Docker..." -ForegroundColor Green

# Check if .env file exists
if (-Not (Test-Path .env)) {
    Write-Host "⚠️  .env file not found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "📝 Please edit .env file with your API keys before proceeding." -ForegroundColor Yellow
    exit 1
}

# Build the Docker image
Write-Host "🏗️  Building Docker image..." -ForegroundColor Cyan
docker build -t peruguide-rag-api:latest .

# Run the container
Write-Host "🚢 Starting container..." -ForegroundColor Cyan
docker run -d `
  --name peruguide-api `
  -p 8000:8000 `
  --env-file .env `
  -v ${PWD}/data:/app/data `
  peruguide-rag-api:latest

Write-Host "`n✅ Container started!" -ForegroundColor Green
Write-Host "🌐 API URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📖 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🏥 Health Check: http://localhost:8000/api/v1/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 View logs: docker logs -f peruguide-api" -ForegroundColor Yellow
Write-Host "🛑 Stop container: docker stop peruguide-api" -ForegroundColor Yellow
Write-Host "🗑️  Remove container: docker rm peruguide-api" -ForegroundColor Yellow
