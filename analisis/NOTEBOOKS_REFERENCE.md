# 📓 Notebooks de Referencia - PeruGuide AI

**Ubicación:** `analisis/notebook/`  
**Propósito:** Documentación de experimentos y desarrollo académico previo  
**Fecha de archivo:** 23 de Octubre de 2025

---

## 📋 Inventario de Notebooks

### 1. `00_analyze_reference_materials.ipynb`
**Descripción:** Análisis exploratorio de materiales de referencia (libros técnicos)

**Contenido esperado:**
- Análisis de 9 libros técnicos sobre LLMs, RAG, embeddings
- Extracción de best practices de 2,959 páginas
- Generación de `materials_analysis_comprehensive.json`

**Uso en Nivel 2:**
- ✅ Ya completado - resultados archivados en `analisis/`
- Los insights ya están documentados en `TECHNICAL_BEST_PRACTICES.md`
- No requiere re-ejecución

**Estado:** 📚 Archivado (fase de análisis completada)

---

### 2. `MNA_NLP_actividad_chatbot_LLM_RAG (3).ipynb`
**Descripción:** Notebook académico - Actividad de chatbot con LLM y RAG

**Contenido típico:**
- Implementación básica de RAG pipeline
- Pruebas de concepto con embeddings
- Experimentos con modelos LLM
- Evaluación básica de respuestas

**Lecciones para Nivel 2:**
- 🔍 **Chunking:** Estrategia de división de documentos
- 🔍 **Retrieval:** Configuración de top_k y thresholds
- 🔍 **Prompt Engineering:** Templates de prompts efectivos
- 🔍 **Errores comunes:** Casos edge identificados

**Recomendación:**
- Revisar para extraer configuraciones que funcionaron bien
- Identificar parámetros óptimos (chunk_size, top_k, temperature)
- Documentar problemas encontrados y soluciones aplicadas

**Acción sugerida:**
```bash
# Revisar notebook para extraer insights
jupyter notebook analisis/notebook/MNA_NLP_actividad_chatbot_LLM_RAG\ \(3\).ipynb

# O convertir a script para análisis
jupyter nbconvert --to python "analisis/notebook/MNA_NLP_actividad_chatbot_LLM_RAG (3).ipynb"
```

---

### 3. `NLP_LLM_con_RAG_y_VectorDatabase_FAISS_Chrome_Wikipedia.ipynb`
**Descripción:** Experimento con RAG usando FAISS, ChromaDB y Wikipedia

**Contenido típico:**
- Comparación FAISS vs ChromaDB
- Integración con datos de Wikipedia
- Benchmarks de performance
- Configuración de vector stores

**Lecciones para Nivel 2:**
- 🔍 **Vector Store:** Comparación FAISS vs Chroma (pros/cons)
- 🔍 **Indexing:** Estrategias de indexación y persistencia
- 🔍 **Benchmarking:** Métricas de latencia y throughput
- 🔍 **Escalabilidad:** Pruebas con diferentes volúmenes de datos

**Recomendación:**
- Extraer configuraciones óptimas de FAISS/Chroma
- Documentar benchmarks para referencia
- Identificar límites de escalabilidad observados

**Acción sugerida:**
```bash
# Revisar notebook para configuraciones
jupyter notebook analisis/notebook/NLP_LLM_con_RAG_y_VectorDatabase_FAISS_Chrome_Wikipedia.ipynb

# Exportar resultados/benchmarks si existen
```

---

## 🎯 Cómo Usar estos Notebooks en Nivel 2

### **Paso 1: Auditoría de Experimentos**
1. Ejecutar cada notebook en el entorno Conda `peruguide-rag`
2. Documentar resultados y configuraciones exitosas
3. Extraer parámetros óptimos encontrados

### **Paso 2: Extracción de Conocimiento**
Crear un documento `LESSONS_LEARNED.md` con:
- ✅ **Configuraciones que funcionaron:**
  ```python
  chunk_size = 512  # Óptimo según experimentos
  top_k = 5         # Balance precision/recall
  temperature = 0.3 # Respuestas consistentes
  ```
- ❌ **Errores a evitar:**
  - Chunks muy grandes (>1000 tokens) → contexto irrelevante
  - top_k muy bajo (<3) → pérdida de información
  - temperature muy alta (>0.7) → respuestas inconsistentes

### **Paso 3: Migración de Código Útil**
Identificar snippets reutilizables:
```python
# Ejemplo: Si en notebook hay buen preprocessing
# Migrar a: src/data_pipeline/processors/cleaner.py

# Ejemplo: Si hay buena configuración de embeddings
# Migrar a: src/embedding_pipeline/models/sentence_transformer.py
```

### **Paso 4: Documentar Gaps**
¿Qué falta en los notebooks que necesitamos en Nivel 2?
- Error handling robusto
- Logging estructurado
- Tests unitarios
- Monitoring de performance
- Deployment considerations

---

## 📊 Comparación: Notebooks vs Nivel 2

