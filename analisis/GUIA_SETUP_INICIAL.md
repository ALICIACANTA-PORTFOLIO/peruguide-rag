# 🚀 GUÍA RÁPIDA: PRIMEROS PASOS
## PeruGuide AI - De 0 a Running en 1 Día

**Objetivo:** Tener el proyecto inicializado y listo para desarrollo  
**Tiempo estimado:** 2-3 horas  
**Requisitos:** Python 3.10+, Git, cuenta GitHub

---

## ✅ CHECKLIST PRE-INICIO (15 minutos)

Antes de escribir cualquier código, valida:

### **Confirmación de Decisión**
- [ ] Leí `PROYECTO_PORTAFOLIO_FINAL.md` completo
- [ ] Leí `RESUMEN_DECISIONES_CLAVE.md`
- [ ] Entiendo el caso de uso y el valor del proyecto
- [ ] Estoy comprometido a completarlo (5 semanas, 75-100 horas)
- [ ] Tengo el tiempo necesario bloqueado en mi calendario

### **Validación Técnica**
```powershell
# Verifica Python version (debe ser 3.10+)
python --version

# Verifica Git
git --version

# Verifica espacio en disco (necesitas ~20GB)
Get-PSDrive C | Select-Object Used,Free
```

### **Preparación de Entorno**
- [ ] Tengo IDE configurado (VS Code recomendado)
- [ ] Tengo cuenta de GitHub activa
- [ ] Tengo cuenta de Hugging Face (crea en https://huggingface.co)
- [ ] Los 30+ PDFs están en "Complementarios Peru" folder
- [ ] Hice backup de los datos

---

## 📁 PASO 1: CREAR REPOSITORIO (20 minutos)

### **1.1 Crear repo en GitHub**

**Opción A: Desde GitHub CLI** (recomendado)
```powershell
# Instalar GitHub CLI si no lo tienes
# https://cli.github.com/

# Autenticarte
gh auth login

# Crear repositorio
cd d:\code\portfolio
gh repo create peruguide-ai --public --description "RAG-based intelligent tourism assistant for Peru 🇵🇪 - Production-ready system showcasing LLM Engineering, MLOps, and Product Design"

# Clonar
git clone https://github.com/TU_USERNAME/peruguide-ai.git
cd peruguide-ai
```

**Opción B: Desde GitHub Web**
1. Ve a https://github.com/new
2. Nombre: `peruguide-ai`
3. Descripción: "RAG-based intelligent tourism assistant for Peru"
4. Public ✅
5. Add README ✅
6. Add .gitignore: Python ✅
7. License: MIT ✅
8. Create repository

Luego clona:
```powershell
cd d:\code\portfolio
git clone https://github.com/TU_USERNAME/peruguide-ai.git
cd peruguide-ai
```

### **1.2 Crear estructura de carpetas**

```powershell
# Crear estructura completa
New-Item -ItemType Directory -Force -Path @(
    "src/data_ingestion",
    "src/embeddings",
    "src/retrieval",
    "src/llm",
    "src/chains",
    "src/utils",
    "api",
    "app",
    "notebooks",
    "tests/unit",
    "tests/integration",
    "data/raw",
    "data/processed",
    "data/vector_stores",
    "docs",
    "scripts",
    "docker",
    ".github/workflows"
)

# Crear archivos __init__.py
New-Item -ItemType File -Path "src/__init__.py"
New-Item -ItemType File -Path "src/data_ingestion/__init__.py"
New-Item -ItemType File -Path "src/embeddings/__init__.py"
New-Item -ItemType File -Path "src/retrieval/__init__.py"
New-Item -ItemType File -Path "src/llm/__init__.py"
New-Item -ItemType File -Path "src/chains/__init__.py"
New-Item -ItemType File -Path "src/utils/__init__.py"
```

**Estructura resultante:**
```
peruguide-ai/
├── .github/
│   └── workflows/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data_ingestion/
│   ├── embeddings/
│   ├── retrieval/
│   ├── llm/
│   ├── chains/
│   └── utils/
├── api/
├── app/
├── notebooks/
├── tests/
│   ├── unit/
│   └── integration/
├── data/
│   ├── raw/
│   ├── processed/
│   └── vector_stores/
├── docs/
├── scripts/
├── docker/
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🐍 PASO 2: SETUP DE PYTHON (30 minutos)

### **2.1 Crear ambiente virtual**

```powershell
# Crear ambiente virtual
python -m venv .venv

# Activar (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Si hay error de permisos, ejecuta:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verificar que estás en el ambiente
python --version
```

### **2.2 Crear pyproject.toml**

Crea archivo `pyproject.toml`:

```toml
[project]
name = "peruguide-ai"
version = "0.1.0"
description = "RAG-based intelligent tourism assistant for Peru"
authors = [{name = "Tu Nombre", email = "tu@email.com"}]
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}

