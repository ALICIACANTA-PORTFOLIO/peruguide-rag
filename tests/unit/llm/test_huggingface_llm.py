"""Tests for Hugging Face LLM implementation."""

import sys
import pytest
from unittest.mock import MagicMock, patch, Mock

# Mock huggingface_hub module before importing our code
sys.modules['huggingface_hub'] = MagicMock()

from src.llm.huggingface_llm import HuggingFaceLLM
from src.llm.config import HuggingFaceConfig
from src.llm.base_llm import Message, LLMResponse, StreamChunk


class TestHuggingFaceLLM:
    """Tests for HuggingFaceLLM class."""
    
    @pytest.fixture
    def config(self):
        """Create test config."""
        return HuggingFaceConfig(
            model="meta-llama/Llama-2-7b-chat-hf",
            temperature=0.7,
            max_tokens=500,
            api_key="hf_test_token_123"
        )
    
    @pytest.fixture
    def mock_hf_client(self):
        """Create mock Hugging Face inference client."""
        client = MagicMock()
        
        # Mock text generation response
        client.text_generation.return_value = "This is a test response from Hugging Face"
        
        return client
    
    @patch('huggingface_hub.InferenceClient')
    def test_initialization(self, mock_client_class, config):
        """Test Hugging Face LLM initialization."""
        llm = HuggingFaceLLM(config)
        
        assert llm.config.model == "meta-llama/Llama-2-7b-chat-hf"
        assert llm.config.temperature == 0.7
        mock_client_class.assert_called_once()
    
    @patch('huggingface_hub.InferenceClient')
    def test_defaults_to_llama2_when_model_none(self, mock_client_class):
        """Test config defaults to Llama-2 when model is None."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        config = HuggingFaceConfig(
            model=None,
            api_key="hf_test"
        )
        assert config.model == "meta-llama/Llama-2-7b-chat-hf"
        
        llm = HuggingFaceLLM(config)
        assert llm.config.model == "meta-llama/Llama-2-7b-chat-hf"
    
    def test_validate_config_no_api_key(self):
        """Test validation fails without API key."""
        config = HuggingFaceConfig(
            model="test-model",
            api_key=None
        )
        
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Hugging Face API token is required"):
                HuggingFaceLLM(config)
    
    @patch.dict('os.environ', {'HUGGINGFACE_API_TOKEN': 'env-token'})
    @patch('huggingface_hub.InferenceClient')
    def test_api_key_from_env(self, mock_client_class, config):
        """Test API key can come from environment."""
        config.api_key = None
        llm = HuggingFaceLLM(config)
        
        # Should not raise, uses env var
        assert llm.config.api_key is None
    
    @patch('huggingface_hub.InferenceClient')
    def test_initialization_with_custom_endpoint(self, mock_client_class):
        """Test initialization with custom endpoint."""
        config = HuggingFaceConfig(
            model="my-model",
            api_key="test-key",
            endpoint_url="https://my-endpoint.aws.endpoints.huggingface.cloud"
        )
        
        llm = HuggingFaceLLM(config)
        
        # Check client was initialized with endpoint
        call_kwargs = mock_client_class.call_args.kwargs
        assert call_kwargs["model"] == "https://my-endpoint.aws.endpoints.huggingface.cloud"
        assert call_kwargs["token"] == "test-key"
    
    @patch('huggingface_hub.InferenceClient')
    def test_generate_basic(self, mock_client_class, config, mock_hf_client):
        """Test basic generation."""
        mock_client_class.return_value = mock_hf_client
        llm = HuggingFaceLLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        response = llm.generate(messages)
        
        assert isinstance(response, LLMResponse)
        assert response.content == "This is a test response from Hugging Face"
        assert response.model == "meta-llama/Llama-2-7b-chat-hf"
        assert response.finish_reason == "stop"
        assert response.latency_ms >= 0  # With mocks it might be 0
    
    @patch('huggingface_hub.InferenceClient')
    def test_generate_with_llama2_chat_format(self, mock_client_class, config, mock_hf_client):
        """Test generation with Llama-2-chat format."""
        mock_client_class.return_value = mock_hf_client
        llm = HuggingFaceLLM(config)
        
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"}
        ]
        response = llm.generate(messages)
        
        # Verify the prompt was formatted for Llama-2-chat
        call_args = mock_hf_client.text_generation.call_args
        prompt = call_args[0][0]
        assert "<<SYS>>" in prompt
        assert "[INST]" in prompt
        assert response.content == "This is a test response from Hugging Face"
    
    @patch('huggingface_hub.InferenceClient')
    def test_generate_with_kwargs(self, mock_client_class, config, mock_hf_client):
        """Test generation with override parameters."""
        mock_client_class.return_value = mock_hf_client
        llm = HuggingFaceLLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        response = llm.generate(messages, temperature=0.5, max_tokens=100)
        
        # Check that kwargs were passed to API
        call_kwargs = mock_hf_client.text_generation.call_args.kwargs
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["max_new_tokens"] == 100
    
    @patch('huggingface_hub.InferenceClient')
    def test_generate_validates_messages(self, mock_client_class, config):
        """Test generate validates messages."""
        mock_client_class.return_value = MagicMock()
        llm = HuggingFaceLLM(config)
        
        # Empty messages
        with pytest.raises(ValueError):
            llm.generate([])
        
        # Invalid role
        with pytest.raises(ValueError):
            llm.generate([{"role": "invalid", "content": "Test"}])
    
    @patch('huggingface_hub.InferenceClient')
    def test_generate_api_error(self, mock_client_class, config):
        """Test generate handles API errors."""
        mock_client = MagicMock()
        mock_client.text_generation.side_effect = Exception("HF API Error")
        mock_client_class.return_value = mock_client
        
        llm = HuggingFaceLLM(config)
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(RuntimeError, match="Hugging Face generation failed"):
            llm.generate(messages)
    
    @patch('huggingface_hub.InferenceClient')
    def test_stream_basic(self, mock_client_class, config):
        """Test basic streaming."""
        mock_client = MagicMock()
        
        # Mock streaming tokens
        mock_token1 = MagicMock()
        mock_token1.token.text = "Hello"
        mock_token1.token.special = False
        
        mock_token2 = MagicMock()
        mock_token2.token.text = " world"
        mock_token2.token.special = False
        
        mock_token3 = MagicMock()
        mock_token3.token.text = ""
        mock_token3.token.special = True
        
        mock_client.text_generation.return_value = iter([
            mock_token1, mock_token2, mock_token3
        ])
        mock_client_class.return_value = mock_client
        
        llm = HuggingFaceLLM(config)
        messages = [{"role": "user", "content": "Hello"}]
        
        chunks = list(llm.stream(messages))
        
        assert len(chunks) == 3
        assert chunks[0].content == "Hello"
        assert chunks[1].content == " world"
        assert chunks[2].finish_reason == "stop"
    
    @patch('huggingface_hub.InferenceClient')
    def test_stream_validates_messages(self, mock_client_class, config):
        """Test stream validates messages."""
        mock_client_class.return_value = MagicMock()
        llm = HuggingFaceLLM(config)
        
        # Empty messages
        with pytest.raises(ValueError):
            list(llm.stream([]))
    
    @patch('huggingface_hub.InferenceClient')
    def test_stream_api_error(self, mock_client_class, config):
        """Test stream handles API errors."""
        mock_client = MagicMock()
        mock_client.text_generation.side_effect = Exception("HF Streaming Error")
        mock_client_class.return_value = mock_client
        
        llm = HuggingFaceLLM(config)
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(RuntimeError, match="Hugging Face streaming failed"):
            list(llm.stream(messages))
    
    @patch('huggingface_hub.InferenceClient')
    def test_count_tokens(self, mock_client_class, config):
        """Test token counting (approximation)."""
        mock_client_class.return_value = MagicMock()
        llm = HuggingFaceLLM(config)
        
        # HF uses approximation: 1 token ≈ 4 chars
        text = "Hello world test"  # 16 chars
        count = llm.count_tokens(text)
        
        assert count == 4  # 16 // 4
    
    @patch('huggingface_hub.InferenceClient')
    def test_format_messages_for_non_chat_model(self, mock_client_class):
        """Test message formatting for non-chat models."""
        config = HuggingFaceConfig(
            model="gpt2",  # Not a chat model
            api_key="test-key"
        )
        mock_client_class.return_value = MagicMock()
        llm = HuggingFaceLLM(config)
        
        messages = [
            Message(role="system", content="System message"),
            Message(role="user", content="User message")
        ]
        
        formatted = llm._format_messages_for_hf(messages)
        
        # For non-chat models, should just concatenate
        assert "System message" in formatted
        assert "User message" in formatted
    
    @patch('huggingface_hub.InferenceClient')
    def test_format_messages_for_generic_chat_model(self, mock_client_class):
        """Test message formatting for generic chat models."""
        config = HuggingFaceConfig(
            model="mistralai/Mistral-7B-Instruct-v0.1",
            api_key="test-key"
        )
        mock_client_class.return_value = MagicMock()
        llm = HuggingFaceLLM(config)
        
        messages = [
            Message(role="user", content="Hello")
        ]
        
        formatted = llm._format_messages_for_hf(messages)
        
        # For chat models (not Llama-2), should have User/Assistant format
        assert "User:" in formatted or "INST" in formatted.lower()
    
    @patch('huggingface_hub.InferenceClient')
    def test_repr(self, mock_client_class, config):
        """Test string representation."""
        mock_client_class.return_value = MagicMock()
        llm = HuggingFaceLLM(config)
        
        repr_str = repr(llm)
        
        assert "HuggingFaceLLM" in repr_str
        assert "meta-llama/Llama-2-7b-chat-hf" in repr_str


class TestHuggingFaceLLMIntegration:
    """Integration tests for HuggingFaceLLM."""
    
    @patch('huggingface_hub.InferenceClient')
    def test_full_workflow(self, mock_client_class):
        """Test full workflow with generation and streaming."""
        # Mock client for both generate and stream
        mock_client = MagicMock()
        
        # Mock generate response
        mock_client.text_generation.side_effect = [
            "Generated response from HF",
            iter([
                MagicMock(token=MagicMock(text="Stream", special=False)),
                MagicMock(token=MagicMock(text=" response", special=False)),
                MagicMock(token=MagicMock(text="", special=True))
            ])
        ]
        
        mock_client_class.return_value = mock_client
        
        config = HuggingFaceConfig(
            model="meta-llama/Llama-2-7b-chat-hf",
            api_key="test-key"
        )
        llm = HuggingFaceLLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Test generate
        response = llm.generate(messages)
        assert response.content == "Generated response from HF"
        assert response.model == "meta-llama/Llama-2-7b-chat-hf"
        
        # Test stream
        chunks = list(llm.stream(messages))
        assert len(chunks) == 3
        assert chunks[0].content == "Stream"
        assert chunks[1].content == " response"
    
    @patch('huggingface_hub.InferenceClient')
    def test_message_formats(self, mock_client_class):
        """Test different message formats."""
        mock_client = MagicMock()
        mock_client.text_generation.return_value = "HF Response"
        mock_client_class.return_value = mock_client
        
        config = HuggingFaceConfig(
            model="meta-llama/Llama-2-7b-chat-hf",
            api_key="test-key"
        )
        llm = HuggingFaceLLM(config)
        
        # Test dict messages
        messages_dict = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User message"}
        ]
        response1 = llm.generate(messages_dict)
        assert response1.content == "HF Response"
        
        # Test Message object messages
        messages_obj = [
            Message(role="system", content="System prompt"),
            Message(role="user", content="User message")
        ]
        response2 = llm.generate(messages_obj)
        assert response2.content == "HF Response"
        
        # Test mixed format
        messages_mixed = [
            {"role": "system", "content": "System prompt"},
            Message(role="user", content="User message")
        ]
        response3 = llm.generate(messages_mixed)
        assert response3.content == "HF Response"
    
    @patch('huggingface_hub.InferenceClient')
    def test_with_custom_endpoint(self, mock_client_class):
        """Test using custom inference endpoint."""
        mock_client = MagicMock()
        mock_client.text_generation.return_value = "Custom endpoint response"
        mock_client_class.return_value = mock_client
        
        config = HuggingFaceConfig(
            model="my-model",
            api_key="test-key",
            endpoint_url="https://custom.endpoint.com"
        )
        llm = HuggingFaceLLM(config)
        
        messages = [{"role": "user", "content": "Test"}]
        response = llm.generate(messages)
        
        assert response.content == "Custom endpoint response"
        assert response.metadata.get("endpoint") == "https://custom.endpoint.com"
