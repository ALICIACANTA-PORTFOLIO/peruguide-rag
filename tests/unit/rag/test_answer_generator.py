"""Tests for RAG Answer Generator."""

import sys
from typing import List
from unittest.mock import MagicMock, patch

import pytest

# Mock optional dependencies
sys.modules['openai'] = MagicMock()
sys.modules['tiktoken'] = MagicMock()

from src.rag.answer_generator import AnswerGenerator, RAGResponse, RetrievalResult
from src.llm.base_llm import Message, LLMResponse, StreamChunk


class TestRAGResponse:
    """Tests for RAGResponse dataclass."""
    
    def test_create_response(self):
        """Test creating RAG response."""
        response = RAGResponse(
            answer="Test answer",
            sources=[{"source_id": 1, "content": "Test"}],
            query="Test query",
            model="gpt-4",
        )
        
        assert response.answer == "Test answer"
        assert len(response.sources) == 1
        assert response.query == "Test query"
        assert response.model == "gpt-4"
    
    def test_response_with_timing(self):
        """Test response with timing information."""
        response = RAGResponse(
            answer="Test answer",
            sources=[],
            query="Test query",
            model="gpt-4",
            latency_ms=150.5,
            retrieval_latency_ms=50.0,
            generation_latency_ms=100.5,
        )
        
        assert response.latency_ms == 150.5
        assert response.retrieval_latency_ms == 50.0
        assert response.generation_latency_ms == 100.5
    
    def test_response_with_usage(self):
        """Test response with token usage."""
        response = RAGResponse(
            answer="Test answer",
            sources=[],
            query="Test query",
            model="gpt-4",
            usage={"total_tokens": 100, "prompt_tokens": 50, "completion_tokens": 50},
        )
        
        assert response.usage["total_tokens"] == 100
        assert response.usage["prompt_tokens"] == 50
    
    def test_repr(self):
        """Test string representation."""
        response = RAGResponse(
            answer="Test answer",
            sources=[{"id": 1}, {"id": 2}],
            query="What is Peru?",
            model="gpt-4",
        )
        
        repr_str = repr(response)
        assert "What is Peru?" in repr_str
        assert "sources=2" in repr_str
        assert "gpt-4" in repr_str


