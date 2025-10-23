# 📚 PeruGuide AI - Navigation Index# 📚 ÍNDICE MAESTRO

## PeruGuide AI - Documentación del Proyecto

## 🚀 Quick Start

**Fecha de análisis:** 23 de Octubre de 2025  

**New to the project?** → Start here: [`START_HERE.md`](START_HERE.md)**Estado:** ✅ Diseño completo + Ready para implementación



------



## 📖 Documentation Map## 🎯 ORDEN DE LECTURA RECOMENDADO



### **Essential Reading (In Order)**### **1️⃣ START HERE - DECISIÓN** (5 min) ⭐

📄 **RESUMEN_DECISIONES_CLAVE.md**

1. **[START_HERE.md](START_HERE.md)** ⭐ **READ FIRST**- Resumen ejecutivo de 1 página

   - Project status, setup commands, first steps- Las 3 preguntas críticas para validar

   - Complete checklist of what's done- Checklist de preparación

   - Next actions clearly defined- **LEE ESTO PRIMERO - Te ayuda a decidir si proceder**



2. **[README.md](README.md)** 📘 **Main Documentation**### **2️⃣ CASO DE USO COMPLETO** (20 min)

   - Project overview & architecture📄 **PROYECTO_PORTAFOLIO_FINAL.md**

   - Complete tech stack- Problema real y solución propuesta

   - Installation guide- User personas con journeys detallados

   - API documentation- Arquitectura técnica completa

- Stack tecnológico con justificaciones

3. **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** 📊 **Executive Overview**- Plan de implementación 5 semanas

   - High-level project vision- Diferenciadores y habilidades demostradas

   - Academic foundation (2,959 pages analyzed)- **Léelo para entender TODO el proyecto**

   - ROI & portfolio value

   - Metrics & goals### **3️⃣ ARQUITECTURA VISUAL** (10 min)

📄 **VISUAL_ROADMAP.md**

4. **[DEVELOPMENT_ROLES.md](DEVELOPMENT_ROLES.md)** 👥 **Your Roles**- Diagramas de arquitectura

   - 7 professional roles defined- Timeline visual semana por semana

   - Responsibilities & deliverables- Flujos de trabajo

   - Code examples & standards- **Vista rápida del panorama completo**

   - Definition of Done

### **4️⃣ SETUP Y ARRANQUE** (2-3 horas HACER)

5. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** 🗂️ **Structure Visualization**📄 **GUIA_SETUP_INICIAL.md**

   - Directory tree with descriptions- Guía paso a paso para Día 0

   - Data flow diagrams- Scripts y comandos listos para ejecutar

   - Role ownership map- Troubleshooting de problemas comunes

   - Quick start commands- Checklist de verificación

- **USA ESTO para inicializar el proyecto HOY**

---

### **5️⃣ EJECUCIÓN DIARIA** (20 min lectura, luego referencia diaria)

## 📂 Key Directories📄 **ACTION_PLAN.md**

- Plan día por día (35 días)

### **Core Code**- Scripts de automatización

- [`src/`](src/) - Main source code (7 modules)- Workflow templates

  - [`data_pipeline/`](src/data_pipeline/) - Data engineering- Risk mitigation

  - [`embedding_pipeline/`](src/embedding_pipeline/) - Embeddings- **Guía operativa durante implementación**

  - [`vector_store/`](src/vector_store/) - Vector DB

  - [`retrieval_pipeline/`](src/retrieval_pipeline/) - Retrieval### **6️⃣ REFERENCIA TÉCNICA** (45 min, consulta continua)

  - [`inference_pipeline/`](src/inference_pipeline/) - RAG chain📄 **TECHNICAL_BEST_PRACTICES.md**

  - [`evaluation/`](src/evaluation/) - RAGAS metrics- Code snippets listos para usar

  - [`utils/`](src/utils/) - Utilities- Patrones de implementación

- Decisiones de diseño explicadas

### **Application**- Trade-offs de tecnologías

