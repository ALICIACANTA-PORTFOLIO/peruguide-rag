"""
Integration test for the complete RAG pipeline.

This test validates the entire system workflow:
1. Load PDF document about Peru
2. Process and clean text
3. Chunk into manageable pieces
4. Generate embeddings
5. Store in vector database
6. Perform semantic retrieval
7. Generate answers with LLM
8. Validate citations and answer quality
"""

import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, patch

import pytest
import numpy as np

from src.data_pipeline.loaders.pdf_loader import PDFLoader
from src.data_pipeline.processors.cleaner import TextCleaner
from src.data_pipeline.processors.metadata_extractor import MetadataExtractor
from src.data_pipeline.chunkers.recursive_splitter import RecursiveCharacterTextSplitter
from src.embedding_pipeline.models.sentence_transformer import SentenceTransformerEmbedder
from src.embedding_pipeline.batch_processor import BatchEmbeddingProcessor
from src.vector_store.faiss_store import FaissVectorStore
from src.retrieval_pipeline.retrievers.semantic_retriever import SemanticRetriever
from src.llm import BaseLLM, OpenAIConfig, LLMResponse, Message
from src.rag import AnswerGenerator, RAGResponse


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def test_pdf_path() -> Path:
    """Path to a small Peru guide PDF for testing."""
    base_path = Path(__file__).parent.parent.parent
    pdf_path = base_path / "Complementarios Peru" / "Gastronomia_Peruana.pdf"
    
    if not pdf_path.exists():
        # Fallback to another PDF if Gastronomia doesn't exist
        pdf_path = base_path / "Complementarios Peru" / "informacion-Peru.pdf"
    
    assert pdf_path.exists(), f"Test PDF not found at {pdf_path}"
    return pdf_path


