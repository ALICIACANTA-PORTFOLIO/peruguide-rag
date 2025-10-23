# 📚 BEST PRACTICES & TECHNICAL INSIGHTS
## Extraídos de Materiales de Referencia

---

## 🎯 LLM ENGINEERING BEST PRACTICES

### Del "LLM Engineer's Handbook" (Iusztin & Labonne, 2024)

#### **1. RAG Pipeline Design Principles**

##### **Chunking Strategy**
```python
# ❌ BAD: Fixed-size chunking sin overlap
chunks = text.split(every=512)

# ✅ GOOD: Recursive chunking con overlap y metadata
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=64,  # 12.5% overlap para preservar contexto
    length_function=len,
    separators=["\n\n", "\n", ".", " ", ""],  # Prioriza separadores naturales
    keep_separator=True
)

chunks = splitter.create_documents(
    texts=[text],
    metadatas=[{"source": "doc.pdf", "page": 1, "department": "Cusco"}]
)
```

**Rationale:**
- Overlap preserva contexto en bordes de chunks
- Separadores naturales mantienen coherencia semántica
- Metadata facilita filtering y source citation

##### **Embedding Selection**
```python
# Para casos multilingües (español + inglés):
model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
# - 768 dimensiones
# - Trained en 50+ lenguajes
# - Balance entre calidad y velocidad
# - ~420MB de modelo

# Para solo español (alternativa):
model_name = "hiiamsid/sentence_similarity_spanish_es"
# - Optimizado para español
# - Menor tamaño

from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs={'device': 'cuda'},  # o 'cpu'
    encode_kwargs={'normalize_embeddings': True}  # Facilita cosine similarity
)
```

##### **Vector Store Configuration**
```python
# FAISS para local development/demo:
from langchain.vectorstores import FAISS

vector_store = FAISS.from_documents(
    documents=chunks,
    embedding=embeddings,
    distance_strategy="COSINE"  # vs DOT_PRODUCT o EUCLIDEAN
)

# Guardar para persistencia
vector_store.save_local("./vector_db/faiss_index")

# Chroma para production (mejor persistencia):
import chromadb
from langchain.vectorstores import Chroma

chroma_client = chromadb.PersistentClient(path="./vector_db/chroma")
vector_store = Chroma(
    client=chroma_client,
    collection_name="peru_tourism",
    embedding_function=embeddings,
    collection_metadata={"hnsw:space": "cosine"}
)
```

**Trade-offs:**
| Feature | FAISS | Chroma |
|---------|-------|--------|
| Speed | ⚡⚡⚡ Fastest | ⚡⚡ Fast |
| Persistence | Manual save | Auto-persist |
| Filtering | Limited | Rich metadata |
| Production | Needs wrapper | Production-ready |
| Setup | Simple | Slightly complex |

**Recomendación:** FAISS para prototipado, Chroma para producción.

##### **Retrieval Strategy**
```python
# ❌ BAD: Naive similarity search
results = vector_store.similarity_search(query, k=5)

# ✅ GOOD: Multi-stage retrieval con reranking
# Stage 1: Cast wide net
candidates = vector_store.similarity_search(
    query, 
    k=20,  # Sobre-recuperar
    filter={"department": "Cusco"}  # Metadata filtering si aplica
)

# Stage 2: Rerank con cross-encoder (opcional pero poderoso)
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
scores = reranker.predict([(query, doc.page_content) for doc in candidates])

# Ordenar por score y tomar top-k
ranked_docs = [doc for _, doc in sorted(zip(scores, candidates), reverse=True)]
final_docs = ranked_docs[:5]
```

**Rationale:**
- Stage 1: Embeddings son fast pero aproximados
- Stage 2: Cross-encoders son lentos pero precisos
- Best of both worlds: Speed + Accuracy

##### **Hybrid Search (Semantic + Keyword)**
```python
from langchain.retrievers import BM25Retriever, EnsembleRetriever

# BM25 para keyword matching (importante para nombres propios)
bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 10

# Semantic retriever
semantic_retriever = vector_store.as_retriever(search_kwargs={"k": 10})

# Ensemble combina ambos
hybrid_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, semantic_retriever],
    weights=[0.3, 0.7]  # Más peso a semantic, pero keyword ayuda
)

results = hybrid_retriever.get_relevant_documents(query)
```

