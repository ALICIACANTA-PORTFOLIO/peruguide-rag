"""Tests for BaseLLM abstract class."""

import pytest
from unittest.mock import MagicMock
from src.llm.base_llm import BaseLLM, Message, LLMResponse, StreamChunk
from src.llm.config import LLMConfig


class MockLLM(BaseLLM):
    """Mock LLM implementation for testing BaseLLM."""
    
    def __init__(self, config):
        """Initialize mock LLM."""
        self.generate_called = False
        self.stream_called = False
        super().__init__(config)
    
    def _validate_config(self):
        """Validate config (mock implementation)."""
        if not self.config.model:
            raise ValueError("Model is required")
    
    def generate(self, messages, **kwargs):
        """Mock generate method."""
        self.generate_called = True
        normalized = self._normalize_messages(messages)
        self._validate_messages(normalized)
        
        return LLMResponse(
            content="Mock response",
            model=self.config.model,
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            finish_reason="stop",
            latency_ms=100.0,
        )
    
    def stream(self, messages, **kwargs):
        """Mock stream method."""
        self.stream_called = True
        normalized = self._normalize_messages(messages)
        self._validate_messages(normalized)
        
        yield StreamChunk(content="Mock ", finish_reason=None)
        yield StreamChunk(content="stream", finish_reason=None)
        yield StreamChunk(content="", finish_reason="stop")
    
    def count_tokens(self, text):
        """Mock token counting."""
        return len(text) // 4
    
    def count_messages_tokens(self, messages):
        """Mock message token counting."""
        normalized = self._normalize_messages(messages)
        return sum(self.count_tokens(msg.content) for msg in normalized) + 5


class TestMessage:
    """Tests for Message dataclass."""
    
    def test_create_message(self):
        """Test creating a message."""
        msg = Message(role="user", content="Hello")
        
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.name is None
    
    def test_message_with_name(self):
        """Test message with name."""
        msg = Message(role="user", content="Hello", name="Alice")
        
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.name == "Alice"
    
    def test_to_dict(self):
        """Test converting message to dict."""
        msg = Message(role="user", content="Hello")
        result = msg.to_dict()
        
        assert result == {"role": "user", "content": "Hello"}
    
    def test_to_dict_with_name(self):
        """Test to_dict includes name if present."""
        msg = Message(role="user", content="Hello", name="Alice")
        result = msg.to_dict()
        
        assert result == {"role": "user", "content": "Hello", "name": "Alice"}


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""
    
    def test_create_response(self):
        """Test creating a response."""
        response = LLMResponse(
            content="Test response",
            model="test-model",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            finish_reason="stop",
            latency_ms=100.5,
        )
        
        assert response.content == "Test response"
        assert response.model == "test-model"
        assert response.usage["total_tokens"] == 15
        assert response.finish_reason == "stop"
        assert response.latency_ms == 100.5
        assert response.metadata == {}
    
    def test_response_with_metadata(self):
        """Test response with metadata."""
        response = LLMResponse(
            content="Test",
            model="test-model",
            usage={"total_tokens": 15},
            finish_reason="stop",
            latency_ms=100.0,
            metadata={"id": "test-123", "custom": "value"},
        )
        
        assert response.metadata["id"] == "test-123"
        assert response.metadata["custom"] == "value"
    
    def test_repr(self):
        """Test string representation."""
        response = LLMResponse(
            content="A" * 100,  # Long content
            model="test-model",
            usage={"total_tokens": 50},
            finish_reason="stop",
            latency_ms=123.456,
        )
        
        repr_str = repr(response)
        assert "test-model" in repr_str
        assert "tokens=50" in repr_str
        assert "latency=123ms" in repr_str
        assert "..." in repr_str  # Content truncated


