"""
OpenAI LLM implementation.

This module provides integration with OpenAI's GPT models (GPT-3.5, GPT-4, etc.)
using the official OpenAI Python SDK.
"""

import os
import time
from typing import List, Dict, Any, Iterator, Union, Optional
import structlog

from src.llm.base_llm import BaseLLM, Message, LLMResponse, StreamChunk
from src.llm.config import OpenAIConfig

log = structlog.get_logger(__name__)


class OpenAILLM(BaseLLM):
    """
    OpenAI LLM implementation using official OpenAI SDK.
    
    Supports all OpenAI chat models including GPT-3.5-turbo, GPT-4, GPT-4-turbo, etc.
    
    Example:
        >>> from src.llm import OpenAILLM, OpenAIConfig
        >>> 
        >>> config = OpenAIConfig(
        ...     model="gpt-4",
        ...     temperature=0.7,
        ...     max_tokens=1000,
        ...     api_key="sk-..."  # or set OPENAI_API_KEY env var
        ... )
        >>> llm = OpenAILLM(config)
        >>> 
        >>> messages = [
        ...     {"role": "system", "content": "You are a Peru travel guide expert."},
        ...     {"role": "user", "content": "What is Machu Picchu?"}
        ... ]
        >>> 
        >>> # Standard generation
        >>> response = llm.generate(messages)
        >>> print(response.content)
        >>> print(f"Tokens used: {response.usage['total_tokens']}")
        >>> 
        >>> # Streaming generation
        >>> for chunk in llm.stream(messages):
        ...     print(chunk.content, end="", flush=True)
    """
    
    def __init__(self, config: OpenAIConfig):
        """
        Initialize OpenAI LLM.
        
        Args:
            config: OpenAIConfig with model and API settings
        """
        super().__init__(config)
        self.config: OpenAIConfig = config
        self._client: Optional[Any] = None
        self._initialize_client()
        
        log.info(
            "openai_llm_initialized",
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
    
    def _validate_config(self) -> None:
        """Validate OpenAI configuration."""
        if not self.config.model:
            raise ValueError("OpenAI model name is required")
        
        # Check for API key in config or environment
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key is required. Set config.api_key or "
                "OPENAI_API_KEY environment variable."
            )
    
    def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError(
                "OpenAI SDK not installed. Install with: pip install openai"
            ) from e
        
        # Get API key from config or environment
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize client with optional parameters
        client_kwargs = {"api_key": api_key}
        
        if self.config.organization:
            client_kwargs["organization"] = self.config.organization
        
        if self.config.base_url:
            client_kwargs["base_url"] = self.config.base_url
        
        self._client = OpenAI(**client_kwargs)
        
        log.debug(
            "openai_client_initialized",
            has_organization=bool(self.config.organization),
            has_custom_base_url=bool(self.config.base_url),
        )
    
    def generate(
        self,
        messages: List[Union[Dict[str, str], Message]],
        **kwargs: Any
    ) -> LLMResponse:
        """
        Generate response from OpenAI.
        
        Args:
            messages: Conversation messages
            **kwargs: Override config parameters (temperature, max_tokens, etc.)
        
        Returns:
            LLMResponse with generated content
        
        Raises:
            ValueError: If messages are invalid
            RuntimeError: If API call fails
        """
        # Normalize and validate messages
        normalized_messages = self._normalize_messages(messages)
        self._validate_messages(normalized_messages)
        
        # Convert to OpenAI format
        openai_messages = [msg.to_dict() for msg in normalized_messages]
        
        # Merge config with kwargs
        params = {
            "model": self.config.model,
            "messages": openai_messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "frequency_penalty": kwargs.get("frequency_penalty", self.config.frequency_penalty),
            "presence_penalty": kwargs.get("presence_penalty", self.config.presence_penalty),
        }
        
        # Add extra params
        for key, value in self.config.extra_params.items():
            if key not in params:
                params[key] = value
        
        log.info(
            "openai_generate_started",
            model=params["model"],
            num_messages=len(openai_messages),
            temperature=params["temperature"],
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
                "openai_generate_completed",
                model=response.model,
                tokens=usage["total_tokens"],
                latency_ms=round(latency_ms, 2),
                finish_reason=finish_reason,
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
                    "system_fingerprint": getattr(response, "system_fingerprint", None),
                },
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            log.error(
                "openai_generate_failed",
                model=params["model"],
                error=str(e),
                latency_ms=round(latency_ms, 2),
            )
            raise RuntimeError(f"OpenAI generation failed: {e}") from e
    
    def stream(
        self,
        messages: List[Union[Dict[str, str], Message]],
        **kwargs: Any
    ) -> Iterator[StreamChunk]:
        """
        Stream response from OpenAI.
        
        Args:
            messages: Conversation messages
            **kwargs: Override config parameters
            
        Yields:
            StreamChunk objects with incremental content
            
        Raises:
            ValueError: If messages are invalid
            RuntimeError: If streaming fails
        """
        # Normalize and validate messages
        normalized_messages = self._normalize_messages(messages)
        self._validate_messages(normalized_messages)
        
        # Convert to OpenAI format
        openai_messages = [msg.to_dict() for msg in normalized_messages]
        
        # Merge config with kwargs
        params = {
            "model": self.config.model,
            "messages": openai_messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "frequency_penalty": kwargs.get("frequency_penalty", self.config.frequency_penalty),
            "presence_penalty": kwargs.get("presence_penalty", self.config.presence_penalty),
            "stream": True,
        }
        
        # Add extra params
        for key, value in self.config.extra_params.items():
            if key not in params:
                params[key] = value
        
        log.info(
            "openai_stream_started",
            model=params["model"],
            num_messages=len(openai_messages),
        )
        
        try:
            stream = self._client.chat.completions.create(**params)
            
            chunk_count = 0
            for chunk in stream:
                if chunk.choices:
                    choice = chunk.choices[0]
                    delta = choice.delta
                    
                    # Extract content delta
                    content = delta.content or ""
                    finish_reason = choice.finish_reason
                    
                    if content or finish_reason:
                        chunk_count += 1
                        yield StreamChunk(
                            content=content,
                            finish_reason=finish_reason,
                            metadata={
                                "chunk_index": chunk_count,
                                "model": chunk.model,
                            },
                        )
            
            log.info(
                "openai_stream_completed",
                chunks=chunk_count,
            )
            
        except Exception as e:
            log.error(
                "openai_stream_failed",
                model=params["model"],
                error=str(e),
            )
            raise RuntimeError(f"OpenAI streaming failed: {e}") from e
    
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
            # Fallback: rough estimate (1 token ≈ 4 chars)
            log.warning(
                "tiktoken_not_installed",
                message="Using rough token estimate. Install tiktoken for accurate counts.",
            )
            return len(text) // 4
        
        try:
            # Get encoding for model
            encoding = tiktoken.encoding_for_model(self.config.model)
            return len(encoding.encode(text))
        except KeyError:
            # Fallback to cl100k_base for unknown models
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
    
    def count_messages_tokens(
        self,
        messages: List[Union[Dict[str, str], Message]]
    ) -> int:
        """
        Count tokens in messages including formatting overhead.
        
        Based on OpenAI's token counting guide:
        https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
        
        Args:
            messages: List of messages
            
        Returns:
            Total tokens including message formatting
        """
        normalized_messages = self._normalize_messages(messages)
        
        # Token overhead per message (varies by model)
        tokens_per_message = 3  # Default for gpt-3.5-turbo and gpt-4
        tokens_per_name = 1
        
        total_tokens = 0
        
        for msg in normalized_messages:
            total_tokens += tokens_per_message
            total_tokens += self.count_tokens(msg.content)
            total_tokens += self.count_tokens(msg.role)
            
            if msg.name:
                total_tokens += tokens_per_name
                total_tokens += self.count_tokens(msg.name)
        
        # Add overhead for assistant response priming
        total_tokens += 3
        
        return total_tokens