**Casos de uso:**
- Query: "¿Qué ver en Machu Picchu?" → Semantic domina
- Query: "Restaurante Astrid y Gastón en Lima" → Keyword critical

#### **2. Prompt Engineering for RAG**

##### **System Prompt Template**
```python
SYSTEM_PROMPT = """Eres PeruGuide AI, un asistente turístico experto en Perú.

TU ROL:
- Proporcionar información precisa y verificable sobre turismo en Perú
- Basar TODAS tus respuestas en el contexto proporcionado
- Citar la fuente específica de cada información
- Ser honesto cuando no tienes información suficiente

DIRECTRICES:
1. FACTUALIDAD: Solo usa información del contexto. Si el contexto no contiene 
   la información necesaria, di: "No tengo información suficiente para responder 
   con certeza a esa pregunta."

2. CITACIÓN: Después de cada afirmación importante, incluye la fuente entre 
   corchetes [Fuente: nombre_documento, página X]

3. ESTRUCTURA: 
   - Respuestas claras y concisas
   - Usa bullets para listas
   - Divide información compleja en secciones

4. TONO: Amigable pero profesional, como un guía turístico experimentado

5. IDIOMA: Responde en el mismo idioma de la pregunta

CONTEXTO PROPORCIONADO:
{context}

PREGUNTA DEL USUARIO:
{question}

RESPUESTA:"""
```

##### **Few-Shot Examples (para casos complejos)**
```python
FEW_SHOT_EXAMPLES = """
EJEMPLO 1:
Pregunta: "¿Cuál es el mejor mes para visitar Machu Picchu?"
Respuesta: "El mejor periodo para visitar Machu Picchu es durante la estación seca, 
de abril a octubre, siendo junio y julio los meses más populares [Fuente: Guía_Cusco, 
pág. 45]. Sin embargo, estos meses también son los más concurridos. Si prefieres 
menos turistas, considera visitar en abril o septiembre, cuando el clima sigue siendo 
favorable [Fuente: Guía_Cusco, pág. 46].

IMPORTANTE: La temporada de lluvias (noviembre-marzo) puede dificultar el acceso, 
especialmente en febrero cuando cierran el Camino Inca por mantenimiento [Fuente: 
Guía_Cusco, pág. 47]."

EJEMPLO 2:
Pregunta: "Necesito información sobre restaurantes veganos en Arequipa"
Respuesta: "No tengo información suficiente en mis fuentes actuales sobre opciones 
específicamente veganas en Arequipa. Sin embargo, puedo decirte que Arequipa es 
conocida por su gastronomía tradicional que incluye platos como rocoto relleno y 
adobo arequipeño [Fuente: Guía_Gastronomía_Peruana, pág. 78]. 

Te recomendaría contactar directamente con restaurantes locales para consultar 
opciones veganas, o buscar en plataformas especializadas en turismo vegano."

AHORA RESPONDE A LA SIGUIENTE PREGUNTA:
"""
```

**Beneficios de Few-Shot:**
- Enseña el formato deseado
- Muestra manejo de incertidumbre
- Establece nivel de detalle esperado

##### **Dynamic Prompting basado en tipo de query**
```python
def get_prompt_template(query_type):
    """Selecciona prompt según tipo de consulta"""
    
    if query_type == "recommendation":
        return """Eres un asesor turístico. El usuario busca recomendaciones.
        
        Estructura tu respuesta así:
        1. **Recomendación Principal**: [Lo más adecuado]
        2. **Por qué**: [Justificación con fuentes]
        3. **Alternativas**: [2-3 opciones adicionales]
        4. **Consideraciones**: [Clima, presupuesto, dificultad, etc.]
        
        Contexto: {context}
        Pregunta: {question}"""
    
    elif query_type == "factual":
        return """Eres una fuente de información factual sobre Perú.
        
        Proporciona:
        - Respuesta directa y concisa
        - Datos específicos (fechas, precios, ubicaciones)
        - Fuentes de cada dato
        
        Contexto: {context}
        Pregunta: {question}"""
    
    elif query_type == "planning":
        return """Eres un planificador de viajes experto.
        
        Ayuda al usuario a crear un itinerario considerando:
        - Días disponibles
        - Intereses (arqueología, gastronomía, naturaleza)
        - Logística (distancias, transporte)
        - Temporada y clima
        
        Presenta el plan en formato día por día.
        
        Contexto: {context}
        Pregunta: {question}"""
    
    # Default
    return SYSTEM_PROMPT
```

