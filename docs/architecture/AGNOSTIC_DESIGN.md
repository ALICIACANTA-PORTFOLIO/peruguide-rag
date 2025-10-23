# 🔄 Filosofía Agnóstica de PeruGuide AI

**Principio Central:** El sistema debe funcionar con **cualquier conjunto de documentos PDF**, no solo guías de turismo de Perú.

---

## 🎯 Objetivos del Diseño Agnóstico

### **1. Reutilizabilidad**
El código debe ser reutilizable para diferentes dominios:
- ✅ Turismo (Perú, Chile, Argentina, cualquier país)
- ✅ Documentación técnica (manuales, guías)
- ✅ Normativas legales (regulaciones, políticas)
- ✅ Academia (papers, libros)
- ✅ Corporativo (reportes internos, procedimientos)

### **2. Flexibilidad de Fuentes**
No asumir una estructura específica de carpetas o nombres de archivos:
- ❌ Hardcoded: `PDF_SOURCE_DIR = "./Complementarios Peru"`
- ✅ Configurable: `PDF_SOURCE_DIR` en `.env` (usuario decide)

### **3. Metadata Agnóstica**
No asumir campos de metadata específicos:
- ❌ Hardcoded: `{"departamento": "Cusco", "categoria": "turismo"}`
- ✅ Configurable: `METADATA_FIELDS` en `.env` (usuario define)

---

## 📁 Estructura de Datos Agnóstica

### **Enfoque Actual (Recomendado)**

```
data/
├── raw/                    # Fuente agnóstica (configurable)
│   ├── *.pdf              # Cualquier PDF
│   ├── subdirectory/      # Estructura libre
│   └── ...
├── processed/             # Outputs intermedios
│   ├── extracted_text/
│   ├── chunks/
│   └── metadata/
└── vector_stores/         # Vector DBs
    ├── faiss/
    └── chroma/
```

### **Configuración en `.env`**

```bash
# Usuario decide la fuente
PDF_SOURCE_DIR=./data/raw
# O
PDF_SOURCE_DIR=./Complementarios Peru
# O
PDF_SOURCE_DIR=./documents/legal_docs
# O
PDF_SOURCE_DIR=/mnt/shared/pdfs

# Agnóstico de nombres de archivos
PDF_FILE_PATTERN=*.pdf
PDF_RECURSIVE=true
```

---

## 🧩 Componentes Agnósticos

### **1. PDF Loader (`src/data_pipeline/loaders/pdf_loader.py`)**

#### ❌ Diseño No Agnóstico (evitar)
```python
def load_pdf(path: str) -> dict:
    # PROBLEMA: Asume estructura específica
    if "Cusco" in path:
        metadata = {"departamento": "Cusco", "tipo": "turismo"}
    elif "Lima" in path:
        metadata = {"departamento": "Lima", "tipo": "turismo"}
    ...
```

#### ✅ Diseño Agnóstico (correcto)
```python
def load_pdf(
    path: str, 
    metadata_extractor: Optional[Callable] = None
) -> dict:
    """
    Carga PDF de forma agnóstica.
    
    Args:
        path: Ruta al PDF (cualquier ubicación)
        metadata_extractor: Función opcional para extraer metadata custom
    
    Returns:
        dict con text, metadata (solo filename por defecto)
    """
    text = extract_text(path)
    
    # Metadata mínima (siempre presente)
    metadata = {
        "filename": os.path.basename(path),
        "filepath": path,
        "timestamp": datetime.now().isoformat()
    }
    
    # Usuario puede inyectar extractor custom
    if metadata_extractor:
        custom_metadata = metadata_extractor(path, text)
        metadata.update(custom_metadata)
    
    return {"text": text, "metadata": metadata}
```

---

### **2. Metadata Extractor (`src/data_pipeline/processors/metadata_extractor.py`)**

#### ✅ Diseño Extensible
```python
class MetadataExtractor:
    """
    Extractor agnóstico de metadata.
    Usuario puede configurar fields a extraer.
    """
    
    def __init__(self, fields: List[str] = None):
        """
        Args:
            fields: Lista de campos a extraer (configurable)
                   Ej: ["category", "region", "author"]
        """
        self.fields = fields or ["filename"]  # Mínimo por defecto
    
    def extract(self, path: str, text: str) -> dict:
        """Extrae metadata según configuración."""
        metadata = {}
        
        if "category" in self.fields:
            metadata["category"] = self._infer_category(text)
        
        if "region" in self.fields:
            metadata["region"] = self._extract_region(path, text)
        
        if "author" in self.fields:
            metadata["author"] = self._extract_author(text)
        
        return metadata
    
    def _infer_category(self, text: str) -> str:
        """
        Inferencia genérica de categoría.
        NOTA: Método naive, puede mejorarse con ML.
        """
        # Agnóstico: no asume "turismo" como única opción
        keywords = {
            "turismo": ["destino", "visitar", "atracciones"],
            "legal": ["articulo", "ley", "normativa"],
            "técnico": ["manual", "procedimiento", "especificación"]
        }
        # ... lógica genérica
        return "general"  # Fallback
```

