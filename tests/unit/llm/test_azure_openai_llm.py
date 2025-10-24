"""Tests for Azure OpenAI LLM implementation."""

import sys
import pytest
from unittest.mock import MagicMock, patch, Mock

# Mock openai module before importing our code
sys.modules['openai'] = MagicMock()
sys.modules['tiktoken'] = MagicMock()

from src.llm.azure_openai_llm import AzureOpenAILLM
from src.llm.config import AzureOpenAIConfig
from src.llm.base_llm import Message, LLMResponse, StreamChunk


class TestAzureOpenAILLM:
    """Tests for AzureOpenAILLM class."""
    
    @pytest.fixture
    def config(self):
        """Create test config."""
        return AzureOpenAIConfig(
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            api_key="azure-key-123",
            azure_endpoint="https://test.openai.azure.com",
            api_version="2024-02-01"
        )
    
    @pytest.fixture
    def mock_azure_client(self):
        """Create mock Azure OpenAI client."""
        client = MagicMock()
        
        # Mock chat completions response
        mock_response = MagicMock()
        mock_response.id = "chatcmpl-azure-123"
        mock_response.model = "gpt-4"
        mock_response.created = 1234567890
        mock_response.system_fingerprint = "fp_azure_123"
        
        # Mock choice
        mock_choice = MagicMock()
        mock_choice.message.content = "Azure response"
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
    
    @patch('openai.AzureOpenAI')
    def test_initialization(self, mock_azure_class, config):
        """Test Azure OpenAI LLM initialization."""
        llm = AzureOpenAILLM(config)
        
        assert llm.config.model == "gpt-4"
        assert llm.config.temperature == 0.7
        assert llm.config.azure_endpoint == "https://test.openai.azure.com"
        mock_azure_class.assert_called_once()
    
    @patch('openai.AzureOpenAI')
    def test_defaults_to_gpt35_when_model_none(self, mock_azure_class):
        """Test config defaults to gpt-35-turbo when model is None."""
        mock_client = MagicMock()
        mock_azure_class.return_value = mock_client
        
        config = AzureOpenAIConfig(
            model=None,
            api_key="test-key",
            azure_endpoint="https://test.openai.azure.com"
        )
        assert config.model == "gpt-35-turbo"
        
        llm = AzureOpenAILLM(config)
        assert llm.config.model == "gpt-35-turbo"
    
    def test_validate_config_no_api_key(self):
        """Test validation fails without API key."""
        config = AzureOpenAIConfig(
            model="gpt-4",
            api_key=None,
            azure_endpoint="https://test.openai.azure.com"
        )
        
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key is required"):
                AzureOpenAILLM(config)
    
    def test_validate_config_no_endpoint(self):
        """Test validation fails without Azure endpoint."""
        config = AzureOpenAIConfig(
            model="gpt-4",
            api_key="test-key",
            azure_endpoint=None
        )
        
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Azure OpenAI endpoint is required"):
                AzureOpenAILLM(config)
    
    @patch.dict('os.environ', {
        'AZURE_OPENAI_API_KEY': 'env-key',
        'AZURE_OPENAI_ENDPOINT': 'https://env.openai.azure.com'
    })
    @patch('openai.AzureOpenAI')
    def test_credentials_from_env(self, mock_azure_class, config):
        """Test API key and endpoint can come from environment."""
        config.api_key = None
        config.azure_endpoint = None
        llm = AzureOpenAILLM(config)
        
        # Should not raise, uses env vars
        assert llm.config.api_key is None
        assert llm.config.azure_endpoint is None
    
    @patch('openai.AzureOpenAI')
    def test_initialization_with_api_version(self, mock_azure_class):
        """Test initialization with custom API version."""
        config = AzureOpenAIConfig(
            model="gpt-4",
            api_key="test-key",
            azure_endpoint="https://test.openai.azure.com",
            api_version="2023-12-01"
        )
        
        llm = AzureOpenAILLM(config)
        
        # Check client was initialized with API version
        call_kwargs = mock_azure_class.call_args.kwargs
        assert call_kwargs["api_key"] == "test-key"
        assert call_kwargs["azure_endpoint"] == "https://test.openai.azure.com"
        assert call_kwargs["api_version"] == "2023-12-01"
    
    @patch('openai.AzureOpenAI')
    def test_generate_basic(self, mock_azure_class, config, mock_azure_client):
        """Test basic generation."""
        mock_azure_class.return_value = mock_azure_client
        llm = AzureOpenAILLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        response = llm.generate(messages)
        
        assert isinstance(response, LLMResponse)
        assert response.content == "Azure response"
        assert response.model == "gpt-4"
        assert response.usage["total_tokens"] == 15
        assert response.finish_reason == "stop"
        assert response.latency_ms > 0
    
    @patch('openai.AzureOpenAI')
    def test_generate_with_kwargs(self, mock_azure_class, config, mock_azure_client):
        """Test generation with override parameters."""
        mock_azure_class.return_value = mock_azure_client
        llm = AzureOpenAILLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        response = llm.generate(messages, temperature=0.5, max_tokens=500)
        
        # Check that kwargs were passed to API
        call_kwargs = mock_azure_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["max_tokens"] == 500
        # Azure uses model parameter (deployment name)
        assert "model" in call_kwargs
    
    @patch('openai.AzureOpenAI')
    def test_generate_validates_messages(self, mock_azure_class, config):
        """Test generate validates messages."""
        mock_azure_class.return_value = MagicMock()
        llm = AzureOpenAILLM(config)
        
        # Empty messages
        with pytest.raises(ValueError):
            llm.generate([])
        
        # Invalid role
        with pytest.raises(ValueError):
            llm.generate([{"role": "invalid", "content": "Test"}])
    
    @patch('openai.AzureOpenAI')
    def test_generate_api_error(self, mock_azure_class, config):
        """Test generate handles API errors."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Azure API Error")
        mock_azure_class.return_value = mock_client
        
        llm = AzureOpenAILLM(config)
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(RuntimeError, match="Azure OpenAI generation failed"):
            llm.generate(messages)
    
    @patch('openai.AzureOpenAI')
    def test_stream_basic(self, mock_azure_class, config):
        """Test basic streaming."""
        mock_client = MagicMock()
        
        # Mock streaming chunks
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = "Azure"
        mock_chunk1.choices[0].finish_reason = None
        mock_chunk1.model = "gpt-4"
        
        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [MagicMock()]
        mock_chunk2.choices[0].delta.content = " stream"
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
        mock_azure_class.return_value = mock_client
        
        llm = AzureOpenAILLM(config)
        messages = [{"role": "user", "content": "Hello"}]
        
        chunks = list(llm.stream(messages))
        
        assert len(chunks) == 3
        assert chunks[0].content == "Azure"
        assert chunks[1].content == " stream"
        assert chunks[2].finish_reason == "stop"
    
    @patch('openai.AzureOpenAI')
    def test_stream_validates_messages(self, mock_azure_class, config):
        """Test stream validates messages."""
        mock_azure_class.return_value = MagicMock()
        llm = AzureOpenAILLM(config)
        
        # Empty messages
        with pytest.raises(ValueError):
            list(llm.stream([]))
    
    @patch('openai.AzureOpenAI')
    def test_stream_api_error(self, mock_azure_class, config):
        """Test stream handles API errors."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Azure Streaming Error")
        mock_azure_class.return_value = mock_client
        
        llm = AzureOpenAILLM(config)
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(RuntimeError, match="Azure OpenAI streaming failed"):
            list(llm.stream(messages))
    
    @patch('tiktoken.encoding_for_model')
    @patch('openai.AzureOpenAI')
    def test_count_tokens_with_tiktoken(self, mock_azure_class, mock_encoding_for_model, config):
        """Test token counting with tiktoken."""
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]
        mock_encoding_for_model.return_value = mock_encoding
        
        mock_azure_class.return_value = MagicMock()
        llm = AzureOpenAILLM(config)
        
        count = llm.count_tokens("Hello world")
        
        assert count == 5
        # Azure OpenAI uses gpt-3.5-turbo encoding regardless of deployment name
        mock_encoding_for_model.assert_called_once_with("gpt-3.5-turbo")
    
    @patch('tiktoken.get_encoding')
    @patch('tiktoken.encoding_for_model')
    @patch('openai.AzureOpenAI')
    def test_count_tokens_fallback_encoding(self, mock_azure_class, mock_encoding_for_model, mock_get_encoding, config):
        """Test token counting falls back to cl100k_base for unknown models."""
        mock_encoding_for_model.side_effect = KeyError("unknown model")
        
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3]
        mock_get_encoding.return_value = mock_encoding
        
        mock_azure_class.return_value = MagicMock()
        llm = AzureOpenAILLM(config)
        
        count = llm.count_tokens("Hello")
        
        assert count == 3
        mock_get_encoding.assert_called_once_with("cl100k_base")
    
    @patch('tiktoken.encoding_for_model')
    @patch('openai.AzureOpenAI')
    def test_count_messages_tokens(self, mock_azure_class, mock_encoding_for_model, config):
        """Test counting tokens in messages."""
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]
        mock_encoding_for_model.return_value = mock_encoding
        
        mock_azure_class.return_value = MagicMock()
        llm = AzureOpenAILLM(config)
        
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"}
        ]
        
        count = llm.count_messages_tokens(messages)
        
        # Should include message overhead (3 tokens per message + 3 for priming)
        assert count > 0
    
    @patch('openai.AzureOpenAI')
    def test_repr(self, mock_azure_class, config):
        """Test string representation."""
        mock_azure_class.return_value = MagicMock()
        llm = AzureOpenAILLM(config)
        
        repr_str = repr(llm)
        
        assert "AzureOpenAILLM" in repr_str
        assert "gpt-4" in repr_str