#### **3. Context Window Management**

##### **Token Budget Strategy**
```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3")

def manage_context_window(
    query: str,
    retrieved_docs: list,
    max_tokens: int = 4096,
    reserved_for_response: int = 512
):
    """
    Gestiona el contexto para no exceder la ventana del modelo
    """
    query_tokens = len(tokenizer.encode(query))
    system_prompt_tokens = len(tokenizer.encode(SYSTEM_PROMPT))
    
    available_tokens = max_tokens - query_tokens - system_prompt_tokens - reserved_for_response
    
    # Priorizar documentos por score
    selected_docs = []
    current_tokens = 0
    
    for doc in retrieved_docs:
        doc_tokens = len(tokenizer.encode(doc.page_content))
        
        if current_tokens + doc_tokens <= available_tokens:
            selected_docs.append(doc)
            current_tokens += doc_tokens
        else:
            # Si queda espacio, truncar último documento
            if available_tokens - current_tokens > 100:  # Al menos 100 tokens
                truncated_content = tokenizer.decode(
                    tokenizer.encode(doc.page_content)[:(available_tokens - current_tokens)]
                )
                doc.page_content = truncated_content + "..."
                selected_docs.append(doc)
            break
    
    return selected_docs
```

**Rationale:**
- Modelos tienen límites de tokens
- Reservar espacio para respuesta
- Priorizar calidad sobre cantidad de contexto

#### **4. Response Post-Processing**

##### **Source Citation Extraction**
```python
def add_source_citations(response: str, source_docs: list) -> dict:
    """
    Añade citas de fuentes estructuradas
    """
    # Extraer metadata de documentos usados
    sources = []
    for doc in source_docs:
        source_info = {
            "document": doc.metadata.get("source", "Unknown"),
            "page": doc.metadata.get("page", "N/A"),
            "department": doc.metadata.get("department", "N/A"),
            "excerpt": doc.page_content[:200] + "..."
        }
        sources.append(source_info)
    
    return {
        "response": response,
        "sources": sources,
        "num_sources": len(sources),
        "confidence": calculate_confidence(response, source_docs)
    }

def calculate_confidence(response: str, source_docs: list) -> float:
    """
    Calcula score de confianza basado en:
    - Cantidad de fuentes
    - Relevancia de fuentes
    - Presencia de hedging language ("podría", "posiblemente")
    """
    confidence = 0.5  # Base
    
    # Más fuentes = más confianza
    confidence += min(len(source_docs) * 0.1, 0.3)
    
    # Penalizar hedging language
    hedging_words = ["podría", "posiblemente", "quizás", "probablemente"]
    for word in hedging_words:
        if word in response.lower():
            confidence -= 0.1
    
    # Bonus por citas específicas
    if "[Fuente:" in response:
        confidence += 0.2
    
    return max(0.0, min(1.0, confidence))
```

##### **Hallucination Detection**
```python
from sentence_transformers import SentenceTransformer, util

def detect_hallucination(response: str, source_docs: list, threshold: float = 0.5) -> dict:
    """
    Detecta si la respuesta contiene información no soportada por las fuentes
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Dividir respuesta en afirmaciones
    response_sentences = response.split('. ')
    
    # Concatenar todo el contexto
    context = " ".join([doc.page_content for doc in source_docs])
    
    # Calcular similarity de cada afirmación con el contexto
    unsupported_claims = []
    
    for sentence in response_sentences:
        sentence_emb = model.encode(sentence, convert_to_tensor=True)
        context_emb = model.encode(context, convert_to_tensor=True)
        
        similarity = util.cos_sim(sentence_emb, context_emb).item()
        
        if similarity < threshold:
            unsupported_claims.append({
                "claim": sentence,
                "similarity": similarity
            })
    
    return {
        "is_grounded": len(unsupported_claims) == 0,
        "unsupported_claims": unsupported_claims,
        "grounding_score": 1.0 - (len(unsupported_claims) / len(response_sentences))
    }
```

