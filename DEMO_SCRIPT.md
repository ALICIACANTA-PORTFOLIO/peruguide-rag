# 🎬 PERUGUIDE AI - END-TO-END DEMO SCRIPT

**Demo Duration:** 10-15 minutes  
**Audience:** Technical recruiters, hiring managers, senior engineers  
**Goal:** Showcase production-ready RAG system with best practices

---

## 🎯 Demo Overview

This script demonstrates the complete PeruGuide AI system from data ingestion to user-facing web interface, highlighting:
- Production-grade architecture
- Comprehensive testing
- Multi-cloud deployment
- Clean code practices
- Enterprise-ready features

---

## 📋 Pre-Demo Checklist

### Environment Setup
```bash
# 1. Terminal 1: API Server
conda activate peruguide-rag
cd d:\code\portfolio\peruguide-rag

# 2. Terminal 2: Frontend
conda activate peruguide-rag
cd d:\code\portfolio\peruguide-rag

# 3. Browser Tabs
# - http://localhost:8000/docs (API Documentation)
# - http://localhost:8501 (Streamlit Frontend)
# - GitHub repository page

# 4. VSCode
# - Open project root
# - Collapse all folders except key files
```

### Files to Have Ready
- `README_NEW.md` (overview)
- `src/api/main.py` (API entry)
- `app/streamlit_app.py` (frontend)
- `tests/integration/test_simple_rag.py` (integration tests)
- `FINAL_SUMMARY.md` (metrics)

---

## 🎬 DEMO SCRIPT

---

### **ACT 1: Problem & Solution** (2 minutes)

#### **SHOW: README_NEW.md - Problem Statement**

**Script:**
> "Hi, I'm [Your Name], and I'd like to show you PeruGuide AI - a production-ready RAG system I built to solve a real problem.
>
> Peru receives 4 million tourists annually, but planning a trip requires 5-8 hours of research across government PDFs. My system reduces that to 15 minutes using AI-powered question answering.
>
> This isn't a toy project - it's a full production system with 505 tests, 94% coverage, multi-cloud deployment, and enterprise features."

#### **SHOW: Architecture Diagram**

**Point out:**
- 9 major components
- Data pipeline → Vector store → Retrieval → LLM → RAG
- REST API + Web frontend
- Multiple deployment options

---

### **ACT 2: Code Quality & Testing** (3 minutes)

#### **SHOW: Test Suite Execution**

**Terminal 1:**
```bash
pytest tests/integration/test_simple_rag.py -v
```

**Script:**
> "Let's start with testing. This is an integration test that validates the entire RAG pipeline end-to-end."

**Point out:**
- 2 tests: end-to-end workflow + multiple queries
- Fast execution (~1.09s)
- Mock architecture for deterministic testing

#### **SHOW: Coverage Report**

**Terminal 1:**
```bash
pytest --cov=src --cov-report=term-missing
```

**Script:**
> "The full test suite has 505 tests with 94% coverage. Here you can see coverage for each component - data pipeline, embeddings, vector store, retrieval, LLMs, and RAG generator."

#### **SHOW: Code Structure**

**VSCode:**
Open `src/api/dependencies/__init__.py`

**Script:**
> "The codebase follows clean architecture principles. This is the dependency injection module - it uses singleton pattern to manage shared resources like the vector store and LLM clients.
>
> Notice the type hints, docstrings, and error handling - all production-grade practices."

---

### **ACT 3: API Backend** (3 minutes)

#### **SHOW: Start API Server**

**Terminal 1:**
```bash
uvicorn src.api.main:app --reload
```

**Script:**
> "Let's start the FastAPI backend. It uses async/await for non-blocking I/O and includes health monitoring."

#### **SHOW: OpenAPI Documentation**

**Browser:**
Open http://localhost:8000/docs

**Script:**
> "FastAPI auto-generates OpenAPI documentation. We have 4 endpoints:
> - POST /query - the main RAG endpoint
> - GET /health - health checks with component status
> - GET /models - list available LLM providers
> - GET / - root endpoint"