class TestAzureOpenAILLMIntegration:
    """Integration tests for AzureOpenAILLM."""
    
    @patch('openai.AzureOpenAI')
    def test_full_workflow(self, mock_azure_class):
        """Test full workflow with generation and streaming."""
        # Mock client for both generate and stream
        mock_client = MagicMock()
        
        # Mock generate response
        mock_response = MagicMock()
        mock_response.id = "test-azure-123"
        mock_response.model = "gpt-4"
        mock_response.created = 1234567890
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated from Azure"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        
        # First call returns generate response
        # Second call returns stream iterator
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "Streamed from Azure"
        mock_chunk.choices[0].finish_reason = "stop"
        mock_chunk.model = "gpt-4"
        
        mock_client.chat.completions.create.side_effect = [
            mock_response,
            iter([mock_chunk])
        ]
        
        mock_azure_class.return_value = mock_client
        
        config = AzureOpenAIConfig(
            model="gpt-4",
            api_key="test-key",
            azure_endpoint="https://test.openai.azure.com"
        )
        llm = AzureOpenAILLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Test generate
        response = llm.generate(messages)
        assert response.content == "Generated from Azure"
        assert response.model == "gpt-4"
        
        # Test stream
        chunks = list(llm.stream(messages))
        assert len(chunks) == 1
        assert chunks[0].content == "Streamed from Azure"
    
    @patch('openai.AzureOpenAI')
    def test_message_formats(self, mock_azure_class):
        """Test different message formats."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.id = "test"
        mock_response.model = "gpt-4"
        mock_response.created = 123
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Azure Response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_class.return_value = mock_client
        
        config = AzureOpenAIConfig(
            model="gpt-4",
            api_key="test-key",
            azure_endpoint="https://test.openai.azure.com"
        )
        llm = AzureOpenAILLM(config)
        
        # Test dict messages
        messages_dict = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User message"}
        ]
        response1 = llm.generate(messages_dict)
        assert response1.content == "Azure Response"
        
        # Test Message object messages
        messages_obj = [
            Message(role="system", content="System prompt"),
            Message(role="user", content="User message")
        ]
        response2 = llm.generate(messages_obj)
        assert response2.content == "Azure Response"
        
        # Test mixed format
        messages_mixed = [
            {"role": "system", "content": "System prompt"},
            Message(role="user", content="User message")
        ]
        response3 = llm.generate(messages_mixed)
        assert response3.content == "Azure Response"
    
    @patch('openai.AzureOpenAI')
    def test_model_as_deployment_name(self, mock_azure_class):
        """Test that model parameter is used as deployment name in Azure."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.id = "test"
        mock_response.model = "gpt-4-deployment"
        mock_response.created = 123
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 3
        mock_response.usage.total_tokens = 8
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_class.return_value = mock_client
        
        config = AzureOpenAIConfig(
            model="gpt-4-deployment",
            api_key="test-key",
            azure_endpoint="https://test.openai.azure.com"
        )
        llm = AzureOpenAILLM(config)
        
        messages = [{"role": "user", "content": "Test"}]
        response = llm.generate(messages)
        
        # Verify deployment name was used
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "gpt-4-deployment"
        assert response.content == "Response"