---

## 🎨 STORYTELLING BEST PRACTICES

### Del "Storytelling with Data" (Cole Nussbaumer Knaflic)

#### **1. The Power of Context**

##### **Three-Minute Story Framework**
Para presentar el proyecto (README, demo, pitch):

```markdown
## PeruGuide AI: The Three-Minute Story

**SETUP (30 sec):** The Big Picture
- Perú: 2.5M+ tourists/year, incredibly diverse
- Problem: Information scattered across 100+ sources
- Gap: No intelligent, verified, personalized assistant

**CONFLICT (60 sec):** The Challenge
- Tourist: 20+ hours researching, still uncertain
- Agency: 50+ repetitive queries daily, opportunity cost
- Developer: Complex RAG systems, production challenges

**RESOLUTION (90 sec):** The Solution
- PeruGuide AI: 30+ official sources → instant answers
- Architecture: Production-grade RAG with RAGAS evaluation
- Value: 95% time saved, 100% source citation, reproductible

[Visual: Before/After comparison]
[Demo: Live query → instant response with sources]
```

**Aplicación:**
- Presentación de 3 minutos para entrevistas
- Demo script estructurado
- README structure: Problem → Solution → Results

#### **2. Eliminate Clutter**

##### **Documentation Principle: Signal vs. Noise**
```markdown
❌ BAD README:
```markdown
# My RAG Project

This project uses LangChain and FAISS and ChromaDB and implements RAG 
with embeddings using sentence transformers and has a FastAPI backend 
and Streamlit frontend and uses Docker and has evaluation with RAGAS 
and supports Spanish and English and...

[walls of text]
[no structure]
[everything is equally important = nothing stands out]
```

✅ GOOD README:
```markdown
# 🇵🇪 PeruGuide AI

> Transform 5,000+ pages of Peru tourism data into instant, verified recommendations

[Clear visual: Architecture diagram]

## ⚡ Quick Start (< 2 min)
```bash
docker-compose up
open http://localhost:8501
```

## 🎯 What Makes This Special
✅ Production-grade RAG architecture
✅ RAGAS-evaluated (Faithfulness: 0.87)
✅ 30+ official data sources
✅ 100% response citation

