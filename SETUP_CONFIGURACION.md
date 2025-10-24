# PeruGuide RAG - Configuración Completa

## 🎉 ¡Configuración Parametrizada Implementada!

### ✅ Archivos Creados

#### 1. **Docker & Database**
- `docker-compose.yml` - Orquestación de contenedores
- `docker/init-db/01-init.sql` - Script de inicialización DB
- `docker/README.md` - Guía de uso de Docker

#### 2. **Configuración (Best Practices)**
- `src/config/settings.py` - Sistema de configuración con Pydantic
- `.env.example` actualizado - Variables parametrizadas
- `.env` - Copia para desarrollo local

#### 3. **Database Module**
- `src/database/database.py` - Conexión async con SQLAlchemy
- `src/database/models.py` - Modelos para analytics y feedback
- `src/database/__init__.py` - Exports del módulo

#### 4. **Ejemplos**
- `examples/01_configuration_database.py` - Ejemplos de uso

---

## 🏗️ Arquitectura de Configuración

### Principios Implementados

1. **12-Factor App** ✅
   - Configuración en variables de entorno
   - Separación de config y código
   - Un codebase, múltiples deploys

2. **Type-Safe Configuration** ✅
   - Pydantic Settings con validación
   - Type hints en todo el código
   - Valores por defecto sensatos

3. **Hierarchical Settings** ✅
   ```python
   settings.app.app_name
   settings.database.database_url
   settings.data_processing.chunk_size
   ```

4. **Domain-Agnostic** ✅
   - Configuración flexible para cualquier dominio
   - Metadata fields personalizables
   - Source directories configurables

---

## 🚀 Pasos para Iniciar

### 1. **Iniciar Docker Desktop**
```bash
# Abrir Docker Desktop manualmente
# Esperar a que Docker esté corriendo

# Verificar que Docker está activo
docker --version
docker ps
```

### 2. **Iniciar Contenedores**
```bash
# Solo PostgreSQL
docker-compose up -d postgres

# PostgreSQL + Redis
docker-compose up -d postgres redis

# Con pgAdmin (desarrollo)
docker-compose --profile dev up -d
```

### 3. **Verificar Estado**
```bash
# Ver contenedores activos
docker-compose ps

# Ver logs
docker-compose logs -f postgres

# Health check de PostgreSQL
docker-compose exec postgres pg_isready -U peruguide_user -d peruguide
```

### 4. **Ejecutar Ejemplos**
```bash
# Activar entorno
conda activate peruguide-rag

# Ejecutar ejemplo de configuración
python examples/01_configuration_database.py
```

---

## 📊 Base de Datos (PostgreSQL)

### Schema: `rag`

#### Tablas Creadas:

1. **`query_logs`** - Tracking de queries y respuestas
   - session_id, query_text, response_text
   - response_time_ms, retrieved_chunks
   - model_name, metadata (JSONB)

2. **`retrieval_logs`** - Documents retrieved
   - query_log_id (FK), document_id, chunk_id
   - relevance_score, rank
   - metadata (JSONB)

3. **`feedback`** - User feedback
   - query_log_id (FK), rating (1-5)
   - feedback_text, feedback_type
   - metadata (JSONB)

4. **`documents`** - Document metadata cache
   - document_id (unique), source_path, filename
   - chunk_count, embedding_model
   - processed_at, last_updated, metadata (JSONB)

5. **`document_chunks`** - Chunk storage
   - document_id (FK), chunk_id, chunk_index
   - chunk_text, token_count
   - metadata (JSONB)

6. **`evaluation_results`** - RAGAS metrics
   - run_id, query_text, response_text, ground_truth
   - faithfulness, answer_relevancy, context_precision, context_recall
   - metadata (JSONB)

### Índices de Performance
- Todos los campos frecuentes están indexados
- JSONB para metadata flexible
- Foreign keys con CASCADE para integridad

---

## 🔧 Configuración Parametrizada

### Secciones de Configuración

