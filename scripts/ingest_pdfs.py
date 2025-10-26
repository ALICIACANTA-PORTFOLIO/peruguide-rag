"""
Script to ingest PDF documents into the vector store.

This script:
1. Loads PDFs from data/raw/ directory
2. Processes and cleans the text
3. Chunks documents into manageable pieces
4. Generates embeddings
5. Stores in FAISS vector store
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import structlog

from src.data_pipeline.loaders.pdf_loader import PDFLoader
from src.data_pipeline.processors.cleaner import TextCleaner
from src.data_pipeline.chunkers.recursive_splitter import RecursiveCharacterTextSplitter
from src.embedding_pipeline.models.sentence_transformer import SentenceTransformerEmbedder
from src.vector_store.faiss_store import FaissVectorStore

logger = structlog.get_logger(__name__)


def main():
    """Main ingestion pipeline."""
    print("\n" + "="*70)
    print("📚 PERUGUIDE RAG - PDF INGESTION PIPELINE")
    print("="*70 + "\n")
    
    # ========================================================================
    # 1. SETUP PATHS
    # ========================================================================
    print("📂 [1/6] Setting up paths...")
    
    data_dir = project_root / "data" / "raw"
    vector_store_dir = project_root / "data" / "vector_stores"
    vector_store_path = vector_store_dir / "faiss_peru_guide.index"
    
    # Create directories if they don't exist
    vector_store_dir.mkdir(parents=True, exist_ok=True)
    
    if not data_dir.exists():
        print(f"   ❌ Error: Data directory not found: {data_dir}")
        print(f"   💡 Expected directory: 'Complementarios Peru' with PDF files")
        return
    
    print(f"   ✅ Data directory: {data_dir}")
    print(f"   ✅ Vector store path: {vector_store_path}")
    
    # ========================================================================
    # 2. LOAD PDFs
    # ========================================================================
    print("\n📖 [2/6] Loading PDF documents...")
    
    loader = PDFLoader(source_dir=str(data_dir), recursive=True)
    pdf_files = loader.find_pdf_files()
    
    print(f"   Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files[:5]:  # Show first 5
        size_mb = pdf.stat().st_size / (1024 * 1024)
        print(f"      • {pdf.name} ({size_mb:.2f} MB)")
    if len(pdf_files) > 5:
        print(f"      ... and {len(pdf_files) - 5} more")
    
    # Load all documents
    documents = loader.load_documents()
    
    if not documents:
        print(f"   ❌ No documents loaded. Check PDF files.")
        return
    
    total_chars = sum(len(doc.text) for doc in documents)
    print(f"   ✅ Loaded {len(documents)} documents ({total_chars:,} characters)")
    
    # ========================================================================
    # 3. CLEAN TEXT
    # ========================================================================
    print("\n🧹 [3/6] Cleaning text...")
    
    cleaner = TextCleaner()
    cleaned_docs = []
    
    for doc in documents:
        # Clean the text content
        cleaned_text_content = cleaner.clean(doc.text)
        
        # Create new document with cleaned text
        from src.data_pipeline.loaders.pdf_loader import Document
        cleaned_doc = Document(
            text=cleaned_text_content,
            metadata=doc.metadata
        )
        cleaned_docs.append(cleaned_doc)
    
    print(f"   ✅ Cleaned {len(cleaned_docs)} documents")
    
    # ========================================================================
    # 4. CHUNK DOCUMENTS
    # ========================================================================
    print("\n✂️  [4/6] Chunking documents...")
    
    chunker = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    all_chunks = []
    for doc in cleaned_docs:
        # Use split_with_metadata which returns Chunk objects
        chunks = chunker.split_with_metadata(
            text=doc.text,
            metadata=doc.metadata
        )
        all_chunks.extend(chunks)
    
    print(f"   ✅ Created {len(all_chunks)} chunks")
    if all_chunks:
        avg_size = sum(len(c['chunk_text']) for c in all_chunks) // len(all_chunks)
        print(f"   📊 Average chunk size: {avg_size} chars")
    
    # ========================================================================
    # 5. GENERATE EMBEDDINGS
    # ========================================================================
    print("\n🧠 [5/6] Generating embeddings...")
    print("   ⏳ Loading embedding model (this may take a moment)...")
    
    embedder = SentenceTransformerEmbedder(
        model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        device="cpu"
    )
    
    print(f"   📐 Model loaded: {embedder.dimension} dimensions")
    print(f"   🔄 Encoding {len(all_chunks)} chunks...")
    
    # Encode in batches
    chunk_texts = [chunk['chunk_text'] for chunk in all_chunks]
    embeddings = embedder.encode_batch(chunk_texts)
    
    print(f"   ✅ Generated {len(embeddings)} embeddings")
    
    # ========================================================================
    # 6. STORE IN VECTOR DATABASE
    # ========================================================================
    print("\n🗄️  [6/6] Storing in FAISS vector store...")
    
    # Initialize vector store
    vector_store = FaissVectorStore(dimension=embedder.dimension)
    
    # Prepare data
    chunk_ids = [chunk['chunk_id'] for chunk in all_chunks]
    metadatas = [{k: v for k, v in chunk.items() if k != 'chunk_text'} for chunk in all_chunks]
    
    # Add to vector store
    vector_store.add(
        ids=chunk_ids,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
    # Save to disk
    vector_store.persist(str(vector_store_path))
    
    print(f"   ✅ Stored {len(vector_store)} vectors")
    print(f"   💾 Saved to: {vector_store_path}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*70)
    print("✅ INGESTION COMPLETE!")
    print("="*70)
    print(f"📊 Summary:")
    print(f"   • PDFs processed:    {len(documents)}")
    print(f"   • Chunks created:    {len(all_chunks)}")
    print(f"   • Embeddings stored: {len(vector_store)}")
    print(f"   • Vector dimension:  {embedder.dimension}")
    print(f"   • Index saved to:    {vector_store_path}")
    print("\n💡 Next steps:")
    print("   1. Restart the API server: uvicorn src.api.main:app --reload")
    print("   2. Open Streamlit: streamlit run app/streamlit_app.py")
    print("   3. Ask questions about Peru!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