[Show, don't just tell]
```

**Principles Applied:**
- **Remove to improve**: Solo lo esencial en primera vista
- **Strategic use of color**: Emojis/badges para jerarquía visual
- **Progressive disclosure**: Links a detalles profundos
- **Visual hierarchy**: Headers, bullets, code blocks

#### **3. Focus Attention**

##### **README Structure con Attention Management**
```markdown
# [HERO IMAGE] ← Immediate visual impact

## [30-second pitch] ← Hook attention

## [Live Demo Link] ← Call-to-action

---

## Why This Matters ← Context
[Problem statement con storytelling]

## The Solution ← Value prop
[3 key features con íconos]

## See It In Action ← Proof
[GIF/video demo]

## Quick Start ← Remove friction
[One-command deployment]

---

[Detalles técnicos en secciones colapsables o docs/ folder]
```

**Preattentive Attributes:**
- Size: Bigger = more important
- Color: Strategic use (green = success, red = warning, blue = info)
- Position: Top = most critical
- Enclosure: Boxes for grouping related items

#### **4. Think Like a Designer**

##### **Documentation Design System**
```markdown
Consistent Iconography:
🎯 = Goal/Objective
✅ = Completed/Verified
🚀 = Performance/Speed
📊 = Metrics/Evaluation
🏗️ = Architecture
💡 = Insight/Tip
⚠️ = Warning/Important
📚 = Documentation/Learning
🔧 = Configuration/Setup
🎨 = UI/UX

Code Block Conventions:
```python  # Python code
```bash    # Terminal commands
```yaml    # Configuration
```text    # Output/logs
```

Visual Hierarchy:
# H1: Project title only
## H2: Major sections
### H3: Subsections
#### H4: Details

Emphasis:
**Bold**: Key terms, important points
*Italic*: Subtle emphasis
`code`: Technical terms, commands
> Blockquote: Important callouts
```

##### **Notebook Design**
```python
# ❌ BAD: Wall of code without explanation
data = load_data()
chunks = split_text(data, 512, 64)
embeddings = get_embeddings(chunks)
db = create_db(embeddings)
retriever = db.as_retriever()
# ... 200 more lines

# ✅ GOOD: Story-driven with explanations
"""
## 📚 Step 1: Loading Our Knowledge Base

We have 30+ PDF guides about Peru tourism. Let's see what we're working with.
"""

data = load_data()
print(f"Loaded {len(data)} documents")
print(f"Total pages: {sum(len(doc.pages) for doc in data)}")

# Visualize distribution
plot_documents_by_department(data)

"""
### 💡 Insight
Notice how Cusco and Lima have the most documentation? This makes sense 
as they're the top tourist destinations.

## 🔪 Step 2: Chunking Strategy

We need to break documents into smaller pieces for effective retrieval.
But how small? Let's experiment...
"""

# Compare different chunk sizes
results = compare_chunk_sizes([256, 512, 1024])
plot_chunk_size_impact(results)

"""
### 📊 Results
512 tokens with 64 overlap gives us the best balance:
- Preserves context (overlap)
- Fits in context window
- Maintains semantic coherence

Let's use that configuration:
"""

chunks = split_text(data, chunk_size=512, overlap=64)
```

**Storytelling Elements:**
- Headers as chapter titles
- Explanatory markdown cells
- Visualizations to show, not tell
- Progressive revelation
- Insights and conclusions

#### **5. Tell a Story with Data**

##### **Evaluation Results Presentation**
```markdown
# 📊 Evaluation Results: The Journey to 0.87 Faithfulness

## The Baseline (Iteration 1)
We started with a simple RAG pipeline...

| Metric | Score | Status |
|--------|-------|--------|
| Faithfulness | 0.62 | 😞 Too many hallucinations |
| Answer Relevancy | 0.71 | 🤔 Decent but not great |
| Context Precision | 0.55 | 😱 Retrieving wrong docs |

**What went wrong:**
- Naive chunking lost context at boundaries
- No reranking → irrelevant docs in context
- Generic prompts → model adding ungrounded info

## Iteration 2: Improved Chunking
Added overlap and preserved section context...

[Bar chart: Before vs After]

| Metric | Before | After | Δ |
|--------|--------|-------|---|
| Context Precision | 0.55 | 0.72 | +31% ✅ |

## Iteration 3: Reranking
Added cross-encoder reranking...

[Line graph: Improvement trajectory]

| Metric | Before | After | Δ |
|--------|--------|-------|---|
| Context Precision | 0.72 | 0.84 | +17% ✅ |
| Answer Relevancy | 0.71 | 0.78 | +10% ✅ |

## Iteration 4: Prompt Engineering
Fine-tuned prompts with few-shot examples...

[Final comparison chart]

| Metric | Baseline | Final | Δ |
|--------|----------|-------|---|
| Faithfulness | 0.62 | 0.87 | +40% 🎉 |
| Answer Relevancy | 0.71 | 0.82 | +15% ✅ |
| Context Precision | 0.55 | 0.84 | +53% ⭐ |

## Key Learnings
1. **Context is king**: Better retrieval → better generation
2. **Iterative wins**: Each small improvement compounds
3. **Measure everything**: Can't improve what you don't measure

[Call-to-action: See the code in notebooks/04_evaluation.ipynb]
```

**Narrative Arc:**
1. **Setup**: Baseline results (conflict)
2. **Rising Action**: Iterative improvements
3. **Climax**: Final results
4. **Resolution**: Key learnings
5. **Call-to-action**: Next steps

---

## 🔍 EVALUATION BEST PRACTICES (From RAGAS & Research)

### **Test Dataset Design**

#### **Diverse Query Types**
```python
test_queries = {
    "factual": [
        "¿Cuál es la altura de Machu Picchu?",
        "¿En qué departamento está el lago Titicaca?",
        "¿Cuándo fue fundada la ciudad de Lima?"
    ],
    "recommendation": [
        "¿Qué lugares me recomiendas visitar en 7 días?",
        "¿Dónde puedo probar la mejor comida peruana?",
        "¿Qué actividades de aventura hay en Cusco?"
    ],
    "planning": [
        "¿Cómo organizar un viaje de 10 días incluyendo Machu Picchu?",
        "¿Qué ruta seguir para visitar la costa y la sierra?",
        "¿Cuál es el mejor itinerario para gastronomía peruana?"
    ],
    "comparative": [
        "¿Qué diferencia hay entre Cusco y Arequipa?",
        "¿Es mejor visitar Machu Picchu en junio o septiembre?",
        "¿Huacachina o Paracas para turismo de aventura?"
    ],
    "edge_cases": [
        "¿Hay opciones veganas en la comida peruana?",  # Limited info
        "¿Qué hacer en Perú con niños pequeños?",  # May not be covered
        "¿Cuál es el costo promedio diario de un viaje a Perú?"  # May not have specific numbers
    ]
}
```

#### **Ground Truth Creation**
```python
# Para cada query, crear ground truth manualmente:
ground_truth = {
    "query": "¿Cuál es la altura de Machu Picchu?",
    "expected_answer": "Machu Picchu está ubicado a 2,430 metros sobre el nivel del mar.",
    "expected_sources": ["Guía_Cusco.pdf", "page 34"],
    "category": "factual",
    "difficulty": "easy"
}
```

### **RAGAS Metrics in Practice**

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)