```python
from src.config.settings import get_settings

settings = get_settings()

# App Settings
settings.app.app_name          # "PeruGuide AI"
settings.app.environment       # "development"
settings.app.debug             # True

# Database Settings
settings.database.postgres_host     # "localhost"
settings.database.postgres_port     # 5432
settings.database.database_url      # Constructed URL
settings.database.database_pool_size # 10

# Data Processing (Domain-Agnostic!)
settings.data_processing.pdf_source_dir      # "./data/raw"
settings.data_processing.chunk_size          # 512
settings.data_processing.metadata_fields     # ["filename", "category", "region"]

# LLM Settings
settings.llm.llm_model_name          # "mistralai/Mistral-7B-Instruct-v0.3"
settings.llm.llm_temperature         # 0.3

# Embedding Settings
settings.embedding.embedding_model_name  # "paraphrase-multilingual-mpnet-base-v2"
settings.embedding.embedding_dimension   # 768

# Vector Store
settings.vector_store.vector_store_type      # "chroma"
settings.vector_store.chroma_collection_name # "peruguide_documents"
```

---

## 💡 Uso Domain-Agnostic

### Tourism (Default)
```bash
# .env
PDF_SOURCE_DIR=./Complementarios Peru
METADATA_FIELDS=["filename", "category", "region", "language"]
CHROMA_COLLECTION_NAME=peru_tourism
```

### Legal Documents
```bash
# .env
PDF_SOURCE_DIR=./data/legal
METADATA_FIELDS=["filename", "case_number", "jurisdiction", "date"]
CHROMA_COLLECTION_NAME=legal_documents
```

### Academic Papers
```bash
# .env
PDF_SOURCE_DIR=./data/papers
METADATA_FIELDS=["filename", "author", "journal", "year", "doi"]
CHROMA_COLLECTION_NAME=academic_papers
```

---

## 📝 Ejemplo de Uso

```python
import asyncio
from src.config.settings import get_settings
from src.database import get_session, QueryLog

async def main():
    # Get configuration
    settings = get_settings()
    print(f"App: {settings.app.app_name}")
    print(f"DB: {settings.database.database_url}")
    
    # Use database
    async with get_session() as session:
        # Insert query log
        log = QueryLog(
            query_text="Example query",
            response_text="Example response",
            model_name=settings.llm.llm_model_name,
        )
        session.add(log)
        await session.commit()
        print(f"Logged query: {log.id}")

asyncio.run(main())
```

---

## 🎯 Siguientes Pasos

### Day 2: Text Processors
1. ✅ Configuración parametrizada
2. ✅ Base de datos PostgreSQL
3. ⏭️ **Implementar TextCleaner**
4. ⏭️ **Implementar MetadataExtractor**
5. ⏭️ Tests >80% coverage

### Comandos para Day 2:
```bash
# Iniciar Docker (si no está corriendo)
docker-compose up -d postgres

# Crear TextCleaner
code src/data_pipeline/processors/cleaner.py

# Crear tests
code tests/unit/data_pipeline/test_cleaner.py

# Ejecutar tests
pytest tests/unit/data_pipeline/test_cleaner.py -v --cov
```

---

## 📚 Referencias

### Best Practices Implementadas:
- ✅ **12-Factor App** - Configuration
- ✅ **Pydantic Settings** - Type safety
- ✅ **SQLAlchemy Async** - Non-blocking DB
- ✅ **Connection Pooling** - Performance
- ✅ **Structured Logging** - Observability
- ✅ **Health Checks** - Monitoring
- ✅ **Domain-Agnostic Design** - Flexibility

### Documentación:
- [12-Factor App](https://12factor.net/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## 🔍 Verificación

### Checklist:
- ✅ docker-compose.yml creado
- ✅ SQL init script creado
- ✅ Settings module con Pydantic
- ✅ Database module con SQLAlchemy async
- ✅ Models con proper relationships
- ✅ .env.example actualizado
- ✅ .env copiado
- ✅ Dependencias instaladas
- ✅ Ejemplos de uso creados
- ✅ Documentación completa

### Para Verificar (una vez Docker esté corriendo):
```bash
# 1. Iniciar Docker Desktop
# 2. Iniciar contenedores
docker-compose up -d postgres

# 3. Verificar conexión
docker-compose exec postgres psql -U peruguide_user -d peruguide -c "\dt rag.*"

# 4. Ejecutar ejemplo
python examples/01_configuration_database.py
```

---

## 🎉 ¡Listo para Continuar!

Ahora tienes:
- ✅ **Configuración parametrizada** (Pydantic Settings)
- ✅ **Base de datos PostgreSQL** (Docker)
- ✅ **Modelos SQLAlchemy** (Analytics & Feedback)
- ✅ **Best practices** (12-Factor, Type Safety, Async)
- ✅ **Domain-agnostic design** (Funciona con cualquier dominio)

**Next:** Day 2 - TextCleaner & MetadataExtractor! 🚀
