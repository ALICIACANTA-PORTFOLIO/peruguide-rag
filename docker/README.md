# PeruGuide RAG - Docker Setup

## Quick Start

### 1. Start Database Container
```bash
# Start PostgreSQL (and optionally Redis)
docker-compose up -d postgres redis

# Check status
docker-compose ps

# View logs
docker-compose logs -f postgres
```

### 2. Start with pgAdmin (Development)
```bash
# Start with development profile (includes pgAdmin)
docker-compose --profile dev up -d

# Access pgAdmin: http://localhost:5050
# Email: admin@peruguide.local
# Password: admin123
```

### 3. Stop Containers
```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

## Configuration

All settings can be customized via `.env` file:

```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=peruguide
POSTGRES_USER=peruguide_user
POSTGRES_PASSWORD=changeme123

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=changeme123
```

## Database Schema

The database is automatically initialized with:
- **Schema:** `rag`
- **Tables:**
  - `query_logs` - Query and response tracking
  - `retrieval_logs` - Retrieved document tracking
  - `feedback` - User feedback
  - `documents` - Document metadata cache
  - `document_chunks` - Document chunks
  - `evaluation_results` - RAGAS evaluation results

## Connecting from Python

```python
from src.config.settings import get_settings
from src.database import get_session

# Get settings
settings = get_settings()
print(settings.database.database_url)

# Use database
async with get_session() as session:
    result = await session.execute(text("SELECT version()"))
    print(result.scalar())
```

## Health Check

```bash
# Check if database is running
docker-compose exec postgres pg_isready -U peruguide_user -d peruguide

# Connect to database
docker-compose exec postgres psql -U peruguide_user -d peruguide

# Run health check from Python
python -c "
import asyncio
from src.database import health_check
result = asyncio.run(health_check())
print(f'Database healthy: {result}')
"
```

## Backup & Restore

### Backup
```bash
# Backup database
docker-compose exec postgres pg_dump -U peruguide_user peruguide > backup.sql

# Backup with compression
docker-compose exec postgres pg_dump -U peruguide_user peruguide | gzip > backup.sql.gz
```

### Restore
```bash
# Restore database
docker-compose exec -T postgres psql -U peruguide_user peruguide < backup.sql

# Restore from compressed backup
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U peruguide_user peruguide
```

## Troubleshooting

### Connection Refused
```bash
# Check if container is running
docker-compose ps

# Check logs
docker-compose logs postgres

# Restart container
docker-compose restart postgres
```

### Permission Denied
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Reset permissions
docker-compose down -v
docker-compose up -d postgres
```

### Performance Issues
```bash
# Check connection pool settings in .env
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Monitor connections
docker-compose exec postgres psql -U peruguide_user -d peruguide -c "SELECT * FROM pg_stat_activity;"
```

## Production Deployment

For production, consider:

1. **Use managed database service** (AWS RDS, Azure Database, etc.)
2. **Enable SSL connections**
3. **Use secrets management** (AWS Secrets Manager, HashiCorp Vault)
4. **Configure backup automation**
5. **Enable monitoring** (CloudWatch, Prometheus)
6. **Set up read replicas** for high availability

Example production `.env`:
```bash
POSTGRES_HOST=your-rds-endpoint.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_DB=peruguide_prod
POSTGRES_USER=peruguide_prod_user
POSTGRES_PASSWORD=${DB_PASSWORD}  # From secrets manager
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
```
