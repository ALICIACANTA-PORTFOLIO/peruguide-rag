"""
Configuration classes for LLM providers.

This module defines configuration dataclasses for different LLM providers,
allowing easy customization and provider-specific settings while maintaining
a consistent interface.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class LLMConfig:
    """Base configuration for LLM providers."""
    
    model: Optional[str] = None
    """Model name/identifier (e.g., 'gpt-4', 'claude-3-opus')"""
    
    temperature: float = 0.7
    """Sampling temperature (0.0 = deterministic, 1.0 = creative)"""
    
    max_tokens: int = 1000
    """Maximum tokens to generate in response"""
    
    top_p: float = 1.0
    """Nucleus sampling parameter (alternative to temperature)"""
    
    frequency_penalty: float = 0.0
    """Penalty for token frequency (-2.0 to 2.0)"""
    
    presence_penalty: float = 0.0
    """Penalty for token presence (-2.0 to 2.0)"""
    
    timeout: int = 60
    """Request timeout in seconds"""
    
    max_retries: int = 3
    """Maximum number of retry attempts on failure"""
    
    extra_params: Dict[str, Any] = field(default_factory=dict)
    """Additional provider-specific parameters"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            **self.extra_params,
        }


@dataclass
class OpenAIConfig(LLMConfig):
    """Configuration for OpenAI LLM provider."""
    
    api_key: Optional[str] = None
    """OpenAI API key (if not set, uses OPENAI_API_KEY env var)"""
    
    organization: Optional[str] = None
    """OpenAI organization ID (optional)"""
    
    base_url: Optional[str] = None
    """Custom base URL for OpenAI API (optional)"""
    
    def __post_init__(self):
        """Validate OpenAI-specific configuration."""
        if self.model is None:
            self.model = "gpt-3.5-turbo"


@dataclass
class AzureOpenAIConfig(LLMConfig):
    """Configuration for Azure OpenAI LLM provider."""
    
    api_key: Optional[str] = None
    """Azure OpenAI API key (if not set, uses AZURE_OPENAI_API_KEY env var)"""
    
    azure_endpoint: Optional[str] = None
    """Azure OpenAI endpoint URL (if not set, uses AZURE_OPENAI_ENDPOINT env var)"""
    
    api_version: str = "2024-02-01"
    """Azure OpenAI API version"""
    
    deployment_name: Optional[str] = None
    """Azure deployment name (if different from model name)"""
    
    def __post_init__(self):
        """Validate Azure-specific configuration."""
        if self.model is None:
            self.model = "gpt-35-turbo"
        
        # Azure uses deployment_name, fallback to model if not set
        if self.deployment_name is None:
            self.deployment_name = self.model


@dataclass
class AnthropicConfig(LLMConfig):
    """Configuration for Anthropic Claude LLM provider."""
    
    api_key: Optional[str] = None
    """Anthropic API key (if not set, uses ANTHROPIC_API_KEY env var)"""
    
    api_url: str = "https://api.anthropic.com"
    """Anthropic API base URL"""
    
    anthropic_version: str = "2023-06-01"
    """Anthropic API version"""
    
    def __post_init__(self):
        """Validate Anthropic-specific configuration."""
        if self.model is None:
            self.model = "claude-3-sonnet-20240229"


@dataclass
class GoogleConfig(LLMConfig):
    """Configuration for Google Gemini LLM provider."""
    
    api_key: Optional[str] = None
    """Google API key (if not set, uses GOOGLE_API_KEY env var)"""
    
    project_id: Optional[str] = None
    """Google Cloud project ID (optional, for Vertex AI)"""
    
    location: str = "us-central1"
    """Google Cloud location for Vertex AI"""
    
    def __post_init__(self):
        """Validate Google-specific configuration."""
        if self.model is None:
            self.model = "gemini-1.5-pro"


@dataclass
class CohereConfig(LLMConfig):
    """Configuration for Cohere LLM provider."""
    
    api_key: Optional[str] = None
    """Cohere API key (if not set, uses COHERE_API_KEY env var)"""
    
    def __post_init__(self):
        """Validate Cohere-specific configuration."""
        if self.model is None:
            self.model = "command-r-plus"


@dataclass
class HuggingFaceConfig(LLMConfig):
    """Configuration for Hugging Face LLM provider."""
    
    api_key: Optional[str] = None
    """Hugging Face API token (if not set, uses HUGGINGFACE_API_TOKEN env var)"""
    
    endpoint_url: Optional[str] = None
    """Custom inference endpoint URL (optional, for dedicated endpoints)"""
    
    task: str = "text-generation"
    """Task type for the model (text-generation, text2text-generation, etc.)"""
    
    use_cache: bool = True
    """Whether to use Hugging Face's caching mechanism"""
    
    def __post_init__(self):
        """Validate Hugging Face-specific configuration."""
        if self.model is None:
            self.model = "meta-llama/Llama-2-7b-chat-hf"


@dataclass
class DeepSeekConfig(LLMConfig):
    """Configuration for DeepSeek LLM provider."""
    
    api_key: Optional[str] = None
    """DeepSeek API key (if not set, uses DEEPSEEK_API_KEY env var)"""
    
    base_url: str = "https://api.deepseek.com"
    """DeepSeek API base URL"""
    
    def __post_init__(self):
        """Validate DeepSeek-specific configuration."""
        if self.model is None:
            self.model = "deepseek-chat"


# Provider configuration mapping for easy lookup
PROVIDER_CONFIGS = {
    "openai": OpenAIConfig,
    "azure": AzureOpenAIConfig,
    "anthropic": AnthropicConfig,
    "google": GoogleConfig,
    "cohere": CohereConfig,
    "huggingface": HuggingFaceConfig,
    "deepseek": DeepSeekConfig,
}


def get_config_class(provider: str) -> type:
    """
    Get configuration class for a provider.
    
    Args:
        provider: Provider name (e.g., 'openai', 'azure', 'anthropic')
        
    Returns:
        Configuration class for the provider
        
    Raises:
        ValueError: If provider is not supported
        
    Example:
        >>> config_class = get_config_class("openai")
        >>> config = config_class(model="gpt-4", temperature=0.5)
    """
    provider_lower = provider.lower()
    if provider_lower not in PROVIDER_CONFIGS:
        supported = ", ".join(PROVIDER_CONFIGS.keys())
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported providers: {supported}"
        )
    return PROVIDER_CONFIGS[provider_lower]
