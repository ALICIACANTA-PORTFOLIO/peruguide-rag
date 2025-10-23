# 👥 Development Roles & Responsibilities

## PeruGuide AI - Professional Team Structure

Este documento define los **roles profesionales**, **responsabilidades**, **entregables** y **estándares de calidad** para el desarrollo del proyecto **PeruGuide AI (Nivel 2: Production-Ready)**.

---

## 🎯 Principios Generales

### **Arquitectura Limpia (Clean Architecture)**

Seguimos los principios de **Clean Architecture** y **SOLID**:

1. **Separation of Concerns**: Cada módulo tiene una responsabilidad única
2. **Dependency Inversion**: Dependencias apuntan hacia abstracciones
3. **Interface Segregation**: Interfaces específicas en lugar de generales
4. **Single Responsibility**: Una clase/función = una responsabilidad
5. **Open/Closed**: Abierto para extensión, cerrado para modificación

### **Estándares de Código**

```python
# ✅ GOOD: Clean, documented, typed
def chunk_text(
    text: str, 
    chunk_size: int = 512, 
    overlap: int = 64
) -> list[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Overlapping characters between chunks
        
    Returns:
        List of text chunks
        
    Raises:
        ValueError: If chunk_size <= overlap
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be > overlap")
    # Implementation...

# ❌ BAD: No types, no docs, unclear
def chunk(t, s=512, o=64):
    return [...]
```

### **Testing Requirements**

- **Unit Tests**: Cada función/clase debe tener tests
- **Integration Tests**: Flujos completos end-to-end
- **Coverage**: Mínimo 75% de cobertura
- **Documentation**: Docstrings en formato Google

---

## 👤 Role 1: Data Engineer

### **Owner**: [Tu Nombre - Data Engineering Hat]

### **Misión**
Diseñar e implementar pipelines robustos para ingestión, procesamiento y transformación de datos (PDFs → chunks embedables).

### **Responsabilidades**

#### 1. **Data Ingestion (PDF Loading)**
```python
# Módulos a implementar:
src/data_pipeline/loaders/
├─ pdf_loader.py          # Wrapper de PyPDFLoader
└─ directory_loader.py    # Batch loading de múltiples PDFs
```

**Tareas:**
- [ ] Implementar `PDFLoader` con manejo de errores
- [ ] Soportar encoding UTF-8 y Latin-1
- [ ] Extraer metadata (filename, departamento, categoría)
- [ ] Logging estructurado de cada documento procesado

**Ejemplo de implementación esperada:**
```python
from typing import List, Dict
from pathlib import Path
import structlog

logger = structlog.get_logger()

class PDFLoader:
    """Load and extract text from PDF files with metadata."""
    
    def load_pdf(self, pdf_path: Path) -> Dict[str, any]:
        """
        Load a single PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with keys: text, metadata, page_count
            
        Raises:
            FileNotFoundError: If PDF not found
            PDFReadError: If PDF is corrupted
        """
        logger.info("loading_pdf", path=str(pdf_path))
        # Implementation with error handling
        
    def load_directory(self, dir_path: Path) -> List[Dict]:
        """Load all PDFs from a directory recursively."""
        # Implementation
```

#### 2. **Text Preprocessing**
```python
# Módulos a implementar:
src/data_pipeline/processors/
├─ cleaner.py                # Text cleaning
└─ metadata_extractor.py     # Metadata extraction
```

**Tareas:**
- [ ] Limpieza de caracteres especiales
- [ ] Normalización de encoding
- [ ] Detección de idioma (ES/EN)
- [ ] Extracción de metadata estructurada

#### 3. **Text Chunking**
```python
# Módulo a implementar:
src/data_pipeline/chunkers/
└─ recursive_splitter.py
```

**Tareas:**
- [ ] Implementar `RecursiveCharacterTextSplitter`
- [ ] Configuración: `chunk_size=512`, `overlap=64`
- [ ] Preservar contexto semántico
- [ ] Validación de calidad de chunks

### **Entregables**

1. ✅ **Código Production-Ready**
   - `src/data_pipeline/` completo
   - Type hints en todas las funciones
   - Docstrings formato Google
   - Error handling robusto

2. ✅ **Tests (>80% coverage)**
   - `tests/unit/test_pdf_loader.py`
   - `tests/unit/test_cleaner.py`
   - `tests/unit/test_chunking.py`
   - `tests/integration/test_data_pipeline.py`

