"""Tests for OpenAI LLM implementation."""

import sys
import pytest
from unittest.mock import MagicMock, patch, Mock

# Mock openai module before importing our code
sys.modules['openai'] = MagicMock()
sys.modules['tiktoken'] = MagicMock()

from src.llm.openai_llm import OpenAILLM
from src.llm.config import OpenAIConfig
from src.llm.base_llm import Message, LLMResponse, StreamChunk


class TestOpenAILLM:
    """Tests for OpenAILLM class."""
    
    @pytest.fixture
    def config(self):
        """Create test config."""
        return OpenAIConfig(
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            api_key="sk-test123"
        )
    
    @pytest.fixture
    def mock_openai_client(self):
        """Create mock OpenAI client."""
        client = MagicMock()
        
        # Mock chat completions response
        mock_response = MagicMock()
        mock_response.id = "chatcmpl-123"
        mock_response.model = "gpt-4"
        mock_response.created = 1234567890
        mock_response.system_fingerprint = "fp_123"
        
        # Mock choice
        mock_choice = MagicMock()
        mock_choice.message.content = "This is a test response"
        mock_choice.finish_reason = "stop"
        mock_response.choices = [mock_choice]
        
        # Mock usage
        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 5
        mock_usage.total_tokens = 15
        mock_response.usage = mock_usage
        
        client.chat.completions.create.return_value = mock_response
        
        return client
    
    @patch('openai.OpenAI')
    def test_initialization(self, mock_openai_class, config):
        """Test OpenAI LLM initialization."""
        llm = OpenAILLM(config)
        
        assert llm.config.model == "gpt-4"
        assert llm.config.temperature == 0.7
        mock_openai_class.assert_called_once()
    
    @patch('openai.OpenAI')
    def test_defaults_to_gpt35_when_model_none(self, mock_openai_class):
        """Test config defaults to gpt-3.5-turbo when model is None."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        config = OpenAIConfig(model=None, api_key="sk-test")
        assert config.model == "gpt-3.5-turbo"
        
        llm = OpenAILLM(config)
        assert llm.config.model == "gpt-3.5-turbo"
    
    def test_validate_config_no_api_key(self):
        """Test validation fails without API key."""
        config = OpenAIConfig(model="gpt-4", api_key=None)
        
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key is required"):
                OpenAILLM(config)
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'sk-env-key'})
    @patch('openai.OpenAI')
    def test_api_key_from_env(self, mock_openai_class, config):
        """Test API key can come from environment."""
        config.api_key = None
        llm = OpenAILLM(config)
        
        # Should not raise, uses env var
        assert llm.config.api_key is None
    
    @patch('openai.OpenAI')
    def test_initialization_with_optional_params(self, mock_openai_class):
        """Test initialization with optional parameters."""
        config = OpenAIConfig(
            model="gpt-4",
            api_key="sk-test",
            organization="org-123",
            base_url="https://custom.openai.com"
        )
        
        llm = OpenAILLM(config)
        
        # Check client was initialized with optional params
        call_kwargs = mock_openai_class.call_args.kwargs
        assert call_kwargs["api_key"] == "sk-test"
        assert call_kwargs["organization"] == "org-123"
        assert call_kwargs["base_url"] == "https://custom.openai.com"
    
    @patch('openai.OpenAI')
    def test_generate_basic(self, mock_openai_class, config, mock_openai_client):
        """Test basic generation."""
        mock_openai_class.return_value = mock_openai_client
        llm = OpenAILLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        response = llm.generate(messages)
        
        assert isinstance(response, LLMResponse)
        assert response.content == "This is a test response"
        assert response.model == "gpt-4"
        assert response.usage["total_tokens"] == 15
        assert response.finish_reason == "stop"
        assert response.latency_ms > 0
    
    @patch('openai.OpenAI')
    def test_generate_with_kwargs(self, mock_openai_class, config, mock_openai_client):
        """Test generation with override parameters."""
        mock_openai_class.return_value = mock_openai_client
        llm = OpenAILLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        response = llm.generate(messages, temperature=0.5, max_tokens=500)
        
        # Check that kwargs were passed to API
        call_kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["max_tokens"] == 500
    
    @patch('openai.OpenAI')
    def test_generate_validates_messages(self, mock_openai_class, config):
        """Test generate validates messages."""
        mock_openai_class.return_value = MagicMock()
        llm = OpenAILLM(config)
        
        # Empty messages
        with pytest.raises(ValueError):
            llm.generate([])
        
        # Invalid role
        with pytest.raises(ValueError):
            llm.generate([{"role": "invalid", "content": "Test"}])
    
    @patch('openai.OpenAI')
    def test_generate_api_error(self, mock_openai_class, config):
        """Test generate handles API errors."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client
        
        llm = OpenAILLM(config)
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(RuntimeError, match="OpenAI generation failed"):
            llm.generate(messages)
    
    @patch('openai.OpenAI')
    def test_stream_basic(self, mock_openai_class, config):
        """Test basic streaming."""
        mock_client = MagicMock()
        
        # Mock streaming chunks
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = "Hello"
        mock_chunk1.choices[0].finish_reason = None
        mock_chunk1.model = "gpt-4"
        
        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [MagicMock()]
        mock_chunk2.choices[0].delta.content = " world"
        mock_chunk2.choices[0].finish_reason = None
        mock_chunk2.model = "gpt-4"
        
        mock_chunk3 = MagicMock()
        mock_chunk3.choices = [MagicMock()]
        mock_chunk3.choices[0].delta.content = None
        mock_chunk3.choices[0].finish_reason = "stop"
        mock_chunk3.model = "gpt-4"
        
        mock_client.chat.completions.create.return_value = iter([
            mock_chunk1, mock_chunk2, mock_chunk3
        ])
        mock_openai_class.return_value = mock_client
        
        llm = OpenAILLM(config)
        messages = [{"role": "user", "content": "Hello"}]
        
        chunks = list(llm.stream(messages))
        
        assert len(chunks) == 3
        assert chunks[0].content == "Hello"
        assert chunks[1].content == " world"
        assert chunks[2].finish_reason == "stop"
    
    @patch('openai.OpenAI')
    def test_stream_validates_messages(self, mock_openai_class, config):
        """Test stream validates messages."""
        mock_openai_class.return_value = MagicMock()
        llm = OpenAILLM(config)
        
        # Empty messages
        with pytest.raises(ValueError):
            list(llm.stream([]))
    
    @patch('openai.OpenAI')
    def test_stream_api_error(self, mock_openai_class, config):
        """Test stream handles API errors."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Streaming Error")
        mock_openai_class.return_value = mock_client
        
        llm = OpenAILLM(config)
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(RuntimeError, match="OpenAI streaming failed"):
            list(llm.stream(messages))
    
    @patch('tiktoken.encoding_for_model')
    @patch('openai.OpenAI')
    def test_count_tokens_with_tiktoken(self, mock_openai_class, mock_encoding_for_model, config):
        """Test token counting with tiktoken."""
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]
        mock_encoding_for_model.return_value = mock_encoding
        
        mock_openai_class.return_value = MagicMock()
        llm = OpenAILLM(config)
        
        count = llm.count_tokens("Hello world")
        
        assert count == 5
        mock_encoding_for_model.assert_called_once_with("gpt-4")
    
    @patch('tiktoken.get_encoding')
    @patch('tiktoken.encoding_for_model')
    @patch('openai.OpenAI')
    def test_count_tokens_fallback_encoding(self, mock_openai_class, mock_encoding_for_model, mock_get_encoding, config):
        """Test token counting falls back to cl100k_base for unknown models."""
        mock_encoding_for_model.side_effect = KeyError("unknown model")
        
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3]
        mock_get_encoding.return_value = mock_encoding
        
        mock_openai_class.return_value = MagicMock()
        llm = OpenAILLM(config)
        
        count = llm.count_tokens("Hello")
        
        assert count == 3
        mock_get_encoding.assert_called_once_with("cl100k_base")
    
    @patch('openai.OpenAI')
    def test_count_tokens_without_tiktoken(self, mock_openai_class, config):
        """Test token counting without tiktoken (fallback to estimation)."""
        mock_openai_class.return_value = MagicMock()
        
        # Mock import error for tiktoken
        import sys
        tiktoken_backup = sys.modules.get('tiktoken')
        try:
            sys.modules['tiktoken'] = None
            # Force reimport
            import importlib
            import src.llm.openai_llm as openai_module
            importlib.reload(openai_module)
            
            llm = openai_module.OpenAILLM(config)
            
            # Approximate: 1 token ≈ 4 chars
            count = llm.count_tokens("Hello world!")  # 12 chars
            assert count == 3  # 12 // 4
        finally:
            if tiktoken_backup:
                sys.modules['tiktoken'] = tiktoken_backup
            else:
                sys.modules.pop('tiktoken', None)
    
    @patch('tiktoken.encoding_for_model')
    @patch('openai.OpenAI')
    def test_count_messages_tokens(self, mock_openai_class, mock_encoding_for_model, config):
        """Test counting tokens in messages."""
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]
        mock_encoding_for_model.return_value = mock_encoding
        
        mock_openai_class.return_value = MagicMock()
        llm = OpenAILLM(config)
        
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"}
        ]
        
        count = llm.count_messages_tokens(messages)
        
        # Should include message overhead (3 tokens per message + 3 for priming)
        assert count > 0
    
    @patch('openai.OpenAI')
    def test_repr(self, mock_openai_class, config):
        """Test string representation."""
        mock_openai_class.return_value = MagicMock()
        llm = OpenAILLM(config)
        
        repr_str = repr(llm)
        
        assert "OpenAILLM" in repr_str
        assert "gpt-4" in repr_str


class TestOpenAILLMIntegration:
    """Integration tests for OpenAILLM."""
    
    @patch('openai.OpenAI')
    def test_full_workflow(self, mock_openai_class):
        """Test full workflow with generation and streaming."""
        # Mock client for both generate and stream
        mock_client = MagicMock()
        
        # Mock generate response
        mock_response = MagicMock()
        mock_response.id = "test-123"
        mock_response.model = "gpt-4"
        mock_response.created = 1234567890
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        
        # First call returns generate response
        # Second call returns stream iterator
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "Streamed"
        mock_chunk.choices[0].finish_reason = "stop"
        mock_chunk.model = "gpt-4"
        
        mock_client.chat.completions.create.side_effect = [
            mock_response,
            iter([mock_chunk])
        ]
        
        mock_openai_class.return_value = mock_client
        
        config = OpenAIConfig(model="gpt-4", api_key="sk-test")
        llm = OpenAILLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Test generate
        response = llm.generate(messages)
        assert response.content == "Generated response"
        assert response.model == "gpt-4"
        
        # Test stream
        chunks = list(llm.stream(messages))
        assert len(chunks) == 1
        assert chunks[0].content == "Streamed"
    
    @patch('openai.OpenAI')
    def test_message_formats(self, mock_openai_class):
        """Test different message formats."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.id = "test"
        mock_response.model = "gpt-4"
        mock_response.created = 123
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        config = OpenAIConfig(model="gpt-4", api_key="sk-test")
        llm = OpenAILLM(config)
        
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