dependencies = [
    "langchain>=0.1.0",
    "langchain-community>=0.0.10",
    "pypdf>=3.17.0",
    "sentence-transformers>=2.2.2",
    "faiss-cpu>=1.7.4",
    "chromadb>=0.4.18",
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "streamlit>=1.28.0",
    "typer>=0.9.0",
    "pydantic>=2.5.0",
    "python-dotenv>=1.0.0",
    "structlog>=23.2.0",
    "tenacity>=8.2.3",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.11.0",
    "ruff>=0.1.6",
    "mypy>=1.7.0",
    "pre-commit>=3.5.0",
    "ipykernel>=6.27.0",
    "jupyter>=1.0.0",
]
evaluation = [
    "ragas>=0.1.0",
    "datasets>=2.15.0",
]
monitoring = [
    "prometheus-client>=0.19.0",
]

[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --cov=src --cov-report=html --cov-report=term"
```

### **2.3 Instalar dependencias**

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Instalar dependencias base
pip install -e .

# Instalar dependencias de desarrollo
pip install -e ".[dev]"

# Instalar dependencias de evaluación
pip install -e ".[evaluation]"

# Verificar instalación
pip list | Select-String "langchain|faiss|streamlit"
```

---

## 🔧 PASO 3: CONFIGURACIÓN INICIAL (30 minutos)

### **3.1 Crear .env.example**

Crea archivo `.env.example`:

```bash
# ============================================
# PERUGUIDE AI - Configuration
# ============================================

# LLM Configuration
LLM_MODEL_NAME=mistral-7b-instruct
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=512

# Embeddings Configuration
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2
EMBEDDING_DEVICE=cpu
EMBEDDING_BATCH_SIZE=32

# Vector Store Configuration
VECTOR_STORE_TYPE=faiss  # faiss or chroma
VECTOR_STORE_PATH=./data/vector_stores
COLLECTION_NAME=peru_tourism

# Retrieval Configuration
RETRIEVAL_TOP_K=5
RETRIEVAL_SCORE_THRESHOLD=0.7
CHUNK_SIZE=512
CHUNK_OVERLAP=64

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# UI Configuration
UI_PORT=8501
UI_TITLE=PeruGuide AI

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Hugging Face (opcional, para modelos privados)
# HUGGINGFACE_TOKEN=your_token_here

# OpenAI (opcional, si usas GPT)
# OPENAI_API_KEY=your_key_here
```

Copia a `.env`:
```powershell
Copy-Item .env.example .env
```

### **3.2 Crear src/config.py**

Crea archivo `src/config.py`:

```python
"""Configuration management for PeruGuide AI."""
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Project
    project_name: str = "PeruGuide AI"
    version: str = "0.1.0"
    
    # Paths
    project_root: Path = Path(__file__).parent.parent
    data_dir: Path = project_root / "data"
    raw_data_dir: Path = data_dir / "raw"
    processed_data_dir: Path = data_dir / "processed"
    vector_store_path: Path = data_dir / "vector_stores"
    
    # LLM
    llm_model_name: str = "mistral-7b-instruct"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 512
    
    # Embeddings
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    embedding_device: Literal["cpu", "cuda"] = "cpu"
    embedding_batch_size: int = 32
    
    # Vector Store
    vector_store_type: Literal["faiss", "chroma"] = "faiss"
    collection_name: str = "peru_tourism"
    
    # Retrieval
    retrieval_top_k: int = 5
    retrieval_score_threshold: float = 0.7
    chunk_size: int = 512
    chunk_overlap: int = 64
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # UI
    ui_port: int = 8501
    ui_title: str = "PeruGuide AI"
    
    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "console"
    
    # Optional API Keys
    huggingface_token: str | None = None
    openai_api_key: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
```

### **3.3 Setup pre-commit hooks**

Crea `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [pydantic>=2.0]
```

Instalar hooks:
```powershell
pre-commit install
```

---

## 📄 PASO 4: README INICIAL (20 minutos)

Actualiza `README.md`:

```markdown
# 🌟 PeruGuide AI

> **Intelligent Tourism Assistant for Peru powered by RAG (Retrieval-Augmented Generation)**

Transform 5,000+ pages of official Peru tourism guides into an intelligent conversational assistant that provides personalized, verifiable, and contextual travel recommendations.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-in%20development-yellow.svg)

---

## 🎯 What is PeruGuide AI?

PeruGuide AI is a **production-ready RAG system** that showcases advanced LLM Engineering capabilities:

- 🤖 **LLM Engineering**: Production-grade RAG architecture
- 📊 **MLOps**: RAGAS evaluation, automated testing, CI/CD
- 🎨 **Product Design**: User-centered design, storytelling
- 🚀 **Deployment**: Docker, monitoring, observability

**Problem Solved:**
- ❌ 4-8 hours planning a trip to Peru
- ❌ Information scattered across 30+ PDFs
- ❌ No personalization or verification

**Solution:**
- ✅ 15-20 minutes with personalized itinerary
- ✅ 100% source citation and verification
- ✅ 95% time saved

---

## 🏗️ Architecture

```
User Interface (Streamlit/FastAPI/CLI)
           ↓
    RAG Orchestration (LangChain)
           ↓
  ┌─────────┴──────────┐
  ↓                    ↓
Retrieval          Generation
(FAISS/Chroma)    (Mistral-7B)
  ↓                    ↓
Evaluation & Monitoring (RAGAS)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- 20GB disk space
- (Optional) CUDA GPU for faster inference

### Installation

```bash
# Clone repository
git clone https://github.com/TU_USERNAME/peruguide-ai.git
cd peruguide-ai

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.\.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -e ".[dev]"

# Setup environment
cp .env.example .env
# Edit .env with your configuration
```

### Usage

**Coming soon!** This project is under active development.

---

## 📊 Project Status

- [x] Project design and architecture
- [x] Requirements and dependencies defined
- [ ] Data ingestion pipeline
- [ ] Vector store construction
- [ ] RAG pipeline implementation
- [ ] Evaluation framework
- [ ] API development
- [ ] UI development
- [ ] Deployment

**Current Phase:** Week 1 - Foundation & Setup

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Mistral-7B-Instruct |
| Embeddings | Multilingual MPNet |
| Vector Store | FAISS / Chroma |
| Orchestration | LangChain |
| API | FastAPI |
| UI | Streamlit |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Containers | Docker |

---

## 📚 Documentation

Comprehensive documentation is coming soon, including:
- Architecture Decision Records (ADR)
- API Reference
- User Guides
- Development Guides
- Deployment Guides

---

## 🤝 Contributing

This is a portfolio project showcasing LLM Engineering capabilities. While it's primarily for demonstration purposes, suggestions and feedback are welcome!

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Tu Nombre**
- GitHub: [@tu_username](https://github.com/tu_username)
- LinkedIn: [Tu Perfil](https://linkedin.com/in/tu-perfil)

---

## 🙏 Acknowledgments

- Data source: Official Peru Tourism Guides (PROMPERÚ)
- Inspired by best practices from LLM Engineer's Handbook
- Built with love for Peru 🇵🇪

---

**⭐ If you find this project interesting, please give it a star!**
```

---

## 🔄 PASO 5: PRIMER COMMIT (10 minutos)

```powershell
# Copiar PDFs a data/raw (si aún no lo hiciste)
Copy-Item -Path "d:\code\portfolio\peruguide-rag\Complementarios Peru\*.pdf" -Destination "data\raw\" -Force

# Agregar todos los archivos
git add .

# Commit inicial
git commit -m "feat: initial project setup

- Project structure with modular architecture
- Python environment with dependencies
- Configuration management with Pydantic
- Pre-commit hooks for code quality
- README with project overview
- Development environment ready"

# Push to GitHub
git push origin main
```

---

## ✅ VERIFICACIÓN FINAL (10 minutos)

Verifica que todo está listo:

```powershell
# 1. Estructura de carpetas
Get-ChildItem -Directory -Name

# 2. Ambiente virtual activo
python -c "import sys; print(sys.prefix)"

# 3. Dependencias instaladas
pip list | Select-String "langchain|faiss"

# 4. Configuración cargada
python -c "from src.config import settings; print(settings.project_name)"

# 5. PDFs en data/raw
Get-ChildItem data\raw\*.pdf | Measure-Object | Select-Object Count

# 6. Git configurado
git remote -v

# 7. Pre-commit instalado
pre-commit run --all-files
```

**Checklist final:**
- [ ] Repositorio en GitHub creado y clonado
- [ ] Estructura de carpetas completa
- [ ] Ambiente virtual creado y activado
- [ ] Dependencias instaladas sin errores
- [ ] Archivos .env y config.py creados
- [ ] Pre-commit hooks instalados
- [ ] README actualizado
- [ ] PDFs copiados a data/raw (30+ archivos)
- [ ] Primer commit realizado
- [ ] Push a GitHub exitoso

---

## 🎉 ¡LISTO PARA DÍA 1!

Si completaste todos los pasos, tu proyecto está **completamente configurado** y listo para empezar el desarrollo.

### **Próximos Pasos:**

**MAÑANA (Día 1 de Semana 1):**
1. Abre `ACTION_PLAN.md`
2. Ve a "SEMANA 1 → Día 3-4: Data Pipeline"
3. Empieza con el PDF loader

**Recordatorio:**
- Haz commits frecuentes (cada feature completa)
- Escribe tests para cada módulo
- Documenta decisiones importantes
- Mantén el README actualizado

---

## 📞 ¿PROBLEMAS?

### **Error: Python version incorrecta**
```powershell
# Instala Python 3.10+ desde python.org
# Verifica: python --version
```

### **Error: Pre-commit hooks fallan**
```powershell
# Desactiva temporalmente
pre-commit uninstall

# Arregla problemas de código
black src/
ruff check src/ --fix

# Reinstala
pre-commit install
```

### **Error: No puedo activar ambiente virtual**
```powershell
# Permisos de PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Error: Dependencias no se instalan**
```powershell
# Limpia cache de pip
pip cache purge

# Intenta de nuevo
pip install -e ".[dev]" --no-cache-dir
```

---

## 🎯 MOMENTUM ES CLAVE

**Ahora que tienes todo setup:**
1. ✅ No pospongas el Día 1
2. ✅ Dedica 2-3 horas mañana
3. ✅ El momentum inicial es crítico
4. ✅ Los primeros 3 días marcan el ritmo

**Remember:** El proyecto mejor diseñado no vale nada sin ejecución.

---

**¡Es momento de construir! 🚀**