---

### **3. Configuración Flexible (`.env`)**

```bash
# ============================================================================
# METADATA CONFIGURATION (Agnóstico)
# ============================================================================
EXTRACT_METADATA=true
METADATA_FIELDS=["filename", "category", "region"]  # Personalizable

# Ejemplo 1: Turismo Perú
# METADATA_FIELDS=["filename", "departamento", "categoria", "region"]

# Ejemplo 2: Documentos Legales
# METADATA_FIELDS=["filename", "tipo_norma", "fecha", "entidad"]

# Ejemplo 3: Papers Académicos
# METADATA_FIELDS=["filename", "authors", "year", "venue"]

# Ejemplo 4: Mínimo (solo filename)
# METADATA_FIELDS=["filename"]
```

---

## 🎨 Ejemplo de Uso Multi-Dominio

### **Caso 1: Turismo Perú (Original)**
```bash
# .env
PDF_SOURCE_DIR=./Complementarios Peru
METADATA_FIELDS=["filename", "departamento", "categoria"]
CHUNK_SIZE=512
```

### **Caso 2: Documentos Legales**
```bash
# .env
PDF_SOURCE_DIR=./data/legal_docs
METADATA_FIELDS=["filename", "tipo_norma", "fecha"]
CHUNK_SIZE=1024  # Chunks más largos para contexto legal
```

### **Caso 3: Papers Académicos**
```bash
# .env
PDF_SOURCE_DIR=./data/papers
METADATA_FIELDS=["filename", "authors", "year", "venue"]
CHUNK_SIZE=256  # Chunks más pequeños para búsqueda precisa
```

### **Caso 4: Corporativo Interno**
```bash
# .env
PDF_SOURCE_DIR=/mnt/company_docs
METADATA_FIELDS=["filename", "department", "confidentiality"]
CHUNK_SIZE=512
```

---

## 🔧 Implementación: Checklist Agnóstico

Al implementar cada componente, verificar:

### **✅ PDF Loader**
- [ ] No hardcodea paths específicos
- [ ] Acepta cualquier estructura de carpetas
- [ ] Metadata mínima (solo filename) por defecto
- [ ] Permite inyección de metadata extractor custom
- [ ] Maneja encodings variados (UTF-8, Latin-1, etc.)

### **✅ Text Processor**
- [ ] No asume idioma específico (español/inglés)
- [ ] Cleaning genérico (no específico a turismo)
- [ ] Configurable desde `.env` (ej: stopwords)

### **✅ Chunker**
- [ ] Chunk_size configurable
- [ ] Separadores configurables
- [ ] No asume estructura de documento específica

### **✅ Embedding Pipeline**
- [ ] Modelo configurable en `.env`
- [ ] Soporta diferentes dimensiones
- [ ] Agnóstico del dominio (usa modelo multilingual)

### **✅ Vector Store**
- [ ] Collection/index name configurable
- [ ] Path configurable
- [ ] Soporta múltiples stores (FAISS, Chroma, etc.)

### **✅ Retrieval Pipeline**
- [ ] top_k configurable
- [ ] threshold configurable
- [ ] Agnóstico del dominio de consulta

### **✅ Inference Pipeline**
- [ ] Prompt templates configurables
- [ ] LLM model configurable
- [ ] No asume conocimiento de dominio específico

---

## 📊 Beneficios del Diseño Agnóstico

### **Para el Proyecto**
1. ✅ **Portfolio Value:** Demuestra pensamiento arquitectónico
2. ✅ **Reutilizabilidad:** Código aplicable a múltiples dominios
3. ✅ **Escalabilidad:** Fácil agregar nuevos tipos de documentos
4. ✅ **Mantenibilidad:** Menos código hardcoded

### **Para el Usuario**
1. ✅ **Flexibilidad:** Puede usar sus propios documentos
2. ✅ **Personalización:** Configura según su dominio
3. ✅ **Facilidad:** No necesita modificar código

### **Para Entrevistas**
1. ✅ **Design Patterns:** Demuestra conocimiento de dependency injection
2. ✅ **Best Practices:** Configuration over hardcoding
3. ✅ **Visión:** Piensas en escalabilidad desde inicio

---

## 🚫 Anti-Patterns a Evitar

### **❌ Hardcoding de Paths**
```python
# MAL
def load_pdfs():
    return glob.glob("./Complementarios Peru/*.pdf")

# BIEN
def load_pdfs(source_dir: str):
    return glob.glob(f"{source_dir}/*.pdf")
```

### **❌ Metadata Específica del Dominio**
```python
# MAL
def extract_metadata(path):
    return {
        "departamento": extract_departamento(path),  # Específico a Perú
        "categoria": "turismo"  # Hardcoded
    }

# BIEN
def extract_metadata(path, fields: List[str]):
    metadata = {}
    for field in fields:
        metadata[field] = extract_field(path, field)
    return metadata
```

