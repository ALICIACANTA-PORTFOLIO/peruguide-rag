#!/usr/bin/env python3
"""
Demo Rápido - Sistema RAG PeruGuide
====================================

Demostración del flujo completo RAG sin necesidad de PDFs grandes.
Usa texto de ejemplo para mostrar todas las etapas del pipeline.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("🇵🇪 DEMO RÁPIDO - SISTEMA RAG PERUGUIDE")
print("=" * 70)

# ============================================================================
# TEXTO DE EJEMPLO (simula contenido de PDFs de turismo)
# ============================================================================
print("\n📄 [1/7] Preparando datos de ejemplo...")

sample_texts = [
    {
        "text": """Machu Picchu es una antigua ciudad inca ubicada en las montañas de los Andes 
        en Perú. Fue construida en el siglo XV y es considerada una de las Nuevas Siete Maravillas 
        del Mundo Moderno. La ciudadela se encuentra a 2,430 metros sobre el nivel del mar y ofrece 
        vistas espectaculares del valle del río Urubamba. Para llegar se puede tomar el tren desde 
        Cusco o hacer el famoso Camino Inca que dura 4 días.""",
        "metadata": {"source": "Cusco_Turismo", "page": 1, "topic": "machu_picchu"}
    },
    {
        "text": """El ceviche es el plato bandera de la gastronomía peruana. Se prepara con pescado 
        fresco marinado en jugo de limón, ají limo, cebolla roja y cilantro. Es un plato refrescante 
        que combina perfectamente los sabores cítricos con el picante característico de la cocina peruana. 
        Los mejores ceviches se encuentran en la costa, especialmente en Lima y el norte del país.""",
        "metadata": {"source": "Gastronomia_Peruana", "page": 1, "topic": "ceviche"}
    },
    {
        "text": """Lima, la capital de Perú, es conocida como la 'Ciudad de los Reyes'. Fue fundada 
        en 1535 por Francisco Pizarro. El centro histórico de Lima es Patrimonio de la Humanidad 
        y alberga magníficas iglesias coloniales, museos y la famosa Plaza de Armas. Destacan el 
        Convento de San Francisco con sus catacumbas, la Catedral de Lima y el Palacio de Gobierno.""",
        "metadata": {"source": "Lima_Info", "page": 1, "topic": "lima_capital"}
    },
    {
        "text": """El Valle Sagrado de los Incas se encuentra cerca de Cusco y es una región rica 
        en sitios arqueológicos. Incluye pueblos como Pisac con su mercado artesanal y fortaleza inca, 
        Ollantaytambo con sus terrazas agrícolas impresionantes, y Chinchero conocido por sus textiles 
        tradicionales. Es un destino imperdible para los amantes de la historia y la cultura andina.""",
        "metadata": {"source": "Cusco_Turismo", "page": 2, "topic": "valle_sagrado"}
    },
    {
        "text": """La papa es un ingrediente fundamental en la cocina peruana. Perú tiene más de 
        3,000 variedades de papa, cada una con sabores y texturas únicos. La causa limeña es un 
        plato frío elaborado con papa amarilla, limón y ají amarillo. El ají de gallina combina 
        papa con una salsa cremosa de ají amarillo y pollo deshilachado. Ambos son íconos de la 
        gastronomía criolla peruana.""",
        "metadata": {"source": "Gastronomia_Peruana", "page": 2, "topic": "papa_cocina"}
    },
    {
        "text": """El Museo Larco en Lima es uno de los museos más importantes del país. Alberga 
        una impresionante colección de arte precolombino con más de 45,000 piezas arqueológicas. 
        Destaca su sala de cerámica erótica y su colección de oro y plata. El museo está ubicado 
        en una mansión virreinal del siglo XVIII rodeada de hermosos jardines.""",
        "metadata": {"source": "Lima_Info", "page": 2, "topic": "museos_lima"}
    },
    {
        "text": """Arequipa, conocida como la Ciudad Blanca por sus construcciones de sillar volcánico, 
        es la segunda ciudad más importante de Perú. Su centro histórico es Patrimonio de la Humanidad. 
        El Monasterio de Santa Catalina es una ciudadela dentro de la ciudad con calles coloridas. 
        Cerca está el Cañón del Colca, uno de los cañones más profundos del mundo donde se pueden 
        observar cóndores en vuelo.""",
        "metadata": {"source": "Arequipa_Turismo", "page": 1, "topic": "arequipa"}
    },
    {
        "text": """El lomo saltado es un plato emblemático que fusiona la cocina china con la peruana. 
        Combina tiras de carne de res salteadas con cebolla, tomate, ají amarillo y papas fritas. 
        Se sirve acompañado de arroz. Este plato es resultado de la inmigración china al Perú en 
        el siglo XIX y representa la fusión culinaria conocida como cocina chifa.""",
        "metadata": {"source": "Gastronomia_Peruana", "page": 3, "topic": "lomo_saltado"}
    }
]

print(f"   ✅ {len(sample_texts)} documentos de ejemplo preparados")

# ============================================================================
# [2/7] LIMPIAR TEXTO
# ============================================================================
print("\n🧹 [2/7] Limpiando y normalizando texto...")

from src.data_pipeline.processors.cleaner import TextCleaner

cleaner = TextCleaner()
cleaned_docs = []

for doc in sample_texts:
    cleaned_text = cleaner.clean(doc["text"])
    cleaned_docs.append({
        "text": cleaned_text,
        "metadata": doc["metadata"]
    })

print(f"   ✅ {len(cleaned_docs)} documentos limpiados")

# ============================================================================
# [3/7] DIVIDIR EN CHUNKS
# ============================================================================
print("\n✂️  [3/7] Dividiendo en chunks semánticos...")

from src.data_pipeline.chunkers.recursive_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20
)

chunks = []
for doc in cleaned_docs:
    doc_chunks = splitter.split_text(doc["text"])
    for i, chunk_text in enumerate(doc_chunks):
        chunks.append({
            "text": chunk_text,
            "metadata": {
                **doc["metadata"],
                "chunk_id": i
            }
        })

print(f"   ✅ Creados {len(chunks)} chunks")

# ============================================================================
# [4/7] GENERAR EMBEDDINGS
# ============================================================================
print("\n🧠 [4/7] Generando embeddings con SentenceTransformer...")
print("   ⏳ Descargando modelo (primera vez puede tardar)...")

from src.embedding_pipeline.models.sentence_transformer import SentenceTransformerEmbedder

# Usar modelo MiniLM que genera embeddings de 384 dimensiones
embedder = SentenceTransformerEmbedder(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    dimension=384  # Especificar dimensión correcta para este modelo
)

chunk_texts = [chunk["text"] for chunk in chunks]
embeddings = embedder.encode_batch(chunk_texts)

# Usar la dimensión real de los embeddings generados
actual_dimension = embeddings[0].shape[0]
print(f"   ✅ Generados {len(embeddings)} embeddings de {actual_dimension} dimensiones")

# ============================================================================
# [5/7] CREAR VECTOR STORE (FAISS)
# ============================================================================
print("\n🗄️  [5/7] Creando vector store con FAISS...")

from src.vector_store.faiss_store import FaissVectorStore

# Usar la dimensión real de los embeddings
vector_store = FaissVectorStore(dimension=actual_dimension)

chunk_ids = [f"chunk_{i}" for i in range(len(chunks))]
metadatas = [chunk["metadata"] for chunk in chunks]

# Agregar el texto a los metadatos para poder recuperarlo después
for i, chunk in enumerate(chunks):
    metadatas[i]["text"] = chunk["text"]

vector_store.add(embeddings, chunk_ids, metadatas)

print(f"   ✅ Vector store creado con {len(embeddings)} vectores")

# ============================================================================
# [6/7] CREAR RETRIEVER
# ============================================================================
print("\n🔍 [6/7] Configurando sistema de recuperación semántica...")

from src.retrieval_pipeline.retrievers.semantic_retriever import SemanticRetriever

retriever = SemanticRetriever(
    embedder=embedder,
    vector_store=vector_store
)

print(f"   ✅ Retriever configurado")

# ============================================================================
# [7/7] CREAR GENERADOR DE RESPUESTAS
# ============================================================================
print("\n🤖 [7/7] Configurando generador de respuestas (LLM)...")

openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    print("   ⚠️  OPENAI_API_KEY no encontrada en .env")
    print("   ℹ️  Modo de prueba: solo se mostrarán chunks recuperados")
    llm = None
    answer_generator = None
else:
    from src.llm import OpenAILLM, OpenAIConfig
    from src.rag import AnswerGenerator
    
    config = OpenAIConfig(
        api_key=openai_key,
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=300
    )
    llm = OpenAILLM(config)
    answer_generator = AnswerGenerator(llm=llm, retriever=retriever)
    print(f"   ✅ LLM configurado: OpenAI GPT-3.5-turbo")

# ============================================================================
# DEMO INTERACTIVA
# ============================================================================
print("\n" + "=" * 70)
print("✅ SISTEMA RAG LISTO - DEMO INTERACTIVA")
print("=" * 70)

example_queries = [
    "¿Qué es Machu Picchu y dónde está ubicado?",
    "¿Cómo se prepara el ceviche peruano?",
    "¿Qué lugares turísticos hay en el Valle Sagrado?",
    "Cuéntame sobre la gastronomía peruana",
    "¿Qué atractivos tiene Lima?"
]

print("\n📝 QUERIES DE EJEMPLO:")
for i, query in enumerate(example_queries, 1):
    print(f"   {i}. {query}")

print("\n" + "-" * 70)

while True:
    print("\n💬 Ingresa tu pregunta sobre turismo en Perú (o 'q' para salir):")
    print("   (o número 1-5 para usar ejemplo, o Enter para ejemplo 1)")
    
    user_input = input(">>> ").strip()
    
    if user_input.lower() == 'q':
        print("\n👋 ¡Hasta luego!")
        break
    
    if not user_input:
        query = example_queries[0]
        print(f"   Usando ejemplo: {query}")
    elif user_input.isdigit() and 1 <= int(user_input) <= len(example_queries):
        query = example_queries[int(user_input) - 1]
        print(f"   Usando ejemplo {user_input}: {query}")
    else:
        query = user_input
    
    print(f"\n🔍 Buscando información relevante...")
    
    retrieved_docs = retriever.retrieve(query, k=3)
    
    print(f"✅ Encontrados {len(retrieved_docs)} chunks relevantes:")
    print("-" * 70)
    
    for i, doc in enumerate(retrieved_docs, 1):
        print(f"\n📄 Chunk {i} (score: {doc['score']:.4f}):")
        print(f"   Fuente: {doc['metadata'].get('source', 'N/A')}")
        # El texto está en metadata
        text = doc['metadata'].get('text', 'N/A')
        print(f"   Texto: {text[:150]}...")
    
    if answer_generator:
        print(f"\n🤖 Generando respuesta con LLM...")
        
        try:
            response = answer_generator.generate_answer(query)
            
            print("\n" + "=" * 70)
            print("💡 RESPUESTA:")
            print("=" * 70)
            print(response.answer)
            
            if response.citations:
                print("\n📚 FUENTES:")
                for i, citation in enumerate(response.citations, 1):
                    print(f"   [{i}] {citation.get('source', 'N/A')}")
            
        except Exception as e:
            print(f"\n❌ Error generando respuesta: {e}")
            print("   ℹ️  Los chunks recuperados se muestran arriba")
    else:
        print("\n💡 Para generar respuestas con LLM, configura OPENAI_API_KEY en .env")
    
    print("\n" + "-" * 70)

print("\n" + "=" * 70)
print("📊 ESTADÍSTICAS DE LA DEMO:")
print("=" * 70)
print(f"   • Documentos de ejemplo: {len(sample_texts)}")
print(f"   • Chunks creados: {len(chunks)}")
print(f"   • Embeddings: {len(embeddings)}")
print(f"   • Dimensión vectorial: {embeddings[0].shape[0]}")
print(f"   • Vector store: FAISS")
print(f"   • Modelo embeddings: paraphrase-multilingual-MiniLM-L12-v2")
if llm:
    print(f"   • LLM: OpenAI GPT-3.5-turbo")
print("=" * 70)
print("\n✨ Demo completada exitosamente!")
