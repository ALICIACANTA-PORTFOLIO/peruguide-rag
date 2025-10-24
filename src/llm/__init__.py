"""
LLM Integration Module

This module provides a provider-agnostic interface for Large Language Models (LLMs).
Following the same ABC pattern used throughout the project, it allows seamless
switching between different LLM providers (OpenAI, Azure, Anthropic, Google, etc.).

Components:
    - BaseLLM: Abstract base class defining LLM interface
    - OpenAILLM: OpenAI implementation (GPT-3.5, GPT-4, etc.)
    - AzureOpenAILLM: Azure OpenAI implementation
    - AnthropicLLM: Anthropic implementation (Claude models)
    - LLMConfig: Configuration classes for each provider

Example:
    >>> # OpenAI
    >>> from src.llm import OpenAILLM, OpenAIConfig
    >>> config = OpenAIConfig(model="gpt-4", temperature=0.7)
    >>> llm = OpenAILLM(config)
    >>> 
    >>> # Azure
    >>> from src.llm import AzureOpenAILLM, AzureOpenAIConfig
    >>> config = AzureOpenAIConfig(
    ...     deployment_name="my-gpt-4",
    ...     azure_endpoint="https://my-resource.openai.azure.com"
    ... )
    >>> llm = AzureOpenAILLM(config)
    >>> 
    >>> # Anthropic
    >>> from src.llm import AnthropicLLM, AnthropicConfig
    >>> config = AnthropicConfig(model="claude-3-sonnet-20240229")
    >>> llm = AnthropicLLM(config)
    >>> 
    >>> # Common interface for all providers
    >>> messages = [{"role": "user", "content": "Hello!"}]
    >>> response = llm.generate(messages)
    >>> print(response.content)
"""

from src.llm.base_llm import BaseLLM, Message, LLMResponse, StreamChunk
from src.llm.config import (
    LLMConfig,
    OpenAIConfig,
    AzureOpenAIConfig,
    AnthropicConfig,
    GoogleConfig,
    CohereConfig,
    HuggingFaceConfig,
    DeepSeekConfig,
    get_config_class,
)
from src.llm.openai_llm import OpenAILLM
from src.llm.azure_openai_llm import AzureOpenAILLM
from src.llm.anthropic_llm import AnthropicLLM
from src.llm.huggingface_llm import HuggingFaceLLM
from src.llm.deepseek_llm import DeepSeekLLM

__all__ = [
    # Base classes
    "BaseLLM",
    "Message",
    "LLMResponse",
    "StreamChunk",
    # Configurations
    "LLMConfig",
    "OpenAIConfig",
    "AzureOpenAIConfig",
    "AnthropicConfig",
    "GoogleConfig",
    "CohereConfig",
    "HuggingFaceConfig",
    "DeepSeekConfig",
    "get_config_class",
    # Implementations
    "OpenAILLM",
    "AzureOpenAILLM",
    "AnthropicLLM",
    "HuggingFaceLLM",
    "DeepSeekLLM",
]
