"""
Simplified Integration Test for RAG Pipeline.

This test validates the core RAG workflow with minimal dependencies.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock
import numpy as np
import pytest

from src.vector_store.faiss_store import FaissVectorStore
from src.retrieval_pipeline.retrievers.semantic_retriever import SemanticRetriever
from src.llm import BaseLLM, OpenAIConfig, LLMResponse
from src.rag import AnswerGenerator, RAGResponse


@pytest.fixture
def vector_store():
    """Create in-memory vector store."""
    return FaissVectorStore(dimension=384)


@pytest.fixture
def mock_embedder():
    """Mock embedder for testing."""
    embedder = Mock()
    embedder.dimension = 384
    embedder.model_name = "test-model"
    embedder.get_dimension.return_value = 384  # Add get_dimension method
    
    def encode(text: str) -> np.ndarray:
        hash_val = hash(text) % 1000
        embedding = np.random.RandomState(hash_val).randn(384).astype(np.float32)
        return embedding / np.linalg.norm(embedding)
    
    embedder.encode.side_effect = encode
    return embedder


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    llm = Mock(spec=BaseLLM)
    llm.config = OpenAIConfig(api_key="test", model="gpt-3.5-turbo")
    
    def generate(messages, **kwargs):
        return LLMResponse(
            content="Perú es conocido por su gastronomía excepcional [Source 1]. "
                   "Los platos típicos incluyen ceviche y lomo saltado [Source 2].",
            model="gpt-3.5-turbo",
            usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            finish_reason="stop",
            latency_ms=120.5
        )
    
    llm.generate.side_effect = generate
    return llm


class TestSimplifiedRAGPipeline:
    """Test RAG pipeline with minimal setup."""
    
    def test_end_to_end_workflow(self, vector_store, mock_embedder, mock_llm):
        """Test complete RAG workflow: Store → Retrieve → Generate."""
        print("\n🧪 Testing End-to-End RAG Pipeline")
        
        # Step 1: Vector store ready
        print("\n1. Using in-memory vector store...")
        
        # Step 2: Add sample Peru documents
        print("\n2. Adding sample documents...")
        sample_docs = [
            "La gastronomía peruana es una de las más reconocidas del mundo, combinando ingredientes nativos con influencias internacionales.",
            "El ceviche es el plato bandera del Perú, preparado con pescado fresco marinado en jugo de limón.",
            "Machu Picchu es una ciudadela inca ubicada en Cusco, considerada una de las siete maravillas del mundo moderno.",
            "Cusco fue la capital del Imperio Inca y combina arquitectura colonial con fundaciones incas.",
            "La Amazonía peruana alberga una biodiversidad excepcional y comunidades indígenas.",
        ]
        
        embeddings = np.array([mock_embedder.encode(doc) for doc in sample_docs])
        ids = [f"doc_{i}" for i in range(len(sample_docs))]
        metadata = [{"content": doc, "source": f"test_{i}.txt"} for i, doc in enumerate(sample_docs)]
        
        vector_store.add(ids=ids, embeddings=embeddings, metadatas=metadata)
        print(f"   ✓ Added {len(sample_docs)} documents")
        
        # Step 3: Create retriever
        print("\n3. Creating semantic retriever...")
        retriever = SemanticRetriever(vector_store=vector_store, embedder=mock_embedder)
        
        # Test retrieval
        query = "¿Cuáles son los platos típicos de Perú?"
        print(f"\n   Query: '{query}'")
        results = retriever.retrieve(query, k=3)
        
        assert len(results) > 0, "No retrieval results"
        print(f"   ✓ Retrieved {len(results)} results")
        print(f"     Top score: {results[0]['score']:.4f}")
        
        # Step 4: Create RAG Answer Generator
        print("\n4. Creating RAG answer generator...")
        rag = AnswerGenerator(
            retriever=retriever,
            llm=mock_llm,
            top_k=3,
            temperature=0.7,
            max_tokens=500
        )
        
        # Step 5: Generate answer
        print("\n5. Generating answer...")
        response = rag.generate(query)
        
        # Validate response
        assert isinstance(response, RAGResponse)
        assert response.answer
        assert len(response.sources) > 0
        assert response.query == query
        assert "[Source" in response.answer  # Has citations
        
        print(f"\n   ✓ Answer generated ({len(response.answer)} chars)")
        print(f"     Sources: {len(response.sources)}")
        print(f"     Latency: {response.latency_ms:.2f}ms")
        print(f"\n   Answer: {response.answer[:200]}...")
        
        print("\n✅ End-to-end pipeline test passed!")
    
    def test_multiple_queries(self, vector_store, mock_embedder, mock_llm):
        """Test RAG with multiple different queries."""
        # Vector store already created by fixture
        
        docs = [
            "Perú tiene 3 regiones geográficas: costa, sierra y selva.",
            "Lima es la capital de Perú, ubicada en la costa del Pacífico.",
            "El Inti Raymi es la fiesta del Sol, celebración inca en Cusco.",
        ]
        
        embeddings = np.array([mock_embedder.encode(d) for d in docs])
        vector_store.add(
            ids=[f"d_{i}" for i in range(len(docs))],
            embeddings=embeddings,
            metadatas=[{"content": d} for d in docs]
        )
        
        retriever = SemanticRetriever(embedder=mock_embedder, vector_store=vector_store)
        rag = AnswerGenerator(retriever, mock_llm, top_k=2)
        
        # Test multiple queries
        queries = [
            "¿Cuáles son las regiones de Perú?",
            "¿Dónde está Lima?",
            "¿Qué es el Inti Raymi?",
        ]
        
        for query in queries:
            response = rag.generate(query)
            assert response.answer
            assert len(response.sources) > 0
            print(f"✓ Query: '{query[:40]}...' → {len(response.answer)} chars")
        
        print("\n✅ Multiple queries test passed!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
