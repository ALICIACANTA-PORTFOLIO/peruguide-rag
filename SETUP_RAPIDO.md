# ⚡ Setup Rápido - 5 Minutos

**Estado:** Entorno Conda `peruguide-rag` ya creado ✅  
**Objetivo:** Instalar dependencias y verificar que todo funciona

---

## 🚀 Comandos (Copiar y Pegar)

### **Paso 1: Activar Entorno (5 seg)**
```powershell
conda activate peruguide-rag
```

### **Paso 2: Instalar Dependencias (3-5 min)**
```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### **Paso 3: Configurar Environment (30 seg)**
```powershell
Copy-Item .env.example .env
```

**Luego editar `.env` con:**
```bash
# Línea ~97: Cambiar según tu fuente de PDFs
PDF_SOURCE_DIR=./Complementarios Peru
```

### **Paso 4: Instalar Pre-commit (30 seg)**
```powershell
pre-commit install
```

### **Paso 5: Verificar Instalación (10 seg)**
```powershell
python -c "import langchain; print('✅ LangChain OK')"
python -c "import fastapi; print('✅ FastAPI OK')"
python -c "import streamlit; print('✅ Streamlit OK')"
pytest --version
```

---

## ✅ Si Todo Funciona Verás:

```
✅ LangChain OK
✅ FastAPI OK
✅ Streamlit OK
pytest 7.4.x
```

---

## 🎯 Después del Setup

### **Opción A: Revisar Notebooks (Recomendado primero)**
```powershell
# Ver notebooks de referencia
jupyter notebook analisis/notebook/
```

**Lee:** `analisis/NOTEBOOKS_REFERENCE.md` para entender qué buscar

### **Opción B: Empezar Implementación**
```powershell
# Crear primer archivo
code src/data_pipeline/loaders/pdf_loader.py
```

**Seguir:** Principios de `docs/architecture/AGNOSTIC_DESIGN.md`

---

## 🆘 Troubleshooting

### **Error: conda no reconocido**
```powershell
# Verificar conda está en PATH
conda --version

# Si no funciona, inicializar conda para PowerShell
conda init powershell
# Luego cerrar y reabrir terminal
```

### **Error: pip install falla**
```powershell
# Actualizar pip primero
python -m pip install --upgrade pip

# Luego reintentar
pip install -r requirements.txt
```

### **Error: pre-commit install falla**
```powershell
# Instalar pre-commit primero
pip install pre-commit

# Luego instalarlo
pre-commit install
```

---

## 📋 Checklist Post-Setup

- [ ] Entorno activado: `conda activate peruguide-rag`
- [ ] Dependencias instaladas (sin errores)
- [ ] `.env` creado y editado
- [ ] Pre-commit instalado
- [ ] Verificación exitosa (todos ✅)
- [ ] Leer `ACTUALIZACION_CONDA_AGNOSTICO.md`
- [ ] Leer `docs/architecture/AGNOSTIC_DESIGN.md`

---

## 🎉 ¡Setup Completo!

**Tiempo total:** 5-10 minutos

**Próximo paso:** Leer `START_HERE.md` sección "💡 Consejos para Empezar"

---

**Nota:** Este es el setup mínimo. Para entender el contexto completo, lee `ACTUALIZACION_CONDA_AGNOSTICO.md`
