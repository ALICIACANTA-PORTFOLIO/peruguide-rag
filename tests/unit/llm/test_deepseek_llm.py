"""Tests for DeepSeek LLM implementation."""

import sys
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

# Mock openai before importing DeepSeekLLM
sys.modules['openai'] = MagicMock()
sys.modules['tiktoken'] = MagicMock()

import pytest

from src.llm.base_llm import Message, StreamChunk
from src.llm.config import DeepSeekConfig
from src.llm.deepseek_llm import DeepSeekLLM


@pytest.fixture
def config() -> DeepSeekConfig:
    """Create test configuration."""
    return DeepSeekConfig(
        api_key="test-key",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=1000,
    )


@pytest.fixture
def mock_deepseek_client():
    """Create mock DeepSeek client."""
    mock_client = MagicMock()
    
    # Mock successful completion response
    mock_response = MagicMock()
    mock_response.id = "chatcmpl-test123"
    mock_response.model = "deepseek-chat"
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello! How can I help?"
    mock_response.choices[0].finish_reason = "stop"
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    mock_response.usage.total_tokens = 30
    
    mock_client.chat.completions.create.return_value = mock_response
    
    return mock_client


class TestDeepSeekLLM:
    """Test DeepSeek LLM implementation."""
    
    @patch('openai.OpenAI')
    def test_initialization(self, mock_openai_class, config):
        """Test DeepSeek LLM initialization."""
        llm = DeepSeekLLM(config)
        
        assert llm.config.model == "deepseek-chat"
        assert llm.config.temperature == 0.7
        assert llm.config.max_tokens == 1000
        
        # Verify OpenAI client initialized with DeepSeek endpoint
        mock_openai_class.assert_called_once()
        call_kwargs = mock_openai_class.call_args[1]
        assert call_kwargs["api_key"] == "test-key"
        assert call_kwargs["base_url"] == "https://api.deepseek.com"
    
    @patch('openai.OpenAI')
    def test_initialization_with_env_var(self, mock_openai_class):
        """Test initialization with environment variable."""
        config = DeepSeekConfig(model="deepseek-chat")
        
        with patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'env-key'}):
            llm = DeepSeekLLM(config)
            
            call_kwargs = mock_openai_class.call_args[1]
            assert call_kwargs["api_key"] == "env-key"
    
    def test_initialization_without_openai_package(self, config):
        """Test error when openai package not available."""
        with patch.dict('sys.modules', {'openai': None}):
            with pytest.raises(RuntimeError, match="OpenAI package is required"):
                DeepSeekLLM(config)
    
    @patch('openai.OpenAI')
    def test_default_model(self, mock_openai_class):
        """Test default model selection."""
        config = DeepSeekConfig(api_key="test-key")
        
        llm = DeepSeekLLM(config)
        assert llm.config.model == "deepseek-chat"
    
    @patch('openai.OpenAI')
    def test_custom_base_url(self, mock_openai_class):
        """Test custom base URL."""
        config = DeepSeekConfig(
            api_key="test-key",
            base_url="https://custom.deepseek.com",
        )
        
        llm = DeepSeekLLM(config)
        
        call_kwargs = mock_openai_class.call_args[1]
        assert call_kwargs["base_url"] == "https://custom.deepseek.com"
    
    @patch('openai.OpenAI')
    def test_generate_basic(self, mock_openai_class, config, mock_deepseek_client):
        """Test basic generation."""
        mock_openai_class.return_value = mock_deepseek_client
        
        llm = DeepSeekLLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        response = llm.generate(messages)
        
        assert response.content == "Hello! How can I help?"
        assert response.model == "deepseek-chat"
        assert response.usage["total_tokens"] == 30
        assert response.finish_reason == "stop"
        assert response.latency_ms >= 0
        assert "id" in response.metadata
    
    @patch('openai.OpenAI')
    def test_generate_with_message_objects(self, mock_openai_class, config, mock_deepseek_client):
        """Test generation with Message objects."""
        mock_openai_class.return_value = mock_deepseek_client
        
        llm = DeepSeekLLM(config)
        
        messages = [Message(role="user", content="Hello")]
        response = llm.generate(messages)
        
        assert response.content == "Hello! How can I help?"
        
        # Verify OpenAI format used
        call_args = mock_deepseek_client.chat.completions.create.call_args
        called_messages = call_args[1]["messages"]
        assert called_messages[0]["role"] == "user"
        assert called_messages[0]["content"] == "Hello"
    
    @patch('openai.OpenAI')
    def test_generate_with_system_message(self, mock_openai_class, config, mock_deepseek_client):
        """Test generation with system message."""
        mock_openai_class.return_value = mock_deepseek_client
        
        llm = DeepSeekLLM(config)
        
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
        ]
        response = llm.generate(messages)
        
        # Verify both messages passed
        call_args = mock_deepseek_client.chat.completions.create.call_args
        called_messages = call_args[1]["messages"]
        assert len(called_messages) == 2
        assert called_messages[0]["role"] == "system"
        assert called_messages[1]["role"] == "user"
    
    @patch('openai.OpenAI')
    def test_generate_with_custom_parameters(self, mock_openai_class, config, mock_deepseek_client):
        """Test generation with custom parameters."""
        mock_openai_class.return_value = mock_deepseek_client
        
        llm = DeepSeekLLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        response = llm.generate(
            messages,
            temperature=0.9,
            max_tokens=500,
            top_p=0.95,
        )
        
        call_args = mock_deepseek_client.chat.completions.create.call_args
        assert call_args[1]["temperature"] == 0.9
        assert call_args[1]["max_tokens"] == 500
        assert call_args[1]["top_p"] == 0.95
    
    @patch('openai.OpenAI')
    def test_generate_error_handling(self, mock_openai_class, config, mock_deepseek_client):
        """Test error handling during generation."""
        mock_deepseek_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_deepseek_client
        
        llm = DeepSeekLLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(RuntimeError, match="DeepSeek generation failed"):
            llm.generate(messages)
    
    @patch('openai.OpenAI')
    def test_stream_basic(self, mock_openai_class, config):
        """Test basic streaming."""
        mock_client = MagicMock()
        
        # Mock stream chunks
        mock_chunks = [
            MagicMock(
                model="deepseek-chat",
                choices=[MagicMock(
                    delta=MagicMock(content="Hello"),
                    finish_reason=None,
                )]
            ),
            MagicMock(
                model="deepseek-chat",
                choices=[MagicMock(
                    delta=MagicMock(content=" there"),
                    finish_reason=None,
                )]
            ),
            MagicMock(
                model="deepseek-chat",
                choices=[MagicMock(
                    delta=MagicMock(content="!"),
                    finish_reason="stop",
                )]
            ),
        ]
        
        mock_client.chat.completions.create.return_value = iter(mock_chunks)
        mock_openai_class.return_value = mock_client
        
        llm = DeepSeekLLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        chunks = list(llm.stream(messages))
        
        assert len(chunks) == 3
        assert chunks[0].content == "Hello"
        assert chunks[1].content == " there"
        assert chunks[2].content == "!"
        assert chunks[2].finish_reason == "stop"
    
    @patch('openai.OpenAI')
    def test_stream_with_empty_deltas(self, mock_openai_class, config):
        """Test streaming with empty delta content."""
        mock_client = MagicMock()
        
        # Mock stream with empty content
        mock_chunks = [
            MagicMock(
                model="deepseek-chat",
                choices=[MagicMock(
                    delta=MagicMock(content=None),
                    finish_reason=None,
                )]
            ),
            MagicMock(
                model="deepseek-chat",
                choices=[MagicMock(
                    delta=MagicMock(content="Hello"),
                    finish_reason="stop",
                )]
            ),
        ]
        
        mock_client.chat.completions.create.return_value = iter(mock_chunks)
        mock_openai_class.return_value = mock_client
        
        llm = DeepSeekLLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        chunks = list(llm.stream(messages))
        
        # Only chunks with content or finish_reason
        assert len(chunks) == 1
        assert chunks[0].content == "Hello"
    
    @patch('openai.OpenAI')
    def test_stream_error_handling(self, mock_openai_class, config):
        """Test error handling during streaming."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Stream Error")
        mock_openai_class.return_value = mock_client
        
        llm = DeepSeekLLM(config)
        
        messages = [{"role": "user", "content": "Hello"}]
        
        with pytest.raises(RuntimeError, match="DeepSeek streaming failed"):
            list(llm.stream(messages))
    
    @patch('openai.OpenAI')
    def test_count_tokens_with_tiktoken(self, mock_openai_class, config):
        """Test token counting with tiktoken."""
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]
        
        with patch('tiktoken.get_encoding', return_value=mock_encoding):
            llm = DeepSeekLLM(config)
            
            count = llm.count_tokens("Hello world")
            
            assert count == 5
            mock_encoding.encode.assert_called_once_with("Hello world")
    
    @patch('openai.OpenAI')
    def test_count_tokens_without_tiktoken(self, mock_openai_class, config):
        """Test token counting without tiktoken (approximation)."""
        with patch.dict('sys.modules', {'tiktoken': None}):
            llm = DeepSeekLLM(config)
            
            # Approximation: 1 token ≈ 4 chars
            count = llm.count_tokens("Hello world")  # 11 chars
            
            assert count == 11 // 4  # 2 tokens
    
    @patch('openai.OpenAI')
    def test_count_messages_tokens(self, mock_openai_class, config):
        """Test counting tokens in messages."""
        llm = DeepSeekLLM(config)
        
        with patch.object(llm, 'count_tokens', return_value=5):
            messages = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ]
            
            count = llm.count_messages_tokens(messages)
            
            # Each message: content (5) + role (5) + overhead (4) = 14
            # Two messages: 14 * 2 = 28
            # Conversation overhead: 3
            # Total: 31
            assert count == 31


class TestDeepSeekLLMIntegration:
    """Integration tests for DeepSeek LLM."""
    
    @patch('openai.OpenAI')
    def test_full_generation_workflow(self, mock_openai_class, config, mock_deepseek_client):
        """Test complete generation workflow."""
        mock_openai_class.return_value = mock_deepseek_client
        
        llm = DeepSeekLLM(config)
        
        # Multi-turn conversation
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "What is 2+2?"},
        ]
        
        response = llm.generate(messages)
        
        assert response.content
        assert response.usage["total_tokens"] > 0
        assert response.model == "deepseek-chat"
    
    @patch('openai.OpenAI')
    def test_streaming_workflow(self, mock_openai_class, config):
        """Test complete streaming workflow."""
        mock_client = MagicMock()
        
        mock_chunks = [
            MagicMock(
                model="deepseek-chat",
                choices=[MagicMock(delta=MagicMock(content="The"), finish_reason=None)]
            ),
            MagicMock(
                model="deepseek-chat",
                choices=[MagicMock(delta=MagicMock(content=" answer"), finish_reason=None)]
            ),
            MagicMock(
                model="deepseek-chat",
                choices=[MagicMock(delta=MagicMock(content=" is 4"), finish_reason="stop")]
            ),
        ]
        
        mock_client.chat.completions.create.return_value = iter(mock_chunks)
        mock_openai_class.return_value = mock_client
        
        llm = DeepSeekLLM(config)
        
        messages = [{"role": "user", "content": "What is 2+2?"}]
        
        # Collect streamed content
        full_content = ""
        for chunk in llm.stream(messages):
            full_content += chunk.content
        
        assert full_content == "The answer is 4"
    
    @patch('openai.OpenAI')
    def test_message_format_compatibility(self, mock_openai_class, config, mock_deepseek_client):
        """Test different message formats."""
        mock_openai_class.return_value = mock_deepseek_client
        
        llm = DeepSeekLLM(config)
        
        # Test with dicts
        dict_messages = [{"role": "user", "content": "Hello"}]
        response1 = llm.generate(dict_messages)
        assert response1.content
        
        # Test with Message objects
        obj_messages = [Message(role="user", content="Hello")]
        response2 = llm.generate(obj_messages)
        assert response2.content