### **❌ Prompts Hardcoded**
```python
# MAL
PROMPT = """Eres un asistente de turismo de Perú.
Responde sobre destinos turísticos en Perú."""

# BIEN
PROMPT_TEMPLATE = os.getenv("PROMPT_TEMPLATE", """
Eres un asistente experto en {domain}.
Responde preguntas sobre {topic} basándote en el contexto.
""")
```

---

## 📝 Documentación Agnóstica

### **README.md**
- Mencionar que el sistema es **domain-agnostic**
- Dar ejemplos de múltiples use cases
- Mostrar cómo configurar para diferentes dominios

### **docs/**
- Crear guía: `docs/guides/custom-domain.md`
- Explicar cómo adaptar a nuevos dominios
- Ejemplos de configuración para 3+ dominios

### **Comments en Código**
```python
"""
PDF Loader - Domain Agnostic

This loader works with ANY PDF documents, not just tourism guides.
Configure source directory and metadata fields in .env

Examples:
    - Tourism: Peru, Chile, Argentina tourism guides
    - Legal: Regulations, policies, laws
    - Academic: Research papers, textbooks
    - Corporate: Internal reports, manuals
"""
```

---

## 🎯 Validación del Diseño Agnóstico

### **Test 1: Cambio de Dominio (Turismo → Legal)**
```bash
# 1. Cambiar .env
PDF_SOURCE_DIR=./data/legal_docs
METADATA_FIELDS=["filename", "tipo_norma"]

# 2. Ejecutar pipeline (sin cambios en código)
python scripts/prepare_data.py
python scripts/build_vector_store.py

# 3. Verificar
# ✅ Debería funcionar sin modificar src/
```

### **Test 2: Cambio de Idioma (Español → Inglés)**
```bash
# 1. Cambiar embedding model en .env
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# 2. Ejecutar pipeline
# ✅ Debería funcionar sin cambios
```

### **Test 3: Cambio de Estructura de Carpetas**
```bash
# 1. Organizar PDFs en estructura custom
data/raw/
├── level1/
│   ├── level2a/
│   │   └── docs1.pdf
│   └── level2b/
│       └── docs2.pdf

# 2. Configurar
PDF_SOURCE_DIR=./data/raw
PDF_RECURSIVE=true

# 3. Ejecutar
# ✅ Debería encontrar todos los PDFs recursivamente
```

---

## 🚀 Implementación Semana 1 con Filosofía Agnóstica

### **Día 1-2: PDF Loader Agnóstico**
```python
# src/data_pipeline/loaders/pdf_loader.py
class PDFLoader:
    def __init__(
        self,
        source_dir: str,
        recursive: bool = True,
        file_pattern: str = "*.pdf",
        metadata_extractor: Optional[Callable] = None
    ):
        """Agnóstico: acepta cualquier configuración."""
        self.source_dir = source_dir
        self.recursive = recursive
        self.file_pattern = file_pattern
        self.metadata_extractor = metadata_extractor
    
    def load_documents(self) -> List[Document]:
        """Carga PDFs desde cualquier fuente."""
        # Implementación agnóstica
        ...
```

### **Día 3-4: Text Processor Agnóstico**
```python
# src/data_pipeline/processors/cleaner.py
class TextCleaner:
    def __init__(self, cleaning_rules: Optional[dict] = None):
        """Agnóstico: rules configurables."""
        self.rules = cleaning_rules or self._default_rules()
    
    def clean(self, text: str) -> str:
        """Limpieza genérica (no específica a dominio)."""
        # Implementación agnóstica
        ...
```

---

## 📚 Referencias para Diseño Agnóstico

- **LLM Engineer's Handbook (Cap 3):** "Build Modular Data Pipelines"
- **Clean Architecture (Uncle Bob):** Dependency Inversion Principle
- **12-Factor App:** Store config in environment
- **Design Patterns:** Strategy Pattern, Dependency Injection

---

## ✅ Resumen

### **Principios Clave:**
1. ✅ **Configuration over Hardcoding:** Todo en `.env`
2. ✅ **Dependency Injection:** Inyectar comportamiento custom
3. ✅ **Minimal Assumptions:** No asumir dominio específico
4. ✅ **Extensibility:** Fácil agregar nuevos dominios
5. ✅ **Documentation:** Explicar cómo adaptar a nuevos casos

### **Resultado:**
Un sistema RAG que funciona con **cualquier conjunto de PDFs**, no solo guías de turismo de Perú. Esto demuestra:
- Pensamiento arquitectónico profesional
- Código reutilizable y escalable
- Diseño mantenible a largo plazo

---

**Próximo:** Al implementar `src/data_pipeline/loaders/pdf_loader.py` esta semana, seguir estos principios desde el inicio.