- [`api/`](api/) - FastAPI REST API- **Consulta mientras codificas**

- [`app/`](app/) - Streamlit UI

- [`tests/`](tests/) - Test suite### **7️⃣ MATERIALES DE REFERENCIA** (Opcional)

📄 **PROJECT_PROPOSAL_ENHANCED.md**

### **Infrastructure**- Análisis de 1,100+ páginas de libros

- [`.github/workflows/`](.github/workflows/) - CI/CD pipelines- Best practices extraídas

- [`docker/`](docker/) - Containerization- Estado del arte en RAG

- [`docs/`](docs/) - MkDocs documentation- **Background y fundamentos**



### **Research & Data**📄 **EXECUTIVE_SUMMARY.md**

- [`analisis/`](analisis/) - Research archive (2,959 pages analyzed)- Resumen de análisis previo

- [`Books/`](Books/) - Reference materials- Métricas y roadmap

- [`Complementarios Peru/`](Complementarios%20Peru/) - Official Peru PDFs- **Vista rápida del análisis**

- [`data/`](data/) - Data directory (raw, processed, vector_stores)

- [`notebooks/`](notebooks/) - Jupyter notebooks (legacy + experiments)---



---## 📂 ESTRUCTURA DE DOCUMENTOS ACTUALIZADA



## 🎯 By Role```

peruguide-rag/

### **Data Engineer** 🗄️│

