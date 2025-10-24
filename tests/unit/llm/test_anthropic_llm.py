"""Tests for Anthropic LLM implementation."""

import sys
import pytest
from unittest.mock import MagicMock, patch, Mock

# Mock anthropic module before importing our code
sys.modules['anthropic'] = MagicMock()

from src.llm.anthropic_llm import AnthropicLLM
from src.llm.config import AnthropicConfig
from src.llm.base_llm import Message, LLMResponse, StreamChunk


class TestAnthropicLLM:
    """Tests for AnthropicLLM class."""
    
    @pytest.fixture
    def config(self):
        """Create test config."""
        return AnthropicConfig(
            model="claude-3-sonnet-20240229",
            temperature=0.7,
            max_tokens=1000,
            api_key="sk-ant-test-token-123"
        )
    
    @pytest.fixture
    def mock_anthropic_client(self):
        """Create mock Anthropic client."""
        client = MagicMock()
        
        # Mock message creation response
        mock_response = MagicMock()
        mock_response.id = "msg_123"
        mock_response.model = "claude-3-sonnet-20240229"
        mock_response.role = "assistant"
        mock_response.content = [MagicMock(text="This is Claude's response")]
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock(
            input_tokens=10,
            output_tokens=5
        )
        
        client.messages.create.return_value = mock_response
        
        return client
    
    @patch('anthropic.Anthropic')
    def test_initialization(self, mock_client_class, config):
        """Test Anthropic LLM initialization."""
        llm = AnthropicLLM(config)
        
        assert llm.config.model == "claude-3-sonnet-20240229"
        assert llm.config.temperature == 0.7
        mock_client_class.assert_called_once()
    
    @patch('anthropic.Anthropic')
    def test_defaults_to_claude3_when_model_none(self, mock_client_class):
        """Test config defaults to Claude 3 when model is None."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        config = AnthropicConfig(
            model=None,
            api_key="sk-ant-test"
        )
        assert config.model == "claude-3-sonnet-20240229"
        
        llm = AnthropicLLM(config)
        assert llm.config.model == "claude-3-sonnet-20240229"
    
    def test_validate_config_no_api_key(self):
        """Test validation fails without API key."""
        config = AnthropicConfig(
            model="claude-3-sonnet-20240229",
            api_key=None
        )
        
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Anthropic API key is required"):
                AnthropicLLM(config)
    
    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'env-token'})
    @patch('anthropic.Anthropic')
    def test_api_key_from_env(self, mock_client_class, config):
        """Test API key can come from environment."""
        config.api_key = None
        llm = AnthropicLLM(config)
        
        # Should not raise, uses env var
        assert llm.config.api_key is None
    
    @patch('anthropic.Anthropic')
    def test_initialization_with_custom_params(self, mock_client_class):
        """Test initialization with custom API URL and version."""
        config = AnthropicConfig(
            model="claude-3-opus-20240229",
            api_key="test-key",
            api_url="https://custom.api.anthropic.com",
            anthropic_version="2024-01-01"
        )
        
        llm = AnthropicLLM(config)
        
        # Check client was initialized
        call_kwargs = mock_client_class.call_args.kwargs
        assert call_kwargs["api_key"] == "test-key"
    
    @patch('anthropic.Anthropic')
    def test_generate_basic(self, mock_client_class, config, mock_anthropic_client):
        """Test basic generation."""
        mock_client_class.return_value = mock_anthropic_client
        llm = AnthropicLLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        response = llm.generate(messages)
        
        assert isinstance(response, LLMResponse)
        assert response.content == "This is Claude's response"
        assert response.model == "claude-3-sonnet-20240229"
        assert response.finish_reason == "end_turn"
        assert response.usage["prompt_tokens"] == 10
        assert response.usage["completion_tokens"] == 5
        assert response.usage["total_tokens"] == 15
    
    @patch('anthropic.Anthropic')
    def test_generate_with_system_message(self, mock_client_class, config, mock_anthropic_client):
        """Test generation with system message (Anthropic-specific)."""
        mock_client_class.return_value = mock_anthropic_client
        llm = AnthropicLLM(config)
        
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"}
        ]
        response = llm.generate(messages)
        
        # Verify system message was passed separately to API
        call_kwargs = mock_anthropic_client.messages.create.call_args.kwargs
        assert call_kwargs.get("system") == "You are helpful"
        assert len(call_kwargs["messages"]) == 1  # Only user message
        assert response.content == "This is Claude's response"
    
    @patch('anthropic.Anthropic')
    def test_generate_with_kwargs(self, mock_client_class, config, mock_anthropic_client):
        """Test generation with override parameters."""
        mock_client_class.return_value = mock_anthropic_client
        llm = AnthropicLLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        response = llm.generate(messages, temperature=0.5, max_tokens=500)
        
        # Check that kwargs were passed to API
        call_kwargs = mock_anthropic_client.messages.create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["max_tokens"] == 500
    
    @patch('anthropic.Anthropic')
    def test_generate_validates_messages(self, mock_client_class, config):
        """Test generate validates messages."""
        mock_client_class.return_value = MagicMock()
        llm = AnthropicLLM(config)
        
        # Empty messages
        with pytest.raises(ValueError):
            llm.generate([])
        
        # Invalid role
        with pytest.raises(ValueError):
            llm.generate([{"role": "invalid", "content": "Test"}])
    
    @patch('anthropic.Anthropic')
    def test_generate_api_error(self, mock_client_class, config):
        """Test generate handles API errors."""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("Anthropic API Error")
        mock_client_class.return_value = mock_client
        
        llm = AnthropicLLM(config)
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(RuntimeError, match="Anthropic generation failed"):
            llm.generate(messages)
    
    @patch('anthropic.Anthropic')
    def test_stream_basic(self, mock_client_class, config):
        """Test basic streaming."""
        mock_client = MagicMock()
        
        # Mock streaming events
        mock_event1 = MagicMock()
        mock_event1.type = "content_block_delta"
        mock_event1.delta = MagicMock(text="Hello")
        
        mock_event2 = MagicMock()
        mock_event2.type = "content_block_delta"
        mock_event2.delta = MagicMock(text=" world")
        
        mock_event3 = MagicMock()
        mock_event3.type = "message_stop"
        
        # Mock streaming - Anthropic uses .create(stream=True)
        mock_client.messages.create.return_value = iter([mock_event1, mock_event2, mock_event3])
        
        mock_client_class.return_value = mock_client
        
        llm = AnthropicLLM(config)
        messages = [{"role": "user", "content": "Hello"}]
        
        chunks = list(llm.stream(messages))
        
        assert len(chunks) == 3
        assert chunks[0].content == "Hello"
        assert chunks[1].content == " world"
        assert chunks[2].finish_reason == "stop"
    
    @patch('anthropic.Anthropic')
    def test_stream_validates_messages(self, mock_client_class, config):
        """Test stream validates messages."""
        mock_client_class.return_value = MagicMock()
        llm = AnthropicLLM(config)
        
        # Empty messages
        with pytest.raises(ValueError):
            list(llm.stream([]))
    
    @patch('anthropic.Anthropic')
    def test_stream_api_error(self, mock_client_class, config):
        """Test stream handles API errors."""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("Anthropic Streaming Error")
        mock_client_class.return_value = mock_client
        
        llm = AnthropicLLM(config)
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(RuntimeError, match="Anthropic streaming failed"):
            list(llm.stream(messages))
    
    @patch('anthropic.Anthropic')
    def test_count_tokens(self, mock_client_class, config):
        """Test token counting (approximation)."""
        mock_client_class.return_value = MagicMock()
        llm = AnthropicLLM(config)
        
        # Anthropic uses approximation: 1 token ≈ 4 chars
        text = "Hello world test"  # 16 chars
        count = llm.count_tokens(text)
        
        assert count == 4  # 16 // 4
    
    @patch('anthropic.Anthropic')
    def test_count_messages_tokens(self, mock_client_class, config):
        """Test counting tokens in messages."""
        mock_client_class.return_value = MagicMock()
        llm = AnthropicLLM(config)
        
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"}
        ]
        
        count = llm.count_messages_tokens(messages)
        
        # Should be approximation of both messages combined
        assert count > 0
    
    @patch('anthropic.Anthropic')
    def test_repr(self, mock_client_class, config):
        """Test string representation."""
        mock_client_class.return_value = MagicMock()
        llm = AnthropicLLM(config)
        
        repr_str = repr(llm)
        
        assert "AnthropicLLM" in repr_str
        assert "claude-3-sonnet-20240229" in repr_str


class TestAnthropicLLMIntegration:
    """Integration tests for AnthropicLLM."""
    
    @patch('anthropic.Anthropic')
    def test_full_workflow(self, mock_client_class):
        """Test full workflow with generation and streaming."""
        # Mock client for both generate and stream
        mock_client = MagicMock()
        
        # Mock generate response
        mock_response = MagicMock()
        mock_response.id = "msg_123"
        mock_response.model = "claude-3-sonnet-20240229"
        mock_response.content = [MagicMock(text="Generated response from Claude")]
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock(input_tokens=10, output_tokens=8)
        mock_client.messages.create.return_value = mock_response
        
        # Mock streaming
        mock_event1 = MagicMock()
        mock_event1.type = "content_block_delta"
        mock_event1.delta = MagicMock(text="Stream")
        
        mock_event2 = MagicMock()
        mock_event2.type = "content_block_delta"
        mock_event2.delta = MagicMock(text=" response")
        
        mock_event3 = MagicMock()
        mock_event3.type = "message_stop"
        
        # Store both regular and streaming response
        mock_client.messages.create.side_effect = [
            mock_response,  # First call for generate
            iter([mock_event1, mock_event2, mock_event3])  # Second call for stream
        ]
        
        mock_client_class.return_value = mock_client
        
        config = AnthropicConfig(
            model="claude-3-sonnet-20240229",
            api_key="test-key"
        )
        llm = AnthropicLLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Test generate
        response = llm.generate(messages)
        assert response.content == "Generated response from Claude"
        assert response.model == "claude-3-sonnet-20240229"
        
        # Test stream
        chunks = list(llm.stream(messages))
        assert len(chunks) == 3
        assert chunks[0].content == "Stream"
        assert chunks[1].content == " response"
    
    @patch('anthropic.Anthropic')
    def test_message_formats(self, mock_client_class):
        """Test different message formats."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock(input_tokens=5, output_tokens=3)
        mock_client.messages.create.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        config = AnthropicConfig(
            model="claude-3-sonnet-20240229",
            api_key="test-key"
        )
        llm = AnthropicLLM(config)
        
        # Test dict messages
        messages_dict = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User message"}
        ]
        response1 = llm.generate(messages_dict)
        assert response1.content == "Response"
        
        # Test Message object messages
        messages_obj = [
            Message(role="system", content="System prompt"),
            Message(role="user", content="User message")
        ]
        response2 = llm.generate(messages_obj)
        assert response2.content == "Response"
        
        # Test mixed format
        messages_mixed = [
            {"role": "system", "content": "System prompt"},
            Message(role="user", content="User message")
        ]
        response3 = llm.generate(messages_mixed)
        assert response3.content == "Response"
    
    @patch('anthropic.Anthropic')
    def test_system_message_extraction(self, mock_client_class):
        """Test that system messages are extracted correctly."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_response.stop_reason = "end_turn"
        mock_response.usage = MagicMock(input_tokens=5, output_tokens=3)
        mock_client.messages.create.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        config = AnthropicConfig(
            model="claude-3-sonnet-20240229",
            api_key="test-key"
        )
        llm = AnthropicLLM(config)
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
        
        llm.generate(messages)
        
        # Check that system message was extracted
        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs.get("system") == "You are a helpful assistant"
        
        # Check that only non-system messages were sent
        api_messages = call_kwargs["messages"]
        assert len(api_messages) == 3  # user, assistant, user (no system)
        assert all(msg["role"] != "system" for msg in api_messages)