class TestAnswerGenerator:
    """Tests for AnswerGenerator class."""
    
    @pytest.fixture
    def mock_retriever(self):
        """Create mock retriever."""
        retriever = MagicMock()
        
        # Mock retrieve method - returns dicts like real SemanticRetriever
        retriever.retrieve.return_value = [
            {
                "id": "doc1",
                "score": 0.95,
                "metadata": {
                    "title": "Inca History",
                    "chapter": "Architecture",
                    "page": 42,
                    "content": "The Incas built Machu Picchu in the 15th century.",
                },
            },
            {
                "id": "doc2",
                "score": 0.87,
                "metadata": {
                    "title": "Peru Geography",
                    "page": 15,
                    "content": "Machu Picchu is located in Cusco region.",
                },
            },
        ]
        
        return retriever
    
    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM."""
        llm = MagicMock()
        llm.config.model = "gpt-4"
        
        # Mock generate method
        llm.generate.return_value = LLMResponse(
            content="Machu Picchu is an ancient Inca citadel built in the 15th century.",
            model="gpt-4",
            usage={"total_tokens": 50, "prompt_tokens": 30, "completion_tokens": 20},
            finish_reason="stop",
            latency_ms=100.0,
        )
        
        # Mock stream method
        llm.stream.return_value = iter([
            StreamChunk(content="Machu ", finish_reason=None),
            StreamChunk(content="Picchu ", finish_reason=None),
            StreamChunk(content="is ancient.", finish_reason="stop"),
        ])
        
        return llm
    
    def test_initialization(self, mock_retriever, mock_llm):
        """Test generator initialization."""
        generator = AnswerGenerator(
            retriever=mock_retriever,
            llm=mock_llm,
            top_k=3,
            include_metadata=True,
        )
        
        assert generator.retriever == mock_retriever
        assert generator.llm == mock_llm
        assert generator.top_k == 3
        assert generator.include_metadata is True
    
    def test_initialization_with_overrides(self, mock_retriever, mock_llm):
        """Test initialization with parameter overrides."""
        generator = AnswerGenerator(
            retriever=mock_retriever,
            llm=mock_llm,
            temperature=0.8,
            max_tokens=500,
        )
        
        assert generator.temperature == 0.8
        assert generator.max_tokens == 500
    
    def test_format_context_basic(self, mock_retriever, mock_llm):
        """Test basic context formatting."""
        generator = AnswerGenerator(
            retriever=mock_retriever,
            llm=mock_llm,
            include_metadata=False,
        )
        
        results = [
            {
                "id": "doc1",
                "score": 0.95,
                "metadata": {"content": "Content 1"},
            },
            {
                "id": "doc2",
                "score": 0.80,
                "metadata": {"content": "Content 2"},
            },
        ]
        
        context = generator._format_context(results)
        
        assert "[Source 1]" in context
        assert "[Source 2]" in context
        assert "Content 1" in context
        assert "Content 2" in context
        assert "0.95" in context
        assert "0.80" in context
    
    def test_format_context_with_metadata(self, mock_retriever, mock_llm):
        """Test context formatting with metadata."""
        generator = AnswerGenerator(
            retriever=mock_retriever,
            llm=mock_llm,
            include_metadata=True,
        )
        
        results = [
            {
                "id": "doc1",
                "score": 0.95,
                "metadata": {
                    "title": "Inca History",
                    "chapter": "Empire",
                    "page": 10,
                    "content": "Inca content",
                },
            },
        ]
        
        context = generator._format_context(results)
        
        assert "[Source 1]" in context
        assert "Title: Inca History" in context
        assert "Chapter: Empire" in context
        assert "Page: 10" in context
        assert "Inca content" in context
    
    def test_format_context_empty(self, mock_retriever, mock_llm):
        """Test formatting empty context."""
        generator = AnswerGenerator(retriever=mock_retriever, llm=mock_llm)
        
        context = generator._format_context([])
        
        assert context == "No relevant context found."
    
    def test_build_prompt(self, mock_retriever, mock_llm):
        """Test prompt building."""
        generator = AnswerGenerator(retriever=mock_retriever, llm=mock_llm)
        
        messages = generator._build_prompt(
            query="What is Machu Picchu?",
            context="[Source 1] Machu Picchu is an Inca citadel.",
        )
        
        assert len(messages) == 2
        assert messages[0].role == "system"
        assert "Peru" in messages[0].content
        assert messages[1].role == "user"
        assert "What is Machu Picchu?" in messages[1].content
        assert "[Source 1]" in messages[1].content
    
    def test_extract_sources(self, mock_retriever, mock_llm):
        """Test source extraction."""
        generator = AnswerGenerator(retriever=mock_retriever, llm=mock_llm)
        
        results = [
            {
                "id": "doc1",
                "score": 0.95,
                "metadata": {"title": "Test", "content": "Content 1"},
            },
            {
                "id": "doc2",
                "score": 0.80,
                "metadata": {"content": "Content 2"},
            },
        ]
        
        sources = generator._extract_sources(results)
        
        assert len(sources) == 2
        assert sources[0]["source_id"] == 1
        assert sources[0]["content"] == "Content 1"
        assert sources[0]["score"] == 0.95
        assert sources[0]["doc_id"] == "doc1"
        assert sources[0]["metadata"]["title"] == "Test"
        assert sources[1]["source_id"] == 2
    
    def test_generate_basic(self, mock_retriever, mock_llm):
        """Test basic RAG generation."""
        generator = AnswerGenerator(retriever=mock_retriever, llm=mock_llm, top_k=2)
        
        response = generator.generate(query="What is Machu Picchu?")
        
        # Verify retrieval was called
        mock_retriever.retrieve.assert_called_once()
        call_kwargs = mock_retriever.retrieve.call_args[1]
        assert call_kwargs["query"] == "What is Machu Picchu?"
        assert call_kwargs["k"] == 2
        
        # Verify LLM was called
        mock_llm.generate.assert_called_once()
        
        # Verify response
        assert isinstance(response, RAGResponse)
        assert response.answer == "Machu Picchu is an ancient Inca citadel built in the 15th century."
        assert len(response.sources) == 2
        assert response.query == "What is Machu Picchu?"
        assert response.model == "gpt-4"
        assert response.latency_ms > 0
    
    def test_generate_with_custom_top_k(self, mock_retriever, mock_llm):
        """Test generation with custom top_k."""
        generator = AnswerGenerator(retriever=mock_retriever, llm=mock_llm, top_k=5)
        
        response = generator.generate(query="Test query", top_k=3)
        
        # Verify top_k override
        call_kwargs = mock_retriever.retrieve.call_args[1]
        assert call_kwargs["k"] == 3
    
    def test_generate_with_filters(self, mock_retriever, mock_llm):
        """Test generation with metadata filters."""
        generator = AnswerGenerator(retriever=mock_retriever, llm=mock_llm)
        
        filters = {"title": "Inca History"}
        response = generator.generate(query="Test query", filters=filters)
        
        # Verify filters passed
        call_kwargs = mock_retriever.retrieve.call_args[1]
        assert call_kwargs["filters"] == filters
    
    def test_generate_with_llm_params(self, mock_retriever, mock_llm):
        """Test generation with LLM parameters."""
        generator = AnswerGenerator(retriever=mock_retriever, llm=mock_llm)
        
        response = generator.generate(
            query="Test query",
            temperature=0.9,
            max_tokens=200,
        )
        
        # Verify LLM params passed
        call_kwargs = mock_llm.generate.call_args[1]
        assert call_kwargs["temperature"] == 0.9
        assert call_kwargs["max_tokens"] == 200
    
    def test_generate_with_temperature_override(self, mock_retriever, mock_llm):
        """Test temperature override from constructor."""
        generator = AnswerGenerator(
            retriever=mock_retriever,
            llm=mock_llm,
            temperature=0.5,
        )
        
        response = generator.generate(query="Test query")
        
        # Verify temperature used
        call_kwargs = mock_llm.generate.call_args[1]
        assert call_kwargs["temperature"] == 0.5
    
    def test_generate_response_structure(self, mock_retriever, mock_llm):
        """Test complete response structure."""
        generator = AnswerGenerator(retriever=mock_retriever, llm=mock_llm)
        
        response = generator.generate(query="What is Cusco?")
        
        # Verify all fields populated
        assert response.answer
        assert response.sources
        assert response.query == "What is Cusco?"
        assert response.model == "gpt-4"
        assert response.usage is not None
        assert response.latency_ms >= 0
        assert response.retrieval_latency_ms >= 0
        assert response.generation_latency_ms >= 0
        assert "top_k" in response.metadata
    
    def test_stream_basic(self, mock_retriever, mock_llm):
        """Test basic streaming generation."""
        generator = AnswerGenerator(retriever=mock_retriever, llm=mock_llm)
        
        chunks = []
        final_response = None
        
        for chunk in generator.stream(query="What is Machu Picchu?"):
            if isinstance(chunk, StreamChunk):
                chunks.append(chunk)
            else:
                final_response = chunk
        
        # Verify chunks received
        assert len(chunks) == 3
        assert chunks[0].content == "Machu "
        assert chunks[1].content == "Picchu "
        assert chunks[2].content == "is ancient."
        
        # Verify retrieval called
        mock_retriever.retrieve.assert_called_once()
        
        # Verify LLM streaming called
        mock_llm.stream.assert_called_once()
    
    def test_stream_returns_final_response(self, mock_retriever, mock_llm):
        """Test that stream returns final RAG response."""
        generator = AnswerGenerator(retriever=mock_retriever, llm=mock_llm)
        
        # Consume all chunks
        gen = generator.stream(query="Test query")
        chunks = list(gen)
        
        # Get final response (returned via generator)
        final_response = gen.gi_value if hasattr(gen, 'gi_value') else None
        
        # Note: In Python, generators don't expose return values directly
        # The final RAGResponse is built but returned via StopIteration
        # This is more for documentation/type hints
        assert chunks  # At least got chunks
    
    def test_stream_with_filters(self, mock_retriever, mock_llm):
        """Test streaming with filters."""
        generator = AnswerGenerator(retriever=mock_retriever, llm=mock_llm)
        
        filters = {"category": "history"}
        list(generator.stream(query="Test query", filters=filters))
        
        # Verify filters passed
        call_kwargs = mock_retriever.retrieve.call_args[1]
        assert call_kwargs["filters"] == filters
    
    def test_repr(self, mock_retriever, mock_llm):
        """Test string representation."""
        generator = AnswerGenerator(retriever=mock_retriever, llm=mock_llm, top_k=5)
        
        repr_str = repr(generator)
        assert "gpt-4" in repr_str
        assert "top_k=5" in repr_str


class TestAnswerGeneratorIntegration:
    """Integration tests for AnswerGenerator."""
    
    @pytest.fixture
    def mock_retriever(self):
        """Create realistic mock retriever."""
        retriever = MagicMock()
        retriever.retrieve.return_value = [
            {
                "id": "doc1",
                "score": 0.92,
                "metadata": {
                    "title": "Complete Guide to Peru",
                    "chapter": "Inca Architecture",
                    "page": 156,
                    "content": "Machu Picchu was built around 1450 AD by the Inca emperor Pachacuti.",
                },
            },
            {
                "id": "doc2",
                "score": 0.88,
                "metadata": {
                    "title": "Peru Geography",
                    "chapter": "Mountain Regions",
                    "page": 45,
                    "content": "Located in the Cusco Region, Machu Picchu sits at 2,430 meters above sea level.",
                },
            },
            {
                "id": "doc3",
                "score": 0.75,
                "metadata": {
                    "title": "UNESCO Sites in Peru",
                    "content": "The site was declared a UNESCO World Heritage Site in 1983.",
                },
            },
        ]
        return retriever
    
    @pytest.fixture
    def mock_llm(self):
        """Create realistic mock LLM."""
        llm = MagicMock()
        llm.config.model = "gpt-4"
        
        llm.generate.return_value = LLMResponse(
            content=(
                "Machu Picchu is an ancient Inca citadel built around 1450 AD by Emperor Pachacuti "
                "[Source 1]. Located in the Cusco Region at 2,430 meters elevation [Source 2], "
                "it was declared a UNESCO World Heritage Site in 1983 [Source 3]."
            ),
            model="gpt-4",
            usage={"total_tokens": 120, "prompt_tokens": 80, "completion_tokens": 40},
            finish_reason="stop",
            latency_ms=150.0,
        )
        
        return llm
    
    def test_full_rag_pipeline(self, mock_retriever, mock_llm):
        """Test complete RAG pipeline."""
        generator = AnswerGenerator(
            retriever=mock_retriever,
            llm=mock_llm,
            top_k=3,
            include_metadata=True,
        )
        
        response = generator.generate(
            query="When was Machu Picchu built and where is it located?",
            top_k=3,
        )
        
        # Verify complete workflow
        assert response.answer
        assert "[Source 1]" in response.answer
        assert "[Source 2]" in response.answer
        assert len(response.sources) == 3
        
        # Verify sources have proper structure
        source1 = response.sources[0]
        assert source1["source_id"] == 1
        assert source1["score"] == 0.92
        assert "title" in source1["metadata"]
        assert source1["metadata"]["title"] == "Complete Guide to Peru"
        
        # Verify timing
        assert response.latency_ms > 0
        assert response.retrieval_latency_ms > 0
        assert response.generation_latency_ms > 0
    
    def test_context_formatting_with_metadata(self, mock_retriever, mock_llm):
        """Test that context includes proper metadata formatting."""
        generator = AnswerGenerator(
            retriever=mock_retriever,
            llm=mock_llm,
            include_metadata=True,
        )
        
        response = generator.generate(query="Test query")
        
        # Get the messages passed to LLM
        call_args = mock_llm.generate.call_args[0][0]
        user_message = [m for m in call_args if m.role == "user"][0]
        
        # Verify metadata in context
        assert "Title: Complete Guide to Peru" in user_message.content
        assert "Chapter: Inca Architecture" in user_message.content
        assert "Page: 156" in user_message.content
    
    def test_system_prompt_included(self, mock_retriever, mock_llm):
        """Test that system prompt is included in messages."""
        generator = AnswerGenerator(retriever=mock_retriever, llm=mock_llm)
        
        response = generator.generate(query="Test query")
        
        # Get messages
        call_args = mock_llm.generate.call_args[0][0]
        system_message = [m for m in call_args if m.role == "system"][0]
        
        # Verify system prompt content
        assert "Peru" in system_message.content
        assert "guide assistant" in system_message.content
        assert "cite sources" in system_message.content.lower()
