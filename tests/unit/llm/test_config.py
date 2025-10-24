"""Tests for LLM configuration classes."""

import pytest
from src.llm.config import (
    LLMConfig,
    OpenAIConfig,
    AzureOpenAIConfig,
    AnthropicConfig,
    GoogleConfig,
    CohereConfig,
    get_config_class,
)


class TestLLMConfig:
    """Tests for base LLMConfig class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = LLMConfig(model="test-model")
        
        assert config.model == "test-model"
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.top_p == 1.0
        assert config.frequency_penalty == 0.0
        assert config.presence_penalty == 0.0
        assert config.timeout == 60
        assert config.max_retries == 3
        assert config.extra_params == {}
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = LLMConfig(
            model="custom-model",
            temperature=0.5,
            max_tokens=500,
            top_p=0.9,
            frequency_penalty=0.5,
            presence_penalty=0.3,
            timeout=30,
            max_retries=5,
            extra_params={"custom": "value"},
        )
        
        assert config.model == "custom-model"
        assert config.temperature == 0.5
        assert config.max_tokens == 500
        assert config.top_p == 0.9
        assert config.frequency_penalty == 0.5
        assert config.presence_penalty == 0.3
        assert config.timeout == 30
        assert config.max_retries == 5
        assert config.extra_params == {"custom": "value"}
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = LLMConfig(
            model="test-model",
            temperature=0.5,
            extra_params={"key": "value"}
        )
        
        result = config.to_dict()
        
        assert result["model"] == "test-model"
        assert result["temperature"] == 0.5
        assert result["max_tokens"] == 1000  # default
        assert result["key"] == "value"  # from extra_params


class TestOpenAIConfig:
    """Tests for OpenAIConfig class."""
    
    def test_default_model(self):
        """Test default model is set."""
        config = OpenAIConfig()
        assert config.model == "gpt-3.5-turbo"
    
    def test_custom_model(self):
        """Test custom model."""
        config = OpenAIConfig(model="gpt-4")
        assert config.model == "gpt-4"
    
    def test_api_key(self):
        """Test API key configuration."""
        config = OpenAIConfig(api_key="sk-test123")
        assert config.api_key == "sk-test123"
    
    def test_organization(self):
        """Test organization configuration."""
        config = OpenAIConfig(organization="org-123")
        assert config.organization == "org-123"
    
    def test_base_url(self):
        """Test custom base URL."""
        config = OpenAIConfig(base_url="https://custom.openai.com")
        assert config.base_url == "https://custom.openai.com"
    
    def test_inherits_from_llmconfig(self):
        """Test that OpenAIConfig inherits LLMConfig properties."""
        config = OpenAIConfig(
            model="gpt-4",
            temperature=0.3,
            max_tokens=2000,
        )
        
        assert config.model == "gpt-4"
        assert config.temperature == 0.3
        assert config.max_tokens == 2000


class TestAzureOpenAIConfig:
    """Tests for AzureOpenAIConfig class."""
    
    def test_default_model(self):
        """Test default model is set."""
        config = AzureOpenAIConfig()
        assert config.model == "gpt-35-turbo"
    
    def test_deployment_name_defaults_to_model(self):
        """Test deployment_name defaults to model name."""
        config = AzureOpenAIConfig(model="my-gpt-4")
        assert config.deployment_name == "my-gpt-4"
    
    def test_custom_deployment_name(self):
        """Test custom deployment name."""
        config = AzureOpenAIConfig(
            model="gpt-4",
            deployment_name="my-deployment"
        )
        assert config.deployment_name == "my-deployment"
    
    def test_azure_endpoint(self):
        """Test Azure endpoint configuration."""
        config = AzureOpenAIConfig(
            azure_endpoint="https://my-resource.openai.azure.com"
        )
        assert config.azure_endpoint == "https://my-resource.openai.azure.com"
    
    def test_api_version(self):
        """Test API version configuration."""
        config = AzureOpenAIConfig(api_version="2024-02-01")
        assert config.api_version == "2024-02-01"
    
    def test_custom_api_version(self):
        """Test custom API version."""
        config = AzureOpenAIConfig(api_version="2023-12-01")
        assert config.api_version == "2023-12-01"


class TestAnthropicConfig:
    """Tests for AnthropicConfig class."""
    
    def test_default_model(self):
        """Test default model is set."""
        config = AnthropicConfig()
        assert config.model == "claude-3-sonnet-20240229"
    
    def test_custom_model(self):
        """Test custom model."""
        config = AnthropicConfig(model="claude-3-opus-20240229")
        assert config.model == "claude-3-opus-20240229"
    
    def test_api_url(self):
        """Test API URL configuration."""
        config = AnthropicConfig()
        assert config.api_url == "https://api.anthropic.com"
    
    def test_anthropic_version(self):
        """Test Anthropic version."""
        config = AnthropicConfig()
        assert config.anthropic_version == "2023-06-01"
    
    def test_api_key(self):
        """Test API key configuration."""
        config = AnthropicConfig(api_key="sk-ant-test123")
        assert config.api_key == "sk-ant-test123"


class TestGoogleConfig:
    """Tests for GoogleConfig class."""
    
    def test_default_model(self):
        """Test default model is set."""
        config = GoogleConfig()
        assert config.model == "gemini-1.5-pro"
    
    def test_custom_model(self):
        """Test custom model."""
        config = GoogleConfig(model="gemini-1.0-pro")
        assert config.model == "gemini-1.0-pro"
    
    def test_location(self):
        """Test default location."""
        config = GoogleConfig()
        assert config.location == "us-central1"
    
    def test_custom_location(self):
        """Test custom location."""
        config = GoogleConfig(location="europe-west1")
        assert config.location == "europe-west1"
    
    def test_project_id(self):
        """Test project ID configuration."""
        config = GoogleConfig(project_id="my-project-123")
        assert config.project_id == "my-project-123"


class TestCohereConfig:
    """Tests for CohereConfig class."""
    
    def test_default_model(self):
        """Test default model is set."""
        config = CohereConfig()
        assert config.model == "command-r-plus"
    
    def test_custom_model(self):
        """Test custom model."""
        config = CohereConfig(model="command-r")
        assert config.model == "command-r"
    
    def test_api_key(self):
        """Test API key configuration."""
        config = CohereConfig(api_key="test-key-123")
        assert config.api_key == "test-key-123"


class TestHuggingFaceConfig:
    """Tests for HuggingFaceConfig class."""
    
    def test_default_model(self):
        """Test default model is set."""
        from src.llm.config import HuggingFaceConfig
        config = HuggingFaceConfig()
        assert config.model == "meta-llama/Llama-2-7b-chat-hf"
    
    def test_custom_model(self):
        """Test custom model."""
        from src.llm.config import HuggingFaceConfig
        config = HuggingFaceConfig(model="mistralai/Mistral-7B-Instruct-v0.1")
        assert config.model == "mistralai/Mistral-7B-Instruct-v0.1"
    
    def test_api_key(self):
        """Test API token configuration."""
        from src.llm.config import HuggingFaceConfig
        config = HuggingFaceConfig(api_key="hf_test_token")
        assert config.api_key == "hf_test_token"
    
    def test_endpoint_url(self):
        """Test custom endpoint URL."""
        from src.llm.config import HuggingFaceConfig
        config = HuggingFaceConfig(endpoint_url="https://my-endpoint.aws.endpoints.huggingface.cloud")
        assert config.endpoint_url == "https://my-endpoint.aws.endpoints.huggingface.cloud"
    
    def test_task(self):
        """Test task configuration."""
        from src.llm.config import HuggingFaceConfig
        config = HuggingFaceConfig(task="text2text-generation")
        assert config.task == "text2text-generation"
    
    def test_use_cache(self):
        """Test cache configuration."""
        from src.llm.config import HuggingFaceConfig
        config = HuggingFaceConfig(use_cache=False)
        assert config.use_cache is False


class TestGetConfigClass:
    """Tests for get_config_class helper function."""
    
    def test_openai(self):
        """Test getting OpenAI config class."""
        config_class = get_config_class("openai")
        assert config_class == OpenAIConfig
    
    def test_azure(self):
        """Test getting Azure config class."""
        config_class = get_config_class("azure")
        assert config_class == AzureOpenAIConfig
    
    def test_anthropic(self):
        """Test getting Anthropic config class."""
        config_class = get_config_class("anthropic")
        assert config_class == AnthropicConfig
    
    def test_google(self):
        """Test getting Google config class."""
        config_class = get_config_class("google")
        assert config_class == GoogleConfig
    
    def test_cohere(self):
        """Test getting Cohere config class."""
        config_class = get_config_class("cohere")
        assert config_class == CohereConfig
    
    def test_huggingface(self):
        """Test getting Hugging Face config class."""
        from src.llm.config import HuggingFaceConfig
        config_class = get_config_class("huggingface")
        assert config_class == HuggingFaceConfig
    
    def test_case_insensitive(self):
        """Test that provider names are case-insensitive."""
        assert get_config_class("OpenAI") == OpenAIConfig
        assert get_config_class("AZURE") == AzureOpenAIConfig
        assert get_config_class("Anthropic") == AnthropicConfig
        from src.llm.config import HuggingFaceConfig
        assert get_config_class("HuggingFace") == HuggingFaceConfig
    
    def test_unsupported_provider(self):
        """Test error for unsupported provider."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            get_config_class("unsupported")
    
    def test_instantiate_from_helper(self):
        """Test creating config instance from helper."""
        config_class = get_config_class("openai")
        config = config_class(model="gpt-4", temperature=0.5)
        
        assert isinstance(config, OpenAIConfig)
        assert config.model == "gpt-4"
        assert config.temperature == 0.5


class TestConfigIntegration:
    """Integration tests for config classes."""
    
    def test_all_configs_have_required_fields(self):
        """Test that all config classes have required fields."""
        configs = [
            OpenAIConfig(),
            AzureOpenAIConfig(),
            AnthropicConfig(),
            GoogleConfig(),
            CohereConfig(),
        ]
        
        for config in configs:
            assert hasattr(config, "model")
            assert hasattr(config, "temperature")
            assert hasattr(config, "max_tokens")
            assert hasattr(config, "to_dict")
            assert config.model is not None  # Default model set
    
    def test_to_dict_includes_base_fields(self):
        """Test that to_dict includes all base fields."""
        config = OpenAIConfig(model="gpt-4", temperature=0.8)
        result = config.to_dict()
        
        # Check base fields are present
        assert "model" in result
        assert "temperature" in result
        assert "max_tokens" in result
        assert "top_p" in result
        assert "frequency_penalty" in result
        assert "presence_penalty" in result
        assert "timeout" in result
        assert "max_retries" in result