| Aspecto | Notebooks (Académico) | Nivel 2 (Producción) |
|---------|----------------------|----------------------|
| **Estructura** | Lineal, exploratorio | Modular, reutilizable |
| **Testing** | Manual, ad-hoc | Automatizado >75% coverage |
| **Error Handling** | Básico/inexistente | Robusto con logging |
| **Documentation** | Markdown cells | Docstrings + MkDocs |
| **Performance** | No optimizado | Benchmarked, monitoreado |
| **Deployment** | No deployable | Docker + CI/CD ready |
| **Reproducibilidad** | Variable | 100% reproducible |

---

## 🔄 Flujo de Trabajo Recomendado

### **Durante Implementación Semana 1:**

```bash
# 1. Activar entorno
conda activate peruguide-rag

# 2. Revisar notebook relevante
jupyter notebook analisis/notebook/[NOTEBOOK_NAME].ipynb

# 3. Extraer configuración exitosa
# Ejemplo: chunk_size, embedding_model, etc.

# 4. Implementar en código profesional
# src/data_pipeline/...
# src/embedding_pipeline/...

# 5. Agregar tests
# tests/unit/test_[module].py

# 6. Documentar decisión
# docs/architecture/decisions/ADR-001-chunking-strategy.md
```

### **Checklist de Extracción por Notebook:**

#### Para `MNA_NLP_actividad_chatbot_LLM_RAG (3).ipynb`:
- [ ] Extraer chunk_size óptimo
- [ ] Extraer prompt templates efectivos
- [ ] Identificar modelos LLM usados
- [ ] Documentar métricas de evaluación
- [ ] Identificar casos edge/problemas

#### Para `NLP_LLM_con_RAG_y_VectorDatabase_FAISS_Chrome_Wikipedia.ipynb`:
- [ ] Extraer configuración FAISS exitosa
- [ ] Comparar FAISS vs Chroma (benchmarks)
- [ ] Documentar índice óptimo (IndexFlatL2, etc.)
- [ ] Extraer estrategia de persistencia
- [ ] Identificar límites de escalabilidad

---

## 💡 Insights Clave a Buscar

### **1. Hiperparámetros Óptimos**
- `chunk_size`: ¿Cuál dio mejores resultados?
- `chunk_overlap`: ¿Necesario? ¿Cuánto?
- `top_k`: ¿Cuántos chunks recuperar?
- `score_threshold`: ¿Umbral mínimo de similaridad?

### **2. Modelos que Funcionaron**
- Embedding model usado y dimensión
- LLM usado (local vs API)
- Configuración de temperature/max_tokens

### **3. Problemas Encontrados**
- Errores de encoding (UTF-8 vs Latin-1)
- PDFs mal formados
- Respuestas alucinadas del LLM
- Latencia inaceptable

### **4. Casos de Uso Validados**
- ¿Qué preguntas funcionaron bien?
- ¿Qué consultas fallaron?
- ¿Cuál fue la precision/recall observada?

---

## 📝 Template: LESSONS_LEARNED.md

Después de revisar notebooks, crear este documento:

```markdown
# Lessons Learned from Academic Notebooks

## Configuraciones Exitosas ✅

### Chunking
- chunk_size: 512 tokens
- chunk_overlap: 64 tokens
- Justificación: Balance entre contexto y precisión

### Embeddings
- Model: paraphrase-multilingual-mpnet-base-v2
- Dimension: 768
- Device: CPU (suficiente para <10k docs)

### Retrieval
- top_k: 5 chunks
- threshold: 0.7 cosine similarity
- search_type: similarity (MMR no mejoró resultados)

### LLM
- Model: Mistral-7B-Instruct v0.3
- temperature: 0.3 (respuestas consistentes)
- max_tokens: 512 (suficiente para respuestas completas)

## Problemas Identificados ❌

1. **Encoding de PDFs:**
   - Problema: Algunos PDFs en Latin-1 causaban UnicodeDecodeError
   - Solución: Probar UTF-8, luego Latin-1 como fallback

2. **Chunks muy largos:**
   - Problema: chunks >1000 tokens incluían contexto irrelevante
   - Solución: chunk_size=512 como máximo

3. **Alucinaciones del LLM:**
   - Problema: LLM inventaba información no presente en docs
   - Solución: Temperature baja (0.3) + prompt estricto

## Métricas Observadas 📊

- Latencia promedio: ~2.5s por query
- Precision@5: ~0.82
- Context relevance: ~0.78

## Recomendaciones para Nivel 2 🎯

1. Implementar retry logic para PDFs con encoding issues
2. Agregar logging de latencia por componente
3. Implementar cache de embeddings
4. Agregar evaluación RAGAS desde inicio
```

---

## 🚀 Próximos Pasos

1. **Esta semana:** Revisar notebooks y documentar insights
2. **Semana 1:** Usar configuraciones extraídas en implementación
3. **Semana 2:** Comparar resultados Nivel 2 vs notebooks
4. **Semana 3:** Evaluar mejoras con RAGAS

---

## 📚 Referencias

- Notebooks originales: `analisis/notebook/`
- Análisis de materiales: `analisis/materials_analysis_comprehensive.json`
- Best practices técnicas: `TECHNICAL_BEST_PRACTICES.md`
- Planteamiento definitivo: `analisis/PLANTEAMIENTO_DEFINITIVO_CON_ANALISIS.md`

---

**Nota:** Estos notebooks representan el trabajo académico y experimental. El Nivel 2 toma los learnings y los convierte en código profesional, testeable y deployable.