3. ✅ **Documentación**
   - `docs/architecture/feature-pipeline.md`
   - Diagramas de flujo (mermaid)
   - Ejemplos de uso

4. ✅ **Data Quality Metrics**
   - Dashboard de calidad de datos
   - Métricas: # docs processed, avg chunk size, errors

### **Métricas de Éxito**

| Métrica | Target | Medición |
|---------|--------|----------|
| Throughput | >10 PDFs/min | Benchmark script |
| Error Rate | <1% | Logs analysis |
| Chunk Quality | >90% valid | Manual review |
| Test Coverage | >80% | pytest-cov |

---

## 👤 Role 2: ML Engineer

### **Owner**: [Tu Nombre - ML Engineering Hat]

### **Misión**
Implementar pipelines de ML para embeddings, retrieval, RAG chain y evaluación con RAGAS.

### **Responsabilidades**

#### 1. **Embedding Pipeline**
```python
# Módulos a implementar:
src/embedding_pipeline/
├─ models/
│  └─ sentence_transformer.py
└─ batch_processor.py
```

**Tareas:**
- [ ] Implementar embedding generation con HuggingFace
- [ ] Batch processing (batch_size=32)
- [ ] Normalización de embeddings (cosine similarity)
- [ ] Caching para evitar re-computación

**Ejemplo esperado:**
```python
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

class EmbeddingModel:
    """Generate embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = "paraphrase-multilingual-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name)
        
    def embed_texts(
        self, 
        texts: List[str], 
        batch_size: int = 32
    ) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            
        Returns:
            Numpy array of embeddings (n_texts, embedding_dim)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True
        )
        return embeddings
```

#### 2. **Vector Store Management**
```python
# Módulos a implementar:
src/vector_store/
├─ abstract_store.py    # Abstract base class
├─ faiss_store.py       # FAISS implementation
└─ chroma_store.py      # ChromaDB implementation
```

**Tareas:**
- [ ] Abstract interface para vector stores
- [ ] Implementación FAISS (development)
- [ ] Implementación Chroma (production)
- [ ] Persistencia y carga de índices

#### 3. **Retrieval Pipeline**
```python
# Módulos a implementar:
src/retrieval_pipeline/
├─ retrievers/
│  ├─ dense_retriever.py
│  └─ hybrid_retriever.py
└─ rerankers/
   └─ cross_encoder.py
```

**Tareas:**
- [ ] Dense retrieval (vector similarity)
- [ ] Top-k selection (k=5, threshold=0.7)
- [ ] Optional: Hybrid retrieval (dense + sparse)
- [ ] Optional: Cross-encoder reranking

#### 4. **Inference Pipeline (RAG Chain)**
```python
# Módulos a implementar:
src/inference_pipeline/
├─ llm/
│  ├─ mistral_client.py
│  └─ prompt_templates.py
├─ chains/
│  └─ rag_chain.py
└─ postprocessing/
   ├─ citation_formatter.py
   └─ confidence_scorer.py
```

**Tareas:**
- [ ] Integración con Mistral-7B
- [ ] Prompt engineering (system + user prompts)
- [ ] LangChain RAG orchestration
- [ ] Citation formatting
- [ ] Confidence scoring

#### 5. **Evaluation (RAGAS)**
```python
# Módulos a implementar:
src/evaluation/
├─ ragas_evaluator.py
├─ test_dataset.json
└─ metrics_logger.py
```

**Tareas:**
- [ ] Crear test dataset (100+ Q&A pairs)
- [ ] Implementar RAGAS evaluation
- [ ] Métricas: faithfulness, answer_relevancy, context_precision
- [ ] Logging de resultados

### **Entregables**

1. ✅ **Embedding Pipeline**
   - Código completo con tests
   - Benchmark de performance

2. ✅ **RAG Chain Funcional**
   - End-to-end pipeline working
   - Latencia <3s (p95)

3. ✅ **RAGAS Evaluation Report**
   - Faithfulness >0.85
   - Answer Relevancy >0.80
   - Context Precision >0.75

4. ✅ **Documentación Técnica**
   - `docs/architecture/inference-pipeline.md`
   - Prompt engineering guide
   - Evaluation methodology

### **Métricas de Éxito**

| Métrica | Target | Status |
|---------|--------|--------|
| Faithfulness | >0.85 | TBD |
| Answer Relevancy | >0.80 | TBD |
| Context Precision | >0.75 | TBD |
| Latency (p95) | <3 sec | TBD |
| Test Coverage | >75% | TBD |