@pytest.fixture
def temp_vector_store_path():
    """Create a temporary directory for the vector store."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def pdf_loader():
    """Initialize PDF loader with Peru documents directory."""
    base_path = Path(__file__).parent.parent.parent
    source_dir = base_path / "Complementarios Peru"
    assert source_dir.exists(), f"Peru documents directory not found: {source_dir}"
    return PDFLoader(source_dir=str(source_dir))


@pytest.fixture
def text_processors():
    """Initialize text processors."""
    return [TextCleaner(), MetadataExtractor()]


@pytest.fixture
def chunker():
    """Initialize text chunker."""
    return RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " "]
    )


@pytest.fixture
def mock_embedder():
    """Mock embedder that returns deterministic embeddings."""
    embedder = Mock(spec=SentenceTransformerEmbedder)
    embedder.dimension = 384
    embedder.model_name = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Return consistent embeddings for reproducibility
    def mock_encode(text: str) -> np.ndarray:
        # Simple hash-based embedding for testing
        hash_val = hash(text) % 1000
        embedding = np.random.RandomState(hash_val).randn(384).astype(np.float32)
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)
        return embedding
    
    def mock_encode_batch(texts: List[str]) -> np.ndarray:
        return np.array([mock_encode(text) for text in texts])
    
    embedder.encode.side_effect = mock_encode
    embedder.encode_batch.side_effect = mock_encode_batch
    
    return embedder


@pytest.fixture
def mock_llm():
    """Mock LLM that returns Peru-related answers."""
    llm = Mock(spec=BaseLLM)
    llm.config = OpenAIConfig(api_key="test-key", model="gpt-3.5-turbo")
    
    def mock_generate(messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        # Extract query from messages
        user_message = next((m for m in messages if m["role"] == "user"), None)
        query_text = user_message["content"] if user_message else ""
        
        # Generate contextual answer based on query
        if "gastronomía" in query_text.lower() or "comida" in query_text.lower():
            answer = (
                "La gastronomía peruana es reconocida mundialmente por su diversidad "
                "y sabor único [Source 1]. Entre los platos más emblemáticos se encuentran "
                "el ceviche, el lomo saltado y el ají de gallina [Source 2]. La cocina peruana "
                "combina influencias indígenas, españolas, africanas y asiáticas [Source 3]."
            )
        elif "machu picchu" in query_text.lower():
            answer = (
                "Machu Picchu es una antigua ciudadela inca ubicada en Cusco [Source 1]. "
                "Fue construida en el siglo XV y es considerada una de las nuevas siete "
                "maravillas del mundo moderno [Source 2]. Se encuentra a 2,430 metros "
                "sobre el nivel del mar [Source 3]."
            )
        elif "cusco" in query_text.lower():
            answer = (
                "Cusco fue la capital del Imperio Inca [Source 1]. La ciudad combina "
                "arquitectura colonial española con fundaciones incas [Source 2]. Es el "
                "punto de partida para visitar Machu Picchu [Source 3]."
            )
        else:
            answer = (
                "Perú es un país ubicado en América del Sur con una rica historia y cultura "
                "[Source 1]. Es conocido por sus sitios arqueológicos incas, su biodiversidad "
                "amazónica y su gastronomía de clase mundial [Source 2]."
            )
        
        return LLMResponse(
            content=answer,
            model="gpt-3.5-turbo",
            usage={"prompt_tokens": 150, "completion_tokens": 80, "total_tokens": 230},
            finish_reason="stop"
        )
    
    llm.generate.side_effect = mock_generate
    llm.get_model_info.return_value = {"model": "gpt-3.5-turbo", "provider": "openai"}
    
    return llm


# ============================================================================
# Integration Tests
# ============================================================================

class TestFullRAGPipeline:
    """Test the complete end-to-end RAG pipeline."""
    
    def test_pipeline_with_small_document(
        self,
        test_pdf_path: Path,
        temp_vector_store_path: Path,
        pdf_loader: PDFLoader,
        text_processors: List,
        chunker: RecursiveCharacterTextSplitter,
        mock_embedder,
        mock_llm
    ):
        """
        Test complete pipeline: Load → Process → Chunk → Embed → Store → Retrieve → Generate.
        """
        # Step 1: Load PDF
        print(f"\n1. Loading PDF: {test_pdf_path.name}")
        document = pdf_loader.load_single_pdf(test_pdf_path)
        assert document is not None, "Failed to load PDF"
        documents = [document]  # Wrap in list for compatibility
        print(f"   ✓ Loaded {len(documents)} document(s)")
        
        # Step 2: Process documents
        print("\n2. Processing documents...")
        for processor in text_processors:
            documents = [processor.process(doc) for doc in documents]
        print(f"   ✓ Processed {len(documents)} documents")
        
        # Step 3: Chunk documents
        print("\n3. Chunking documents...")
        all_chunks = []
        for doc in documents:
            chunks = chunker.split(doc)
            all_chunks.extend(chunks)
        
        assert len(all_chunks) > 0, "No chunks created"
        print(f"   ✓ Created {len(all_chunks)} chunks")
        
        # Limit to first 20 chunks for faster testing
        test_chunks = all_chunks[:20]
        print(f"   ✓ Using {len(test_chunks)} chunks for testing")
        
        # Step 4: Generate embeddings
        print("\n4. Generating embeddings...")
        batch_processor = BatchEmbeddingProcessor(
            embedder=mock_embedder,
            batch_size=8
        )
        
        texts = [chunk.content for chunk in test_chunks]
        embeddings = batch_processor.process_batch(texts)
        
        assert embeddings.shape[0] == len(test_chunks), "Embedding count mismatch"
        assert embeddings.shape[1] == 384, "Incorrect embedding dimension"
        print(f"   ✓ Generated embeddings: {embeddings.shape}")
        
        # Step 5: Store in vector database
        print("\n5. Storing in vector database...")
        vector_store = FaissVectorStore(
            dimension=384,
            index_path=str(temp_vector_store_path / "test_index.faiss")
        )
        
        # Add documents to store
        ids = [chunk.id for chunk in test_chunks]
        metadatas = [chunk.metadata for chunk in test_chunks]
        
        vector_store.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        stored_count = vector_store.count()
        assert stored_count == len(test_chunks), f"Expected {len(test_chunks)} docs, got {stored_count}"
        print(f"   ✓ Stored {stored_count} documents")
        
        # Step 6: Perform semantic retrieval
        print("\n6. Testing semantic retrieval...")
        retriever = SemanticRetriever(
            vector_store=vector_store,
            embedder=mock_embedder
        )
        
        # Test queries
        test_queries = [
            "¿Cuáles son los platos típicos de Perú?",
            "¿Qué ingredientes se usan en la cocina peruana?",
            "¿Cuál es la historia de la gastronomía peruana?"
        ]
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            results = retriever.retrieve(query=query, k=3)
            
            assert len(results) > 0, f"No results for query: {query}"
            assert len(results) <= 3, "Too many results returned"
            
            # Validate result structure
            for result in results:
                assert "id" in result, "Missing 'id' in result"
                assert "score" in result, "Missing 'score' in result"
                assert "metadata" in result, "Missing 'metadata' in result"
                assert 0.0 <= result["score"] <= 1.0, f"Invalid score: {result['score']}"
            
            print(f"   ✓ Retrieved {len(results)} results")
            print(f"     Top score: {results[0]['score']:.4f}")
        
        # Step 7: Generate answers with RAG
        print("\n7. Testing RAG answer generation...")
        rag = AnswerGenerator(
            retriever=retriever,
            llm=mock_llm,
            top_k=3,
            temperature=0.7,
            max_tokens=500
        )
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            response = rag.generate(query)
            
            # Validate response structure
            assert isinstance(response, RAGResponse), "Invalid response type"
            assert response.answer, "Empty answer"
            assert len(response.sources) > 0, "No sources provided"
            assert response.query == query, "Query mismatch"
            assert response.model, "No model info"
            
            # Validate citations in answer
            assert "[Source" in response.answer, "No citations in answer"
            
            # Validate latency metrics
            assert response.latency_ms is not None, "Missing total latency"
            assert response.retrieval_latency_ms is not None, "Missing retrieval latency"
            assert response.generation_latency_ms is not None, "Missing generation latency"
            
            print(f"   ✓ Generated answer ({len(response.answer)} chars)")
            print(f"     Sources: {len(response.sources)}")
            print(f"     Latency: {response.latency_ms:.2f}ms")
            print(f"     Answer preview: {response.answer[:100]}...")
        
        print("\n✅ Full pipeline test completed successfully!")
    
    def test_pipeline_streaming(
        self,
        test_pdf_path: Path,
        temp_vector_store_path: Path,
        pdf_loader: PDFLoader,
        text_processors: List,
        chunker: RecursiveCharacterTextSplitter,
        mock_embedder,
        mock_llm
    ):
        """Test streaming answers through the pipeline."""
        # Setup (same as previous test, but abbreviated)
        print("\n🔄 Testing streaming pipeline...")
        
        # Load and process (simplified)
        document = pdf_loader.load_single_pdf(test_pdf_path)
        assert document is not None, "Failed to load PDF"
        documents = [document]
        for processor in text_processors:
            documents = [processor.process(doc) for doc in documents]
        
        all_chunks = []
        for doc in documents:
            chunks = chunker.split(doc)
            all_chunks.extend(chunks)
        
        test_chunks = all_chunks[:10]  # Fewer chunks for speed
        
        # Embed and store
        batch_processor = BatchEmbeddingProcessor(embedder=mock_embedder, batch_size=8)
        texts = [chunk.content for chunk in test_chunks]
        embeddings = batch_processor.process_batch(texts)
        
        vector_store = FaissVectorStore(
            dimension=384,
            index_path=str(temp_vector_store_path / "stream_test.faiss")
        )
        
        ids = [chunk.id for chunk in test_chunks]
        metadatas = [chunk.metadata for chunk in test_chunks]
        vector_store.add(ids=ids, embeddings=embeddings, metadatas=metadatas)
        
        # Create RAG with streaming
        retriever = SemanticRetriever(vector_store=vector_store, embedder=mock_embedder)
        
        # Mock streaming
        def mock_stream(messages, **kwargs):
            response = mock_llm.generate(messages, **kwargs)
            words = response.content.split()
            for word in words:
                from src.llm import StreamChunk
                yield StreamChunk(content=word + " ", finish_reason=None)
            yield StreamChunk(content="", finish_reason="stop")
        
        mock_llm.stream.side_effect = mock_stream
        
        rag = AnswerGenerator(
            retriever=retriever,
            llm=mock_llm,
            top_k=3
        )
        
        # Test streaming
        query = "¿Qué es la gastronomía peruana?"
        print(f"\nQuery: '{query}'")
        print("Streaming: ", end="")
        
        chunks_received = 0
        final_response = None
        
        for chunk, final in rag.stream(query):
            if final is None:
                print(chunk, end="", flush=True)
                chunks_received += 1
            else:
                final_response = final
        
        print()  # New line after streaming
        
        assert chunks_received > 0, "No chunks received"
        assert final_response is not None, "No final response"
        assert isinstance(final_response, RAGResponse), "Invalid final response type"
        assert len(final_response.sources) > 0, "No sources in final response"
        
        print(f"\n✓ Received {chunks_received} chunks")
        print(f"✓ Final response with {len(final_response.sources)} sources")
        print("\n✅ Streaming test completed successfully!")


class TestPipelineEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_query(
        self,
        temp_vector_store_path: Path,
        mock_embedder,
        mock_llm
    ):
        """Test handling of empty queries."""
        vector_store = FaissVectorStore(
            dimension=384,
            index_path=str(temp_vector_store_path / "empty_test.faiss")
        )
        
        # Add dummy data
        dummy_embeddings = np.random.randn(5, 384).astype(np.float32)
        dummy_ids = [f"doc_{i}" for i in range(5)]
        dummy_metadata = [{"content": f"Content {i}"} for i in range(5)]
        
        vector_store.add(ids=dummy_ids, embeddings=dummy_embeddings, metadatas=dummy_metadata)
        
        retriever = SemanticRetriever(vector_store=vector_store, embedder=mock_embedder)
        rag = AnswerGenerator(retriever=retriever, llm=mock_llm, top_k=3)
        
        # Empty query should still work (LLM handles validation)
        with pytest.raises(ValueError, match="empty"):
            rag.generate("")
    
    def test_no_retrieval_results(
        self,
        temp_vector_store_path: Path,
        mock_embedder,
        mock_llm
    ):
        """Test when retrieval returns no results."""
        vector_store = FaissVectorStore(
            dimension=384,
            index_path=str(temp_vector_store_path / "no_results_test.faiss")
        )
        
        # Empty vector store
        retriever = SemanticRetriever(vector_store=vector_store, embedder=mock_embedder)
        rag = AnswerGenerator(retriever=retriever, llm=mock_llm, top_k=3)
        
        # Should handle gracefully with no context
        response = rag.generate("Test query")
        assert response.answer  # LLM should generate something
        assert len(response.sources) == 0  # No sources available


# ============================================================================
# Performance Tests
# ============================================================================

class TestPipelinePerformance:
    """Test pipeline performance metrics."""
    
    def test_latency_tracking(
        self,
        temp_vector_store_path: Path,
        mock_embedder,
        mock_llm
    ):
        """Verify latency metrics are tracked correctly."""
        vector_store = FaissVectorStore(
            dimension=384,
            index_path=str(temp_vector_store_path / "latency_test.faiss")
        )
        
        # Add test data
        embeddings = np.random.randn(10, 384).astype(np.float32)
        ids = [f"doc_{i}" for i in range(10)]
        metadata = [{"content": f"Test content {i}"} for i in range(10)]
        
        vector_store.add(ids=ids, embeddings=embeddings, metadatas=metadata)
        
        retriever = SemanticRetriever(vector_store=vector_store, embedder=mock_embedder)
        rag = AnswerGenerator(retriever=retriever, llm=mock_llm, top_k=3)
        
        # Generate answer
        response = rag.generate("Test query")
        
        # Validate latency metrics exist
        assert response.latency_ms is not None
        assert response.retrieval_latency_ms is not None
        assert response.generation_latency_ms is not None
        
        # Validate latency values are reasonable
        assert response.latency_ms > 0
        assert response.retrieval_latency_ms > 0
        assert response.generation_latency_ms > 0
        
        # Total should be sum of parts (with small tolerance for overhead)
        assert response.latency_ms >= (
            response.retrieval_latency_ms + response.generation_latency_ms
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
