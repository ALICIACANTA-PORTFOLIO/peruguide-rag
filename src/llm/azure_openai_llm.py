"""
Azure OpenAI LLM implementation.

This module provides integration with Azure OpenAI Service using the official SDK.
"""

import os
import time
from typing import List, Dict, Any, Iterator, Union, Optional
import structlog

from src.llm.base_llm import BaseLLM, Message, LLMResponse, StreamChunk
from src.llm.config import AzureOpenAIConfig

log = structlog.get_logger(__name__)


class AzureOpenAILLM(BaseLLM):
    """
    Azure OpenAI LLM implementation.
    
    Uses Azure-deployed OpenAI models with enterprise features like
    managed identity, VNet integration, and regional deployment.
    
    Example:
        >>> from src.llm import AzureOpenAILLM, AzureOpenAIConfig
        >>> 
        >>> config = AzureOpenAIConfig(
        ...     model="gpt-35-turbo",  # Azure deployment name
        ...     deployment_name="my-gpt-35-deployment",
        ...     azure_endpoint="https://my-resource.openai.azure.com",
        ...     api_key="...",  # or set AZURE_OPENAI_API_KEY
        ...     api_version="2024-02-01",
        ...     temperature=0.7,
        ... )
        >>> llm = AzureOpenAILLM(config)
        >>> 
        >>> messages = [{"role": "user", "content": "Hello!"}]
        >>> response = llm.generate(messages)
    """
    
    def __init__(self, config: AzureOpenAIConfig):
        """
        Initialize Azure OpenAI LLM.
        
        Args:
            config: AzureOpenAIConfig with deployment and endpoint settings
        """
        super().__init__(config)
        self.config: AzureOpenAIConfig = config
        self._client: Optional[Any] = None
        self._initialize_client()
        
        log.info(
            "azure_openai_llm_initialized",
            deployment=config.deployment_name,
            endpoint=config.azure_endpoint,
            api_version=config.api_version,
        )
    
    def _validate_config(self) -> None:
        """Validate Azure OpenAI configuration."""
        if not self.config.deployment_name:
            raise ValueError("Azure deployment name is required")
        
        # Check for API key
        api_key = self.config.api_key or os.getenv("AZURE_OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "Azure OpenAI API key is required. Set config.api_key or "
                "AZURE_OPENAI_API_KEY environment variable."
            )
        
        # Check for endpoint
        endpoint = self.config.azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        if not endpoint:
            raise ValueError(
                "Azure OpenAI endpoint is required. Set config.azure_endpoint or "
                "AZURE_OPENAI_ENDPOINT environment variable."
            )
    
    def _initialize_client(self) -> None:
        """Initialize Azure OpenAI client."""
        try:
            from openai import AzureOpenAI
        except ImportError as e:
            raise RuntimeError(
                "OpenAI SDK not installed. Install with: pip install openai"
            ) from e
        
        # Get credentials from config or environment
        api_key = self.config.api_key or os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = self.config.azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        
        self._client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=self.config.api_version,
        )
        
        log.debug("azure_openai_client_initialized")
    
    def generate(
        self,
        messages: List[Union[Dict[str, str], Message]],
        **kwargs: Any
    ) -> LLMResponse:
        """
        Generate response from Azure OpenAI.
        
        Args:
            messages: Conversation messages
            **kwargs: Override config parameters
        
        Returns:
            LLMResponse with generated content
        """
        # Normalize and validate messages
        normalized_messages = self._normalize_messages(messages)
        self._validate_messages(normalized_messages)
        
        # Convert to OpenAI format
        openai_messages = [msg.to_dict() for msg in normalized_messages]
        
        # Merge config with kwargs
        params = {
            "model": self.config.deployment_name,  # Azure uses deployment name
            "messages": openai_messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "frequency_penalty": kwargs.get("frequency_penalty", self.config.frequency_penalty),
            "presence_penalty": kwargs.get("presence_penalty", self.config.presence_penalty),
        }
        
        log.info(
            "azure_generate_started",
            deployment=params["model"],
            num_messages=len(openai_messages),
        )
        
        start_time = time.time()
        
        try:
            response = self._client.chat.completions.create(**params)
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response data
            choice = response.choices[0]
            content = choice.message.content or ""
            finish_reason = choice.finish_reason
            
            # Extract usage
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            
            log.info(
                "azure_generate_completed",
                deployment=response.model,
                tokens=usage["total_tokens"],
                latency_ms=round(latency_ms, 2),
            )
            
            return LLMResponse(
                content=content,
                model=response.model,
                usage=usage,
                finish_reason=finish_reason,
                latency_ms=latency_ms,
                metadata={
                    "id": response.id,
                    "created": response.created,
                },
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            log.error(
                "azure_generate_failed",
                deployment=params["model"],
                error=str(e),
                latency_ms=round(latency_ms, 2),
            )
            raise RuntimeError(f"Azure OpenAI generation failed: {e}") from e
    
    def stream(
        self,
        messages: List[Union[Dict[str, str], Message]],
        **kwargs: Any
    ) -> Iterator[StreamChunk]:
        """
        Stream response from Azure OpenAI.
        
        Args:
            messages: Conversation messages
            **kwargs: Override config parameters
            
        Yields:
            StreamChunk objects with incremental content
        """
        # Normalize and validate messages
        normalized_messages = self._normalize_messages(messages)
        self._validate_messages(normalized_messages)
        
        # Convert to OpenAI format
        openai_messages = [msg.to_dict() for msg in normalized_messages]
        
        # Merge config with kwargs
        params = {
            "model": self.config.deployment_name,
            "messages": openai_messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "frequency_penalty": kwargs.get("frequency_penalty", self.config.frequency_penalty),
            "presence_penalty": kwargs.get("presence_penalty", self.config.presence_penalty),
            "stream": True,
        }
        
        log.info(
            "azure_stream_started",
            deployment=params["model"],
            num_messages=len(openai_messages),
        )
        
        try:
            stream = self._client.chat.completions.create(**params)
            
            chunk_count = 0
            for chunk in stream:
                if chunk.choices:
                    choice = chunk.choices[0]
                    delta = choice.delta
                    
                    content = delta.content or ""
                    finish_reason = choice.finish_reason
                    
                    if content or finish_reason:
                        chunk_count += 1
                        yield StreamChunk(
                            content=content,
                            finish_reason=finish_reason,
                            metadata={"chunk_index": chunk_count},
                        )
            
            log.info("azure_stream_completed", chunks=chunk_count)
            
        except Exception as e:
            log.error(
                "azure_stream_failed",
                deployment=params["model"],
                error=str(e),
            )
            raise RuntimeError(f"Azure OpenAI streaming failed: {e}") from e
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken.
        
        Args:
            text: Text to tokenize
            
        Returns:
            Number of tokens
        """
        try:
            import tiktoken
        except ImportError:
            # Fallback: rough estimate
            return len(text) // 4
        
        try:
            # Azure models use same encodings as OpenAI
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            return len(encoding.encode(text))
        except Exception:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
    
    def count_messages_tokens(
        self,
        messages: List[Union[Dict[str, str], Message]]
    ) -> int:
        """
        Count tokens in messages including formatting overhead.
        
        Args:
            messages: List of messages
            
        Returns:
            Total tokens including message formatting
        """
        normalized_messages = self._normalize_messages(messages)
        
        tokens_per_message = 3
        tokens_per_name = 1
        total_tokens = 0
        
        for msg in normalized_messages:
            total_tokens += tokens_per_message
            total_tokens += self.count_tokens(msg.content)
            total_tokens += self.count_tokens(msg.role)
            
            if msg.name:
                total_tokens += tokens_per_name
                total_tokens += self.count_tokens(msg.name)
        
        total_tokens += 3  # Assistant response priming
        
        return total_tokens