---

## 👤 Role 3: Backend Engineer

### **Owner**: [Tu Nombre - Backend Engineering Hat]

### **Misión**
Diseñar e implementar REST API con FastAPI, integrando todos los componentes del sistema.

### **Responsabilidades**

#### 1. **API Core**
```python
# Módulos a implementar:
api/
├─ main.py              # FastAPI app
├─ routers/
│  ├─ query.py          # /query endpoint
│  ├─ feedback.py       # /feedback endpoint
│  └─ admin.py          # /health, /metrics
├─ models/
│  └─ schemas.py        # Pydantic models
└─ middleware/
   ├─ auth.py
   └─ rate_limit.py
```

**Tareas:**
- [ ] FastAPI app initialization
- [ ] CORS configuration
- [ ] Request/Response models (Pydantic)
- [ ] Error handling middleware
- [ ] OpenAPI documentation

**Ejemplo de endpoint esperado:**
```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter(prefix="/api/v1")

class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(5, ge=1, le=20)
    filters: Optional[dict] = None

class Source(BaseModel):
    """Source citation model."""
    document: str
    page: int
    confidence: float
    excerpt: str

class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    answer: str
    sources: List[Source]
    confidence: float
    latency_ms: int

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Process a user query using RAG.
    
    Args:
        request: Query request with question and parameters
        
    Returns:
        Answer with source citations and confidence score
        
    Raises:
        HTTPException: If processing fails
    """
    # Implementation
```

#### 2. **Middleware & Security**

**Tareas:**
- [ ] Rate limiting (60 req/min)
- [ ] Authentication (optional)
- [ ] Request logging
- [ ] Error handling

#### 3. **Integration with ML Pipeline**

**Tareas:**
- [ ] Integrar RAG chain
- [ ] Async processing
- [ ] Connection pooling
- [ ] Caching strategy

### **Entregables**

1. ✅ **FastAPI Application**
   - 3+ endpoints funcionales
   - OpenAPI docs auto-generated
   - Error handling robusto

2. ✅ **Tests**
   - `tests/integration/test_api.py`
   - Test de cada endpoint
   - Load testing script

3. ✅ **API Documentation**
   - `docs/api/overview.md`
   - `docs/api/endpoints.md`
   - Ejemplos de uso con curl

### **Métricas de Éxito**

| Métrica | Target | Status |
|---------|--------|--------|
| Uptime | >99% | TBD |
| Response Time (p95) | <3s | TBD |
| Throughput | >100 RPS | TBD |
| Error Rate | <1% | TBD |

---

## 👤 Role 4: Frontend Engineer

### **Owner**: [Tu Nombre - Frontend Engineering Hat]

### **Misión**
Implementar interfaz de usuario con Streamlit, siguiendo principios de UX/storytelling.

### **Responsabilidades**

#### 1. **Main App**
```python
# Módulos a implementar:
app/
├─ Home.py
└─ pages/
   ├─ Chat.py
   ├─ Sources.py
   └─ Analytics.py
```

**Tareas:**
- [ ] Chat interface (conversacional)
- [ ] Source display (badges con links)
- [ ] Confidence visualization
- [ ] Export functionality (PDF, JSON)

**Ejemplo esperado:**
```python
import streamlit as st
from typing import List

st.set_page_config(
    page_title="PeruGuide AI",
    page_icon="🇵🇪",
    layout="wide"
)

def render_chat_interface():
    """Render main chat interface."""
    st.title("🇵🇪 PeruGuide AI")
    st.markdown("""
    Pregúntame lo que quieras sobre turismo en Perú.
    Tengo acceso a +5,000 páginas de guías oficiales.
    """)
    
    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources if available
            if "sources" in message:
                render_sources(message["sources"])
    
    # User input
    if prompt := st.chat_input("¿Qué quieres saber sobre Perú?"):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Call API
        response = call_api(prompt)
        
        # Add assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["answer"],
            "sources": response["sources"],
            "confidence": response["confidence"]
        })
        
        st.rerun()

def render_sources(sources: List[dict]):
    """Render source citations."""
    st.markdown("### 📄 Fuentes")
    for source in sources:
        with st.expander(f"{source['document']} (p. {source['page']})"):
            st.markdown(source['excerpt'])
            st.metric("Confianza", f"{source['confidence']:.2f}")
```