**Point out:**
- Pydantic schema validation
- Request/response examples
- Built-in try-it-out feature

#### **SHOW: Health Check**

**Browser:**
Click "Try it out" on `/api/v1/health`

**Script:**
> "The health endpoint checks all components - embedder, vector store, retriever, LLM, and RAG generator. This is critical for production monitoring."

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-24T...",
  "components": {
    "embedder": "healthy",
    "vector_store": "healthy",
    "retriever": "healthy",
    "llm": "healthy",
    "answer_generator": "healthy"
  }
}
```

#### **SHOW: Query Endpoint**

**Browser:**
Click "Try it out" on `/api/v1/query`

**Request Body:**
```json
{
  "query": "¿Cuáles son los principales destinos turísticos en Cusco?",
  "model": "openai",
  "top_k": 3
}
```

**Script:**
> "Here's a query asking about main tourist destinations in Cusco. Notice the request accepts:
> - The question in Spanish or English
> - Model selection (OpenAI, Claude, DeepSeek, etc.)
> - Number of documents to retrieve (top_k)
>
> The response includes the answer, source citations with metadata, and performance metrics."

**Point out response structure:**
- `answer`: Generated response
- `sources`: Retrieved documents with page numbers
- `metadata`: Latency breakdown
- `model_used`: Which LLM generated the answer

---

### **ACT 4: Web Frontend** (3 minutes)

#### **SHOW: Start Frontend**

**Terminal 2:**
```bash
streamlit run app/streamlit_app.py
```

**Script:**
> "Now let's look at the user-facing web interface. This is a Streamlit app with a custom Peru theme."

#### **SHOW: Frontend Features**

**Browser:**
Open http://localhost:8501

**Walk through:**

1. **API Health Check** (Sidebar)
   > "First, the sidebar shows real-time API health status. All components are green - healthy."

2. **Model Selection** (Sidebar)
   > "Users can choose from 5 different LLM providers - OpenAI, Claude, DeepSeek, Azure OpenAI, or HuggingFace. This gives cost flexibility and vendor independence."

3. **Advanced Settings** (Sidebar)
   > "Advanced users can adjust the number of documents to retrieve and toggle metadata display."

4. **Example Queries** (Sidebar)
   > "New users can click example questions to get started."

5. **Query Interface** (Main)
   **Type in query box:**
   ```
   ¿Qué documentos necesito para viajar a Perú desde Estados Unidos?
   ```
   
   **Click "🔍 Buscar Respuesta"**
   
   > "Let's ask about travel documents from the US to Peru."

6. **Results Display**
   **Point out:**
   - Answer box with formatted response
   - Performance metrics (total latency, retrieval time, generation time)
   - Source citations with expandable metadata
   - Page numbers and source IDs

**Script:**
> "The response is generated in under 500ms. You can see exactly which documents were used with page numbers and metadata. This transparency is crucial for trust."

7. **Different Model Comparison**
   **Change model to "Claude" in sidebar**
   **Click "🔍 Buscar Respuesta" again**
   
   > "Let's try the same question with Claude instead of GPT-4. Notice how easy it is to switch models - the abstraction layer handles all provider differences."

---

### **ACT 5: Deployment & DevOps** (2 minutes)

#### **SHOW: Docker Deployment**

**VSCode:**
Open `Dockerfile`

**Script:**
> "The system is containerized with Docker using multi-stage builds. The builder stage installs dependencies, and the runtime stage is minimal - around 500MB.
>
> This Dockerfile includes:
> - Non-root user for security
> - Health check endpoint
> - Environment variable configuration
> - Optimized layer caching"

#### **SHOW: Multi-Cloud Deployment**

**VSCode:**
Open `scripts/deployment/deploy-azure.sh`

**Script:**
> "I've created deployment scripts for three major cloud providers:
> - Azure Container Apps
> - AWS ECS Fargate
> - Google Cloud Run
>
> Each script handles:
> - Building and pushing images
> - Creating infrastructure
> - Deploying the application
> - Configuring auto-scaling
> - Setting up monitoring"

**Scroll to show key sections:**
- Resource group creation
- Container registry
- Secret management
- Service deployment

#### **SHOW: Deployment Documentation**

**VSCode:**
Open `scripts/deployment/README.md`

**Script:**
> "The deployment docs include cost estimates, security best practices, and monitoring setup. For example:
> - Azure: ~$20-30/month
> - AWS: ~$30-40/month  
> - GCP: ~$5-15/month with pay-per-use
>
> All three support auto-scaling based on CPU/memory metrics."

---

### **ACT 6: Documentation & Metrics** (2 minutes)

#### **SHOW: Comprehensive README**

**VSCode:**
Open `README_NEW.md`

**Scroll through sections:**
1. **Badges** - Python, FastAPI, Streamlit, Tests, Coverage
2. **Quick Start** - Multiple installation options
3. **Architecture** - System diagram
4. **API Docs** - All endpoints with examples
5. **Development Guide** - Testing, code quality
6. **Deployment** - Multi-cloud guides
7. **Performance** - Benchmarks

**Script:**
> "The README is production-ready with:
> - Multiple installation paths (conda, pip, Docker)
> - Complete API documentation
> - Deployment guides for all platforms
> - Performance benchmarks
> - Contributing guidelines"

#### **SHOW: Final Summary**

**VSCode:**
Open `FINAL_SUMMARY.md`

**Highlight key metrics:**

**Script:**
> "Let me show you the final project statistics:
> - **16 commits** across 5 weeks
> - **73+ files** with ~15,000 lines of code
> - **505 tests** - all passing with 94% coverage
> - **9 major components** - all production-ready
> - **5 LLM providers** - multi-vendor support
> - **4 deployment targets** - cloud flexibility
>
> This represents about 48 hours of focused development following industry best practices."

**Scroll to achievements:**
> "Key achievements include:
> - ✅ Multi-cloud deployment ready
> - ✅ Comprehensive test coverage
> - ✅ Clean, modular architecture
> - ✅ Auto-generated API docs
> - ✅ Health monitoring built-in
> - ✅ Multiple LLM providers
> - ✅ Production-grade error handling"

---

### **ACT 7: Code Walkthrough** (Optional - 3 minutes if time permits)

#### **SHOW: RAG Generator**

**VSCode:**
Open `src/rag/answer_generator.py`

**Highlight:**
- `generate_answer()` method
- Prompt engineering
- Citation extraction
- Error handling

**Script:**
> "This is the core RAG logic. It:
> 1. Takes the user query and retrieved documents
> 2. Formats them into a prompt with Peru context
> 3. Calls the LLM with temperature control
> 4. Extracts citations from the response
> 5. Returns structured output with metadata
>
> Notice the comprehensive error handling and logging."

#### **SHOW: LLM Abstraction**

**VSCode:**
Open `src/llm/base.py`

**Script:**
> "The LLM abstraction uses Python's ABC (Abstract Base Class) to define a common interface. This makes it trivial to add new providers - just implement 3 methods:
> - `generate()` - sync generation
> - `agenerate()` - async generation  
> - `validate_config()` - config validation
>
> Currently supporting OpenAI, Claude, DeepSeek, Azure, and HuggingFace."

---

## 🎭 DEMO CLOSING (1 minute)

### Summary

**Script:**
> "To summarize, PeruGuide AI demonstrates:
>
> **Technical Excellence:**
> - Clean architecture with 94% test coverage
> - Production-grade API with FastAPI
> - Multi-provider LLM support
> - Enterprise deployment capabilities
>
> **Best Practices:**
> - Test-driven development
> - Comprehensive documentation
> - Docker containerization
> - Multi-cloud deployment
> - Health monitoring
> - Structured logging
>
> **Business Value:**
> - Reduces tourist research time by 96% (5 hours → 15 minutes)
> - Scalable to millions of queries
> - Cloud-agnostic architecture
> - Cost-optimized with multiple LLM options
>
> The entire codebase is on GitHub, fully documented, and ready to deploy.
>
> Questions?"

---

## 💡 Q&A Preparation

### Common Questions & Answers

**Q: How do you handle rate limiting from LLM providers?**
> A: Each provider has configurable retry logic with exponential backoff. In production, I'd add Redis caching and queue-based processing.

**Q: What about data privacy and security?**
> A: The system uses environment variables for secrets, supports Azure Key Vault/AWS Secrets Manager, and processes data in-memory without persistence of user queries.

**Q: How does this scale?**
> A: The vector store supports millions of documents, API is stateless for horizontal scaling, and cloud deployment includes auto-scaling. Current benchmarks show ~100 req/min on a single instance.

**Q: What's the cost to run this in production?**
> A: GCP Cloud Run is cheapest at $5-15/month (pay-per-use). Azure Container Apps is ~$20-30/month. LLM costs depend on usage - OpenAI ~$0.002/query with GPT-3.5.

**Q: How do you ensure answer quality?**
> A: Multiple layers - prompt engineering, citation tracking, metadata filtering, and top_k tuning. In production, I'd add human feedback loop and A/B testing.

**Q: Can this be adapted to other domains?**
> A: Absolutely. The architecture is domain-agnostic. Just swap the PDFs, retrain embeddings, and adjust prompts. Everything else stays the same.

**Q: What's next for this project?**
> A: Planned enhancements include WebSocket streaming, Redis caching, user authentication, Prometheus metrics, and CI/CD pipeline with GitHub Actions.

---

## 🎬 Alternative Demo Paths

### Short Demo (5 minutes)
1. Problem statement (30s)
2. Test execution (1m)
3. API demo (2m)
4. Frontend demo (1m)
5. Metrics summary (30s)

### Technical Deep-Dive (20 minutes)
Add:
- Vector store internals
- Embedding model selection
- Prompt engineering techniques
- Cost optimization strategies
- Monitoring and observability

### Business-Focused (8 minutes)
Emphasize:
- ROI calculation
- User research reduction (96% time saving)
- Scalability to other tourism markets
- Cost per query vs. human research
- Deployment timeline (hours, not weeks)

---

## 📊 Demo Metrics to Highlight

### Speed
- **Test Suite:** 505 tests in ~10 seconds
- **API Response:** <250ms average
- **Retrieval:** ~12ms for top-5 results
- **Generation:** ~230ms with GPT-3.5

### Quality
- **Test Coverage:** 94%+ across all components
- **Code Quality:** Type hints, docstrings, clean architecture
- **Documentation:** 3,000+ lines of docs

### Scale
- **Vector Store:** 1M documents (tested)
- **Throughput:** ~100 req/min (single instance)
- **Deployment:** Azure, AWS, GCP ready

---

## 🛠️ Troubleshooting

### If API Doesn't Start
```bash
# Check port 8000 is free
netstat -ano | findstr :8000

# Try different port
uvicorn src.api.main:app --reload --port 8001
```

### If Frontend Has Connection Error
```bash
# Check API_URL in app/.streamlit/secrets.toml
echo API_URL = "http://localhost:8000" > app/.streamlit/secrets.toml
```

### If Tests Fail
```bash
# Ensure dependencies are installed
pip install -r requirements-test.txt

# Run with verbose output
pytest tests/integration/test_simple_rag.py -vv
```

---

## 📝 Post-Demo Follow-Up

### Materials to Share
- GitHub repository link
- README_NEW.md (overview)
- FINAL_SUMMARY.md (metrics)
- Live demo recording (if available)
- Architecture diagram

### Next Steps
- Share repository link
- Offer to walk through any specific component
- Discuss potential adaptations to company's needs
- Schedule technical deep-dive if interested

---

**Demo Script Version:** 1.0  
**Last Updated:** October 24, 2025  
**Status:** ✅ Ready for Production

**Good luck with your demo!** 🚀🇵🇪