- **Start:** [DEVELOPMENT_ROLES.md - Role 1](DEVELOPMENT_ROLES.md#role-1-data-engineer)├── 🎯 QUICK START (Para empezar HOY)

- **Work in:** [`src/data_pipeline/`](src/data_pipeline/)│   ├── RESUMEN_DECISIONES_CLAVE.md          ← Validación y decisión (5 min)

- **Tests:** [`tests/unit/test_*`](tests/unit/)│   ├── GUIA_SETUP_INICIAL.md                ← Setup paso a paso (2-3 horas)

- **First task:** Implement `pdf_loader.py`│   └── INDEX.md (este archivo)               ← Navegación

│

### **ML Engineer** 🤖├── 📋 STRATEGIC PLANNING

- **Start:** [DEVELOPMENT_ROLES.md - Role 2](DEVELOPMENT_ROLES.md#role-2-ml-engineer)│   ├── PROYECTO_PORTAFOLIO_FINAL.md         ← Caso de uso completo (20 min)

- **Work in:** │   ├── VISUAL_ROADMAP.md                     ← Arquitectura visual (10 min)

  - [`src/embedding_pipeline/`](src/embedding_pipeline/)│   └── EXECUTIVE_SUMMARY.md                  ← Resumen análisis previo

  - [`src/retrieval_pipeline/`](src/retrieval_pipeline/)│

  - [`src/inference_pipeline/`](src/inference_pipeline/)├── �️ IMPLEMENTATION

  - [`src/evaluation/`](src/evaluation/)│   ├── ACTION_PLAN.md                        ← Plan día a día (35 días)

- **Tests:** [`tests/unit/`, `tests/integration/`](tests/)│   ├── TECHNICAL_BEST_PRACTICES.md           ← Guía técnica y snippets

- **First task:** Implement embedding model│   └── PROJECT_PROPOSAL_ENHANCED.md          ← Análisis de materiales

│

### **Backend Engineer** ⚙️├── 📊 ANALYSIS & RESEARCH

- **Start:** [DEVELOPMENT_ROLES.md - Role 3](DEVELOPMENT_ROLES.md#role-3-backend-engineer)│   └── 00_analyze_reference_materials.ipynb  ← Análisis de libros

- **Work in:** [`api/`](api/)│

- **Tests:** [`tests/integration/test_api.py`](tests/integration/)├── 📚 REFERENCE MATERIALS

- **First task:** Setup FastAPI app structure│   ├── Books/

│   │   ├── llm/                              ← 4 libros LLM engineering

### **Frontend Engineer** 🎨│   │   └── story-telling/                    ← 3 libros storytelling

- **Start:** [DEVELOPMENT_ROLES.md - Role 4](DEVELOPMENT_ROLES.md#role-4-frontend-engineer)│   ├── Complementarios Peru/                 ← 30+ PDFs turismo (DATOS)

- **Work in:** [`app/`](app/)│   └── [Notebooks legacy]                    ← Para referencia

- **First task:** Create basic Streamlit interface│

└── � NEXT PROJECT (crear después del setup)

### **DevOps Engineer** 🔧    └── peruguide-ai/                         ← Repositorio nuevo

- **Start:** [DEVELOPMENT_ROLES.md - Role 5](DEVELOPMENT_ROLES.md#role-5-devops-engineer)        ├── src/

- **Work in:** [`.github/workflows/`](.github/workflows/), [`docker/`](docker/)        ├── api/

- **First task:** Setup CI pipeline        ├── app/

        ├── notebooks/

### **QA Engineer** ✅        ├── tests/

- **Start:** [DEVELOPMENT_ROLES.md - Role 6](DEVELOPMENT_ROLES.md#role-6-qa-engineer)        ├── data/

- **Work in:** [`tests/`](tests/)        ├── docs/

- **First task:** Create test fixtures in `conftest.py`        └── [estructura completa]

```

### **Technical Writer** 📝

- **Start:** [DEVELOPMENT_ROLES.md - Role 7](DEVELOPMENT_ROLES.md#role-7-technical-writer)---

- **Work in:** [`docs/`](docs/)

- **First task:** Expand getting started guide## 🎨 GUÍA POR CASO DE USO



---### **"¿Debo empezar este proyecto?"**

```

## 📅 By Timeline1. RESUMEN_DECISIONES_CLAVE.md (5 min)

   → Responde las 3 preguntas de validación

### **Week 1: Foundation**   → Revisa checklist de preparación

- [x] Project structure setup```

- [x] Documentation created

- [ ] Data pipeline implementation → [See Week 1 Plan](START_HERE.md#semana-1-foundation-próxima)### **"Quiero entender el proyecto completo"**

- [ ] Embedding pipeline```

- [ ] API skeleton1. RESUMEN_DECISIONES_CLAVE.md (5 min)

2. PROYECTO_PORTAFOLIO_FINAL.md (20 min)

### **Week 2: Integration**3. VISUAL_ROADMAP.md (10 min)

- [ ] RAG chainTotal: 35 minutos → Visión completa

- [ ] API endpoints```

- [ ] Basic UI

### **"Listo para empezar HOY"**

### **Week 3: Testing**```

- [ ] Test suite1. RESUMEN_DECISIONES_CLAVE.md (5 min) - validar

- [ ] RAGAS evaluation2. GUIA_SETUP_INICIAL.md (2-3 horas) - ejecutar

- [ ] CI/CD setup3. Verificación final ✓

4. Mañana → ACTION_PLAN.md Semana 1

### **Week 4: Deployment**```

- [ ] Docker deployment

- [ ] Documentation complete### **"Necesito detalles técnicos"**

- [ ] Final testing & launch```

1. TECHNICAL_BEST_PRACTICES.md (45 min)

---2. PROJECT_PROPOSAL_ENHANCED.md (análisis)

3. Libros en Books/ (profundización)

## 🔍 By Topic```



### **Architecture & Design**### **"¿Cómo lo ejecuto día a día?"**

- [README.md - Architecture](README.md#-architecture)```

- [PROJECT_STRUCTURE.md - Data Flow](PROJECT_STRUCTURE.md#-data-flow-diagram)1. ACTION_PLAN.md (20 min lectura inicial)

- [`analisis/PLANTEAMIENTO_DEFINITIVO_CON_ANALISIS.md`](analisis/PLANTEAMIENTO_DEFINITIVO_CON_ANALISIS.md)2. Cada día: seguir checklist de la semana actual

3. Consultar TECHNICAL_BEST_PRACTICES según necesidad

### **Tech Stack**```

- [README.md - Tech Stack](README.md#-tech-stack)

- [EXECUTIVE_SUMMARY.md - Tech Stack Justificado](EXECUTIVE_SUMMARY.md#-tech-stack-justificado)### **"Quiero empezar a implementar HOY"**

```

### **Setup & Installation**1. VISUAL_ROADMAP.md → "Next Actions" (5 min)

- [START_HERE.md - Setup Ambiente](START_HERE.md#setup-ambiente-primera-vez)2. ACTION_PLAN.md → "First Actions" (5 min)

- [docs/index.md - Getting Started](docs/index.md)3. TECHNICAL_BEST_PRACTICES.md → Bookmarked (referencia)

- [README.md - Getting Started](README.md#-getting-started)Total: 10 min + start coding

```

### **Testing**

- [DEVELOPMENT_ROLES.md - Testing Requirements](DEVELOPMENT_ROLES.md#testing-requirements)### **"Necesito referencia técnica específica"**

- [`pytest.ini`](pytest.ini)```

- [`tests/`](tests/)1. Busca keyword en TECHNICAL_BEST_PRACTICES.md

   - Chunking → sección "Chunking Strategy"

### **Research & Analysis**   - Embeddings → sección "Embedding Selection"

- [`analisis/PLANTEAMIENTO_DEFINITIVO_CON_ANALISIS.md`](analisis/PLANTEAMIENTO_DEFINITIVO_CON_ANALISIS.md) - 2,959 pages analyzed   - Prompts → sección "Prompt Engineering"

- [`analisis/materials_analysis_comprehensive.json`](analisis/materials_analysis_comprehensive.json) - Extracted insights   - Evaluation → sección "RAGAS Metrics"

2. Si necesitas más profundidad → Books/ folder

### **Evaluation & Metrics**```

- [README.md - Evaluation & Metrics](README.md#-evaluation--metrics)

- [EXECUTIVE_SUMMARY.md - Métricas de Éxito](EXECUTIVE_SUMMARY.md#-métricas-de-éxito)### **"Quiero presentar el proyecto a alguien"**

```

---1. EXECUTIVE_SUMMARY.md → "Visión en 30 segundos"

2. VISUAL_ROADMAP.md → Muestra la arquitectura visual

## ⚙️ Configuration Files3. PROJECT_PROPOSAL_ENHANCED.md → User journeys

Total: Demo de 5 minutos

| File | Purpose | Status |```

|------|---------|--------|

| [`.env.example`](.env.example) | Environment variables template | ✅ |### **"Necesito motivación / recordar por qué esto importa"**

| [`pyproject.toml`](pyproject.toml) | Project metadata & config | ✅ |```

| [`requirements.txt`](requirements.txt) | Python dependencies | ✅ |1. PROJECT_PROPOSAL_ENHANCED.md → "The Problem" y "The Solution"

| [`requirements-dev.txt`](requirements-dev.txt) | Dev dependencies | ✅ |2. VISUAL_ROADMAP.md → "End Goal"

| [`.gitignore`](.gitignore) | Git ignore patterns | ✅ |3. ACTION_PLAN.md → "Mantras for Success"

| [`pytest.ini`](pytest.ini) | pytest configuration | ✅ |```

| [`.pre-commit-config.yaml`](.pre-commit-config.yaml) | Pre-commit hooks | ✅ |

| [`mkdocs.yml`](mkdocs.yml) | Documentation config | ✅ |---

| [`LICENSE`](LICENSE) | MIT License | ✅ |

## 🔍 ÍNDICE CONCEPTUAL

---

### **Arquitectura & Diseño**

## 🔗 External Resources- **Overview**: VISUAL_ROADMAP.md → Arquitectura section

- **Detallado**: PROJECT_PROPOSAL_ENHANCED.md → "Arquitectura Mejorada"

### **Libraries Documentation**- **Implementación**: TECHNICAL_BEST_PRACTICES.md → Todos los sections

- [LangChain](https://python.langchain.com/docs/)

- [FastAPI](https://fastapi.tiangolo.com/)### **RAG Pipeline**

- [Streamlit](https://docs.streamlit.io/)- **Visión**: PROJECT_PROPOSAL_ENHANCED.md → "RAG Pipeline Avanzado"

- [RAGAS](https://docs.ragas.io/)- **Best Practices**: TECHNICAL_BEST_PRACTICES.md → "RAG Pipeline Design Principles"

- [Sentence Transformers](https://www.sbert.net/)- **Código**: TECHNICAL_BEST_PRACTICES.md → Code snippets

- [FAISS](https://github.com/facebookresearch/faiss)

- [ChromaDB](https://www.trychroma.com/)### **Chunking**

- **Estrategia**: TECHNICAL_BEST_PRACTICES.md → "Chunking Strategy"

### **Reference Books** (In [`Books/`](Books/))- **Implementación**: ACTION_PLAN.md → Semana 1, Día 5

- LLM Engineer's Handbook- **Experimentos**: 00_analyze_reference_materials.ipynb

- Build a Large Language Model from Scratch

- Hands-On Large Language Models### **Embeddings**

- Storytelling with Data- **Selección**: TECHNICAL_BEST_PRACTICES.md → "Embedding Selection"

- + 5 more (see [`Books/`](Books/) directory)- **Comparación**: PROJECT_PROPOSAL_ENHANCED.md → Stack tecnológico

- **Implementación**: ACTION_PLAN.md → Semana 1, Día 6-7

---

### **Vector Store**

## 🆘 Troubleshooting- **Comparación FAISS vs Chroma**: TECHNICAL_BEST_PRACTICES.md → Trade-offs table

- **Setup**: ACTION_PLAN.md → Semana 1, Día 6-7

### **Setup Issues**- **Código**: TECHNICAL_BEST_PRACTICES.md → "Vector Store Configuration"

- See [docs/index.md - Troubleshooting](docs/index.md#troubleshooting)

- Check [START_HERE.md - FAQ](START_HERE.md#-faq)### **Retrieval**

- **Estrategias**: TECHNICAL_BEST_PRACTICES.md → "Retrieval Strategy"

### **Development Issues**- **Hybrid Search**: TECHNICAL_BEST_PRACTICES.md → "Hybrid Search"

- Review [DEVELOPMENT_ROLES.md](DEVELOPMENT_ROLES.md) for your role- **Reranking**: TECHNICAL_BEST_PRACTICES.md → Multi-stage retrieval

- Check module-specific `__init__.py` documentation

- Consult research in [`analisis/`](analisis/)### **Prompt Engineering**

- **Templates**: TECHNICAL_BEST_PRACTICES.md → "Prompt Engineering for RAG"

### **Testing Issues**- **Few-shot**: TECHNICAL_BEST_PRACTICES.md → Few-Shot Examples

- See [`pytest.ini`](pytest.ini) configuration- **Dynamic**: TECHNICAL_BEST_PRACTICES.md → Dynamic Prompting

- Check [`tests/conftest.py`](tests/conftest.py) for fixtures

- Review [DEVELOPMENT_ROLES.md - QA Engineer](DEVELOPMENT_ROLES.md#role-6-qa-engineer)### **Evaluation**

- **Framework**: TECHNICAL_BEST_PRACTICES.md → "Evaluation Best Practices"

---- **RAGAS**: TECHNICAL_BEST_PRACTICES.md → "RAGAS Metrics in Practice"

- **Test Dataset**: TECHNICAL_BEST_PRACTICES.md → "Test Dataset Design"

## 📊 Project Status- **Roadmap**: ACTION_PLAN.md → Semana 2, Día 10-11



**Phase:** ✅ Setup Complete → Ready for Implementation  ### **Storytelling**

**Next Milestone:** Week 1 - Feature Pipeline Complete  - **Principles**: PROJECT_PROPOSAL_ENHANCED.md → "Caso de Uso con Storytelling"

**Timeline:** 4 weeks total  - **Framework**: TECHNICAL_BEST_PRACTICES.md → "Storytelling Best Practices"

**Target:** Production-Ready RAG System (Nivel 2)- **Application**: PROJECT_PROPOSAL_ENHANCED.md → User journeys

- **Documentation**: TECHNICAL_BEST_PRACTICES.md → "Documentation Design"

---

### **API Development**

## 🎯 Quick Actions- **FastAPI**: ACTION_PLAN.md → Semana 3, Día 15-16

- **Endpoints**: TECHNICAL_BEST_PRACTICES.md (no explícito, pero hay patterns)

```bash- **Testing**: ACTION_PLAN.md → Semana 3, Día 19-21

# Setup (first time)

python -m venv venv### **Deployment**

.\venv\Scripts\activate- **Docker**: TECHNICAL_BEST_PRACTICES.md → "Docker Multi-Stage Build"

pip install -r requirements.txt- **Compose**: TECHNICAL_BEST_PRACTICES.md → "Docker Compose for Full Stack"

pip install -r requirements-dev.txt- **Cloud**: ACTION_PLAN.md → Semana 4, Día 24-25



# Daily workflow### **Observability**

pytest tests/ -v --cov=src- **Logging**: TECHNICAL_BEST_PRACTICES.md → Response Post-Processing

ruff check src/ api/ app/- **Metrics**: ACTION_PLAN.md → Semana 4, Día 26-28

black src/ api/ app/- **Tracing**: PROJECT_PROPOSAL_ENHANCED.md → Arquitectura



# Run application (when ready)### **Documentation**

uvicorn api.main:app --reload- **README**: TECHNICAL_BEST_PRACTICES.md → "Documentation Principle"

streamlit run app/Home.py- **Notebooks**: ACTION_PLAN.md → Semana 5, Día 29-30

- **Style Guide**: TECHNICAL_BEST_PRACTICES.md → "Documentation Design System"

# Documentation

mkdocs serve---

```

## 📊 MÉTRICAS Y OBJETIVOS

---

### **Dónde encontrar:**

## 📞 Help & Support- **Objetivos completos**: PROJECT_PROPOSAL_ENHANCED.md → "Success Criteria"

- **Métricas técnicas**: EXECUTIVE_SUMMARY.md → Tabla de métricas

- **Documentation Issues:** Check this INDEX.md for navigation- **Tracking diario**: ACTION_PLAN.md → Success criteria section

- **Implementation Questions:** See [DEVELOPMENT_ROLES.md](DEVELOPMENT_ROLES.md)- **Evaluation**: TECHNICAL_BEST_PRACTICES.md → Evaluation section

- **Architecture Questions:** See [README.md](README.md) or [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

- **Research Questions:** See [`analisis/`](analisis/) directory### **Quick Reference:**

```

---Technical Excellence:

- Faithfulness: > 0.85

<div align="center">- Answer Relevancy: > 0.80

- Latency p95: < 3s

**📚 Use this index to navigate the project effectively**- Code Coverage: > 80%



[🚀 Start Here](START_HERE.md) | [📘 README](README.md) | [👥 Roles](DEVELOPMENT_ROLES.md) | [🗂️ Structure](PROJECT_STRUCTURE.md)User Value:

- Coverage: > 85%

</div>- Citation: 100%

- Languages: 2+ (ES, EN)

Portfolio Impact:
- GitHub stars: > 50
- LinkedIn views: > 500
- External forks: ≥ 1
```

---

## 🗓️ TIMELINE REFERENCE

### **Roadmap Completo**
📄 PROJECT_PROPOSAL_ENHANCED.md → "Roadmap de Implementación Actualizado"

### **Checklist Diario**
📄 ACTION_PLAN.md → Todo el documento es un checklist

### **Visual Timeline**
📄 VISUAL_ROADMAP.md → Timeline section con ASCII art

### **Quick View:**
```
Week 1: Foundation (Setup, Data, Vector Store)
Week 2: Core RAG (Pipeline, Evaluation, Optimization)
Week 3: API & Production (FastAPI, Features, Tests)
Week 4: UI & Deployment (Streamlit, Docker, Deploy)
Week 5: Documentation & Showcase (Notebooks, Docs, Marketing)
```

---

## 🛠️ CÓDIGO Y SNIPPETS

### **Dónde encontrar código:**
📄 **TECHNICAL_BEST_PRACTICES.md** tiene TODO el código necesario:
- Data ingestion: PDFLoader, ChunkingStrategy
- Embeddings: EmbeddingManager
- Vector Store: VectorStoreManager, FAISS/Chroma setup
- Retrieval: Retriever, Reranker, Hybrid search
- Prompts: System prompts, Few-shot examples, Dynamic prompting
- Evaluation: RAGAS integration, Test dataset
- Post-processing: Source citation, Confidence scoring, Hallucination detection
- Deployment: Dockerfile, Docker Compose

### **Orden de uso:**
1. Week 1 → Data ingestion code
2. Week 1 → Vector store code
3. Week 2 → RAG chain code
4. Week 2 → Evaluation code
5. Week 3 → API code (patterns en best practices)
6. Week 4 → Deployment code

---

## 📚 REFERENCE MATERIALS

### **Libros Analizados (Books/ folder)**

#### **LLM Engineering:**
1. `llm-engineers-handbook-engineering-production.pdf` (523 páginas)
   - Production-ready RAG systems
   - MLOps & LLMOps principles
   - Inference optimization

2. `Designing Large Language Model Applications (2023).pdf`
   - Application design patterns
   - System integration
   - Error handling

3. `Hands-On Large Language Models.pdf`
   - Practical examples
   - Embeddings & generation
   - Visualizations

4. `Build a Large Language Model (From Scratch).pdf`
   - Fundamentals
   - Implementation details
   - Best practices

#### **Storytelling:**
1. `storytelling-with-data-cole-nussbaumer-knaflic.pdf`
   - Context, visual display, clutter elimination
   - Focus attention, think like designer
   - Tell a story

2. `Brent Dykes Effective Data Storytelling.pdf`
   - Data + Narrative + Visuals framework
   - Driving change with data
   - Engagement strategies

3. `_OceanofPDF.com_User_Story_Mapping.pdf`
   - User journey mapping
   - Story slicing
   - Personas

#### **NLP & Technical:**
- `PracticalNaturalLanguageProcessing.pdf`
- `Large Language Models Meet NLP A Survey.pdf`
- BERT paper, SuperGLUE paper
- Semana 1-8 MNA materials (teoría)

### **Datos del Proyecto:**
- `Complementarios Peru/` → 30+ PDFs oficiales (PromPerú, MINCETUR)
- Por departamento: Lima, Cusco, Arequipa, etc.
- Gastronomía, destinos, información general

### **Notebooks de Análisis:**
- `00_analyze_reference_materials.ipynb` → Extracción de insights
- Legacy notebooks → Referencia de ejercicios anteriores

---

## 🎯 DECISIONES CLAVE DOCUMENTADAS

### **Technology Stack**
📍 Ubicación: PROJECT_PROPOSAL_ENHANCED.md → "Stack Tecnológico Definitivo"

**Core:**
- LangChain (orchestration)
- sentence-transformers (embeddings)
- FAISS/Chroma (vector store)
- Mistral-7B or API (LLM)

**Production:**
- FastAPI (API)
- Streamlit (UI)
- Docker (deployment)
- RAGAS (evaluation)

### **Architecture Decisions**
📍 Ubicación: PROJECT_PROPOSAL_ENHANCED.md → "Arquitectura Mejorada"

**Layered approach:**
1. Presentation Layer (UI, API, CLI)
2. Application Layer (RAG pipeline)
3. Data Layer (Vector store, document store)
4. Observability Layer (Logging, metrics, tracing)

### **Evaluation Strategy**
📍 Ubicación: PROJECT_PROPOSAL_ENHANCED.md → "Evaluation Strategy"

**Metrics:**
1. Retrieval Quality (Precision@K, Recall@K)
2. Generation Quality (RAGAS: Faithfulness, Relevancy)
3. System Performance (Latency, Throughput)
4. User Satisfaction (NPS, Task success)

---

## 🚀 QUICK START GUIDE

### **Para empezar HOY mismo:**

1. **Lee esto** (15 min):
   - VISUAL_ROADMAP.md → Completo
   - ACTION_PLAN.md → "First Actions" section

2. **Ejecuta esto** (15 min):
   ```bash
   gh repo create peruguide-ai --public
   git clone https://github.com/[tu-user]/peruguide-ai.git
   cd peruguide-ai
   # Seguir checklist de ACTION_PLAN.md Día 1-2
   ```

3. **Bookmarks esto** (referencia continua):
   - TECHNICAL_BEST_PRACTICES.md (abierto en tab)
   - ACTION_PLAN.md (checklist diario)
   - PROJECT_PROPOSAL_ENHANCED.md (contexto)

---

## 💡 TIPS DE NAVEGACIÓN

### **Buscar información específica:**
1. Usa Ctrl+F en los documentos markdown
2. Keywords útiles:
   - "chunking" → chunking strategy
   - "embedding" → embedding selection
   - "RAG" → RAG pipeline
   - "RAGAS" → evaluation
   - "prompt" → prompt engineering
   - "docker" → deployment
   - "storytelling" → narrative techniques

### **Cuando estés bloqueado:**
1. Check ACTION_PLAN.md → "Support & Resources"
2. Re-read relevant section en TECHNICAL_BEST_PRACTICES.md
3. Consulta Books/ folder para deep dive
4. Search GitHub issues, StackOverflow

### **Para mantener motivación:**
1. Re-read PROJECT_PROPOSAL_ENHANCED.md → User journeys
2. Review VISUAL_ROADMAP.md → End Goal
3. Check ACTION_PLAN.md → Mantras for Success
4. Celebrate small wins! 🎉

---

## 📝 CHANGELOG DE DOCUMENTOS

### **23 Octubre 2025 - Creación inicial**
- ✅ Análisis exhaustivo de 9+ libros y papers
- ✅ Extracción de insights clave (00_analyze_reference_materials.ipynb)
- ✅ Propuesta mejorada con storytelling (PROJECT_PROPOSAL_ENHANCED.md)
- ✅ Best practices técnicas (TECHNICAL_BEST_PRACTICES.md)
- ✅ Plan de acción ejecutable (ACTION_PLAN.md)
- ✅ Resumen ejecutivo (EXECUTIVE_SUMMARY.md)
- ✅ Hoja de ruta visual (VISUAL_ROADMAP.md)
- ✅ Índice maestro (INDEX.md - este documento)

---

## 🎬 READY TO START?

Has completado:
- ✅ Análisis de materiales
- ✅ Diseño de arquitectura
- ✅ Planificación completa
- ✅ Documentación exhaustiva

Siguiente paso:
- 🎯 **Leer VISUAL_ROADMAP.md**
- 🎯 **Ejecutar First Actions**
- 🎯 **Comenzar Week 1, Day 1**

---

## 📞 DOCUMENT FEEDBACK

Si falta algo en este índice o en cualquier documento:
1. Anótalo en un TODO.md
2. Prioriza según impacto
3. Agrega en próxima iteración

Pero recuerda: **Ship > Perfect**. Tienes todo lo necesario para empezar. 🚀

---

*Índice creado: 23 Octubre 2025*
*Última actualización: 23 Octubre 2025*
*Estado: Complete and ready for execution ✅*

**¡VAMOS A CONSTRUIR ALGO EXTRAORDINARIO! 💪**