#### 2. **UX/UI Design**

**Tareas:**
- [ ] Design system (colores, tipografía)
- [ ] Responsive layout
- [ ] Loading states
- [ ] Error messages user-friendly

### **Entregables**

1. ✅ **Streamlit App Funcional**
   - Chat interface completa
   - Source display
   - Analytics dashboard

2. ✅ **UX Documentation**
   - User flows
   - Design decisions
   - Accessibility audit

### **Métricas de Éxito**

| Métrica | Target | Status |
|---------|--------|--------|
| User Satisfaction | >4.2/5 | TBD |
| Task Completion | >85% | TBD |
| Accessibility | WCAG 2.1 AA | TBD |

---

## 👤 Role 5: DevOps Engineer

### **Owner**: [Tu Nombre - DevOps Hat]

### **Misión**
Implementar CI/CD, containerización y observability.

### **Responsabilidades**

#### 1. **CI/CD Pipelines**
```yaml
# .github/workflows/ci.yml
# .github/workflows/cd.yml
```

**Tareas:**
- [ ] CI: pytest, coverage, linting
- [ ] CD: deploy on merge to main
- [ ] Automated testing
- [ ] Security scanning

#### 2. **Containerization**
```dockerfile
# docker/Dockerfile
# docker/docker-compose.yml
```

**Tareas:**
- [ ] Multi-stage Docker build
- [ ] Docker Compose para local dev
- [ ] Volume management
- [ ] Health checks

#### 3. **Observability**

**Tareas:**
- [ ] Structured logging (structlog)
- [ ] Prometheus metrics
- [ ] Grafana dashboards (opcional Nivel 2)
- [ ] Alerting rules

### **Entregables**

1. ✅ **CI/CD Pipeline Working**
2. ✅ **Docker Setup**
3. ✅ **Monitoring Dashboard**
4. ✅ **Deployment Guide**

---

## 👤 Role 6: QA Engineer

### **Owner**: [Tu Nombre - QA Hat]

### **Misión**
Asegurar calidad mediante testing exhaustivo.

### **Responsabilidades**

**Tareas:**
- [ ] Unit tests (>75% coverage)
- [ ] Integration tests
- [ ] E2E tests
- [ ] Performance tests
- [ ] Test documentation

### **Entregables**

1. ✅ **Test Suite Completo**
2. ✅ **Coverage Report (>75%)**
3. ✅ **QA Documentation**

---

## 👤 Role 7: Technical Writer

### **Owner**: [Tu Nombre - Documentation Hat]

### **Misión**
Documentar todo el proyecto.

### **Responsabilidades**

**Tareas:**
- [ ] README narrativo
- [ ] Architecture docs
- [ ] API reference
- [ ] Deployment guide
- [ ] Troubleshooting guide

### **Entregables**

1. ✅ **MkDocs Site Completo**
2. ✅ **API Documentation**
3. ✅ **User Guides**

---

## 📅 Timeline & Coordination

### **Semana 1: Foundation**
- **Data Engineer**: Feature pipeline
- **ML Engineer**: Embedding pipeline
- **Backend Engineer**: API skeleton

### **Semana 2: Integration**
- **ML Engineer**: RAG chain
- **Backend Engineer**: API endpoints
- **Frontend Engineer**: UI básica

### **Semana 3: Testing**
- **QA Engineer**: Test suite
- **ML Engineer**: RAGAS evaluation
- **DevOps**: CI/CD setup

### **Semana 4: Deployment**
- **DevOps Engineer**: Docker + deploy
- **Technical Writer**: Documentation
- **All**: Final testing & launch

---

## 📊 Definition of Done (DoD)

Para considerar un componente "completo", debe cumplir:

- ✅ **Code**: Implementado con type hints y docstrings
- ✅ **Tests**: >75% coverage, todos pasando
- ✅ **Docs**: Documentado en MkDocs
- ✅ **Review**: Code review realizado
- ✅ **Integration**: Integrado con el resto del sistema
- ✅ **Performance**: Cumple métricas target

---

## 🎯 Next Steps

1. **Leer este documento completo** ✅ (completado ahora)
2. **Revisar estructura del proyecto** → Ver README.md
3. **Setup ambiente de desarrollo** → Ver docs/getting-started/
4. **Comenzar implementación** → Seguir roadmap semanal

---

**¿Listo para comenzar? 🚀**
