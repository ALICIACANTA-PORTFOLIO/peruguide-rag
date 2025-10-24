#!/usr/bin/env python3
"""
Quick Demo: PeruGuide RAG System
================================

Este script demuestra el sistema RAG completo usando un PDF pequeño de turismo.
NO requiere configuración de base de datos - usa solo FAISS en memoria.

Uso:
    python demo_quick.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from src.data_pipeline.loaders.pdf_loader import PDFLoader
from src.data_pipeline.processors.cleaner import TextCleaner
from src.data_pipeline.chunkers.recursive_splitter import RecursiveCharacterTextSplitter
from src.embedding_pipeline.models.sentence_transformer import SentenceTransformerEmbedder
from src.vector_store.faiss_store import FaissVectorStore
from src.retrieval_pipeline.retrievers.semantic_retriever import SemanticRetriever
from src.llm import OpenAILLM, OpenAIConfig
from src.rag import AnswerGenerator


def main():
    """Demo rápida del sistema RAG."""
    
    print("=" * 70)
    print("🇵🇪 PERUGUIDE RAG SYSTEM - DEMO RÁPIDA")
    print("=" * 70)
    
    # ========================================================================
    # 1. CARGAR PDFS DE TURISMO
    # ========================================================================
    print("\n📄 [1/7] Cargando PDFs de turismo de Perú...")
    
    # Buscar todos los PDFs en data/raw/
    data_dir = Path("data/raw")
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ ERROR: No se encontraron PDFs en data/raw/")
        print("\n💡 Copia algunos PDFs a la carpeta data/raw/ primero:")
        print("   Copy-Item 'deleteme\\Complementarios Peru\\*.pdf' data\\raw\\")
        return
    
    print(f"   ✅ Encontrados {len(pdf_files)} PDFs:")
    for pdf in pdf_files:
        size_mb = pdf.stat().st_size / (1024 * 1024)
        print(f"      • {pdf.name} ({size_mb:.2f} MB)")
    
    # Cargar todos los PDFs
    all_documents = []
    
    # Cargar todos los PDFs
    all_documents = []
    
    for pdf_path in pdf_files:
        print(f"   📖 Cargando: {pdf_path.name}...")
        try:
            # Crear loader para cada PDF
            loader = PDFLoader(source_dir=str(data_dir))
            doc = loader.load_single_pdf(pdf_path)
            
            if doc:
                # Convertir el Document a formato esperado (dict con text y metadata)
                doc_dict = {
                    "text": doc.text,
                    "metadata": {
                        **doc.metadata,
                        "source_file": pdf_path.name
                    }
                }
                all_documents.append(doc_dict)
                print(f"      ✅ PDF cargado ({len(doc.text)} caracteres)")
            else:
                print(f"      ⚠️ No se pudo cargar el PDF")
        except Exception as e:
            print(f"      ⚠️ Error: {e}")
    
    documents = all_documents
    print(f"\n   ✅ TOTAL: {len(documents)} PDFs cargados")
    
    # ========================================================================
    # 2. LIMPIAR TEXTO
    # ========================================================================
    print("\n🧹 [2/7] Limpiando y normalizando texto...")
    
    cleaner = TextCleaner()
    cleaned_docs = []
    for doc in documents:
        cleaned_text = cleaner.clean(doc["text"])
        cleaned_docs.append({
            "text": cleaned_text,
            "metadata": doc["metadata"]
        })
    
    print(f"   ✅ Texto limpiado de {len(cleaned_docs)} páginas")
    
    # ========================================================================
    # 3. DIVIDIR EN CHUNKS
    # ========================================================================
    print("\n✂️  [3/7] Dividiendo en chunks semánticos...")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
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
    
    # ========================================================================
    # 4. GENERAR EMBEDDINGS
    # ========================================================================
    print("\n🧠 [4/7] Generando embeddings con SentenceTransformer...")
    
    embedder = SentenceTransformerEmbedder(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    chunk_texts = [chunk["text"] for chunk in chunks]
    embeddings = embedder.encode_batch(chunk_texts)
    
    print(f"   ✅ Generados {len(embeddings)} embeddings de {embeddings[0].shape[0]} dimensiones")
    
    # ========================================================================
    # 5. CREAR VECTOR STORE (FAISS)
    # ========================================================================
    print("\n🗄️  [5/7] Creando vector store con FAISS...")
    
    vector_store = FaissVectorStore(dimension=embeddings[0].shape[0])
    
    # Preparar metadatos y IDs
    chunk_ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [chunk["metadata"] for chunk in chunks]
    
    # Agregar embeddings al vector store
    vector_store.add(embeddings, chunk_ids, metadatas)
    
    print(f"   ✅ Vector store creado con {len(embeddings)} vectores")
    
    # ========================================================================
    # 6. CREAR RETRIEVER
    # ========================================================================
    print("\n🔍 [6/7] Configurando sistema de recuperación semántica...")
    
    retriever = SemanticRetriever(
        embedder=embedder,
        vector_store=vector_store
    )
    
    print(f"   ✅ Retriever configurado")
    
    # ========================================================================
    # 7. CREAR GENERADOR DE RESPUESTAS
    # ========================================================================
    print("\n🤖 [7/7] Configurando generador de respuestas (LLM)...")
    
    # Verificar que tenemos API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("   ⚠️  OPENAI_API_KEY no encontrada en .env")
        print("   ℹ️  Modo de prueba: se mostrarán los chunks recuperados sin generar respuesta")
        llm = None
    else:
        config = OpenAIConfig(
            api_key=openai_key,
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=500
        )
        llm = OpenAILLM(config)
        print(f"   ✅ LLM configurado: OpenAI GPT-3.5-turbo")
    
    if llm:
        answer_generator = AnswerGenerator(llm=llm, retriever=retriever)
        print(f"   ✅ Answer Generator listo")
    else:
        answer_generator = None
    
    # ========================================================================
    # DEMO INTERACTIVA
    # ========================================================================
    print("\n" + "=" * 70)
    print("✅ SISTEMA RAG LISTO - PRUEBAS INTERACTIVAS")
    print("=" * 70)
    
    # Queries de ejemplo
    example_queries = [
        "¿Cuáles son los principales atractivos turísticos de Cusco?",
        "¿Qué platos típicos son famosos en la gastronomía peruana?",
        "Háblame sobre el turismo en Perú y sus destinos principales",
        "¿Qué actividades puedo hacer en Cusco?",
        "¿Cuáles son las características de la cocina peruana?"
    ]
    
    print("\n📝 QUERIES DE EJEMPLO:")
    for i, query in enumerate(example_queries, 1):
        print(f"   {i}. {query}")
    
    print("\n" + "-" * 70)
    
    while True:
        print("\n💬 Ingresa tu pregunta sobre turismo en Perú (o 'q' para salir):")
        print("   (o ingresa un número 1-5 para usar un ejemplo, o Enter para ejemplo 1)")
        
        user_input = input(">>> ").strip()
        
        if user_input.lower() == 'q':
            print("\n👋 ¡Hasta luego!")
            break
        
        # Usar query de ejemplo si está vacío
        if not user_input:
            query = example_queries[0]
            print(f"   Usando ejemplo: {query}")
        elif user_input.isdigit() and 1 <= int(user_input) <= len(example_queries):
            query = example_queries[int(user_input) - 1]
            print(f"   Usando ejemplo {user_input}: {query}")
        else:
            query = user_input
        
        print(f"\n🔍 Buscando información relevante...")
        
        # Recuperar contexto
        retrieved_docs = retriever.retrieve(query, k=5)
        
        print(f"✅ Encontrados {len(retrieved_docs)} chunks relevantes:")
        print("-" * 70)
        
        for i, doc in enumerate(retrieved_docs, 1):
            print(f"\n📄 Chunk {i} (score: {doc['score']:.4f}):")
            print(f"   Página: {doc['metadata'].get('page', 'N/A')}")
            print(f"   Texto: {doc['text'][:200]}...")
        
        if llm and answer_generator:
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
                        print(f"   [{i}] Página {citation.get('page', 'N/A')}")
                
                print(f"\n⏱️  Tiempo: {response.metadata.get('generation_time', 'N/A')}s")
                print(f"🔢 Tokens: {response.metadata.get('total_tokens', 'N/A')}")
                
            except Exception as e:
                print(f"\n❌ Error generando respuesta: {e}")
                print("   ℹ️  Los chunks recuperados se muestran arriba")
        else:
            print("\n💡 Para generar respuestas con LLM, configura OPENAI_API_KEY en .env")
        
        print("\n" + "-" * 70)
    
    print("\n" + "=" * 70)
    print("📊 ESTADÍSTICAS DE LA DEMO:")
    print("=" * 70)
    print(f"   • PDFs procesados: {len(pdf_files)}")
    for pdf in pdf_files:
        print(f"      - {pdf.name}")
    print(f"   • Páginas totales: {len(documents)}")
    print(f"   • Chunks creados: {len(chunks)}")
    print(f"   • Embeddings: {len(embeddings)}")
    print(f"   • Dimensión vectorial: {embeddings[0].shape[0]}")
    print(f"   • Vector store: FAISS")
    print(f"   • Modelo embeddings: paraphrase-multilingual-MiniLM-L12-v2")
    if llm:
        print(f"   • LLM: {llm.__class__.__name__}")
    print("=" * 70)


if __name__ == "__main__":
    main()