class TestStreamChunk:
    """Tests for StreamChunk dataclass."""
    
    def test_create_chunk(self):
        """Test creating a chunk."""
        chunk = StreamChunk(content="Hello")
        
        assert chunk.content == "Hello"
        assert chunk.finish_reason is None
        assert chunk.metadata == {}
    
    def test_chunk_with_finish_reason(self):
        """Test chunk with finish reason."""
        chunk = StreamChunk(content="", finish_reason="stop")
        
        assert chunk.content == ""
        assert chunk.finish_reason == "stop"
    
    def test_chunk_with_metadata(self):
        """Test chunk with metadata."""
        chunk = StreamChunk(
            content="Test",
            metadata={"chunk_index": 1, "model": "test-model"}
        )
        
        assert chunk.metadata["chunk_index"] == 1
        assert chunk.metadata["model"] == "test-model"


class TestBaseLLM:
    """Tests for BaseLLM base class."""
    
    @pytest.fixture
    def config(self):
        """Create test config."""
        return LLMConfig(model="test-model", temperature=0.7)
    
    @pytest.fixture
    def llm(self, config):
        """Create mock LLM instance."""
        return MockLLM(config)
    
    def test_initialization(self, config):
        """Test LLM initialization."""
        llm = MockLLM(config)
        
        assert llm.config.model == "test-model"
        assert llm.config.temperature == 0.7
    
    def test_validate_config_called(self):
        """Test that _validate_config is called during init."""
        config = LLMConfig(model=None)  # Invalid
        
        with pytest.raises(ValueError, match="Model is required"):
            MockLLM(config)
    
    def test_normalize_messages_dict(self, llm):
        """Test normalizing dict messages."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        
        normalized = llm._normalize_messages(messages)
        
        assert len(normalized) == 2
        assert all(isinstance(msg, Message) for msg in normalized)
        assert normalized[0].role == "user"
        assert normalized[0].content == "Hello"
        assert normalized[1].role == "assistant"
    
    def test_normalize_messages_message_objects(self, llm):
        """Test normalizing Message objects."""
        messages = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi")
        ]
        
        normalized = llm._normalize_messages(messages)
        
        assert len(normalized) == 2
        assert normalized[0] is messages[0]  # Same object
        assert normalized[1] is messages[1]
    
    def test_normalize_messages_mixed(self, llm):
        """Test normalizing mixed dict and Message objects."""
        messages = [
            {"role": "user", "content": "Hello"},
            Message(role="assistant", content="Hi")
        ]
        
        normalized = llm._normalize_messages(messages)
        
        assert len(normalized) == 2
        assert all(isinstance(msg, Message) for msg in normalized)
    
    def test_normalize_messages_with_name(self, llm):
        """Test normalizing messages with name field."""
        messages = [{"role": "user", "content": "Hello", "name": "Alice"}]
        
        normalized = llm._normalize_messages(messages)
        
        assert normalized[0].name == "Alice"
    
    def test_normalize_messages_invalid_dict(self, llm):
        """Test error for invalid message dict."""
        messages = [{"role": "user"}]  # Missing content
        
        with pytest.raises(ValueError, match="must have 'role' and 'content'"):
            llm._normalize_messages(messages)
    
    def test_normalize_messages_invalid_type(self, llm):
        """Test error for invalid message type."""
        messages = ["invalid"]
        
        with pytest.raises(ValueError, match="must be dict or Message object"):
            llm._normalize_messages(messages)
    
    def test_validate_messages_empty(self, llm):
        """Test validation fails for empty messages."""
        with pytest.raises(ValueError, match="cannot be empty"):
            llm._validate_messages([])
    
    def test_validate_messages_invalid_role(self, llm):
        """Test validation fails for invalid role."""
        messages = [Message(role="invalid", content="Test")]
        
        with pytest.raises(ValueError, match="Invalid role"):
            llm._validate_messages(messages)
    
    def test_validate_messages_empty_content(self, llm):
        """Test validation fails for empty content."""
        messages = [Message(role="user", content="")]
        
        with pytest.raises(ValueError, match="cannot be empty"):
            llm._validate_messages(messages)
    
    def test_validate_messages_whitespace_content(self, llm):
        """Test validation fails for whitespace-only content."""
        messages = [Message(role="user", content="   ")]
        
        with pytest.raises(ValueError, match="cannot be empty"):
            llm._validate_messages(messages)
    
    def test_validate_messages_valid(self, llm):
        """Test validation passes for valid messages."""
        messages = [
            Message(role="system", content="You are helpful"),
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there")
        ]
        
        # Should not raise
        llm._validate_messages(messages)
    
    def test_get_model_info(self, llm):
        """Test getting model info."""
        info = llm.get_model_info()
        
        assert info["provider"] == "mock"
        assert info["model"] == "test-model"
        assert info["temperature"] == 0.7
        assert info["max_tokens"] == 1000
    
    def test_repr(self, llm):
        """Test string representation."""
        repr_str = repr(llm)
        
        assert "MockLLM" in repr_str
        assert "model=test-model" in repr_str
    
    def test_generate_calls_normalize_and_validate(self, llm):
        """Test that generate calls normalize and validate."""
        messages = [{"role": "user", "content": "Hello"}]
        
        response = llm.generate(messages)
        
        assert llm.generate_called
        assert response.content == "Mock response"
    
    def test_stream_calls_normalize_and_validate(self, llm):
        """Test that stream calls normalize and validate."""
        messages = [{"role": "user", "content": "Hello"}]
        
        chunks = list(llm.stream(messages))
        
        assert llm.stream_called
        assert len(chunks) == 3
        assert chunks[0].content == "Mock "
        assert chunks[1].content == "stream"
        assert chunks[2].finish_reason == "stop"


class TestBaseLLMIntegration:
    """Integration tests for BaseLLM."""
    
    def test_generate_with_invalid_messages(self):
        """Test generate fails with invalid messages."""
        config = LLMConfig(model="test-model")
        llm = MockLLM(config)
        
        # Empty messages
        with pytest.raises(ValueError):
            llm.generate([])
        
        # Invalid role
        with pytest.raises(ValueError):
            llm.generate([{"role": "invalid", "content": "Test"}])
    
    def test_stream_with_invalid_messages(self):
        """Test stream fails with invalid messages."""
        config = LLMConfig(model="test-model")
        llm = MockLLM(config)
        
        # Empty messages
        with pytest.raises(ValueError):
            list(llm.stream([]))
    
    def test_full_workflow(self):
        """Test full workflow with generate and stream."""
        config = LLMConfig(model="test-model", temperature=0.5, max_tokens=500)
        llm = MockLLM(config)
        
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"}
        ]
        
        # Generate
        response = llm.generate(messages)
        assert response.model == "test-model"
        assert response.usage["total_tokens"] == 15
        
        # Stream
        chunks = list(llm.stream(messages))
        assert len(chunks) == 3
        
        # Token counting
        tokens = llm.count_tokens("Hello world")
        assert tokens > 0
        
        msg_tokens = llm.count_messages_tokens(messages)
        assert msg_tokens > 0
        
        # Model info
        info = llm.get_model_info()
        assert info["model"] == "test-model"
        assert info["temperature"] == 0.5
        assert info["max_tokens"] == 500


class TestBaseLLMEdgeCases:
    """Edge case tests for BaseLLM."""
    
    def test_message_with_special_characters(self):
        """Test messages with special characters."""
        config = LLMConfig(model="test-model")
        llm = MockLLM(config)
        
        messages = [
            {"role": "user", "content": "Hello 🌍\n\tSpecial chars: @#$%"}
        ]
        
        # Should not raise
        response = llm.generate(messages)
        assert response.content == "Mock response"
    
    def test_very_long_message(self):
        """Test with very long message."""
        config = LLMConfig(model="test-model")
        llm = MockLLM(config)
        
        messages = [
            {"role": "user", "content": "A" * 10000}
        ]
        
        # Should not raise
        response = llm.generate(messages)
        assert response.content == "Mock response"
    
    def test_many_messages(self):
        """Test with many messages in conversation."""
        config = LLMConfig(model="test-model")
        llm = MockLLM(config)
        
        messages = []
        for i in range(100):
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({"role": role, "content": f"Message {i}"})
        
        # Should not raise
        response = llm.generate(messages)
        assert response.content == "Mock response"