# Preparar dataset
data = {
    "question": [...],
    "answer": [...],  # Generated by RAG
    "contexts": [...],  # Retrieved contexts
    "ground_truths": [...]  # Expected answers
}

# Evaluar
results = evaluate(
    dataset=data,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall
    ]
)

print(results)
```

**Interpretation:**
- **Faithfulness > 0.85**: Respuestas grounded en contexto
- **Answer Relevancy > 0.80**: Responde lo que se preguntó
- **Context Precision > 0.75**: Contexto recuperado es relevante
- **Context Recall > 0.70**: Se recuperó toda la info necesaria

---

## 🚀 DEPLOYMENT BEST PRACTICES

### **Docker Multi-Stage Build**
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /root/.local /root/.local
COPY src/ ./src/
COPY data/vector_stores/ ./data/vector_stores/

# Make sure scripts are in PATH
ENV PATH=/root/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run app
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Benefits:**
- Smaller final image (no build tools)
- Faster deployment
- Better security (minimal attack surface)

### **Docker Compose for Full Stack**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - VECTOR_STORE_PATH=/data/vector_stores
    volumes:
      - ./data/vector_stores:/data/vector_stores:ro
    depends_on:
      - redis
    deploy:
      resources:
        limits:
          memory: 4G
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  streamlit:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api

volumes:
  redis_data:
```

---

## 📚 CONCLUSIÓN

Este documento sintetiza las mejores prácticas extraídas de **9 libros y papers** de referencia, aplicadas específicamente al proyecto **PeruGuide AI**.

**Key Takeaways:**
1. ✅ **Engineering**: RAG no es solo "embeddings + LLM", requiere pipeline robusto
2. ✅ **Evaluation**: Métricas objetivas son fundamentales para iteración
3. ✅ **Storytelling**: La narrativa convierte un proyecto técnico en memorable
4. ✅ **Production**: Gap teoría-producción se cierra con arquitectura adecuada
5. ✅ **Documentation**: Docs son tan importantes como el código

**¿Siguiente paso?**
Implementar estas prácticas en el proyecto real, iterando y evaluando continuamente. 🚀

---

*Última actualización: 23 Octubre 2025*
