"""DeepSeek LLM implementation."""

import os
import time
from typing import Any, Dict, Generator, List, Optional, Union

import structlog

from .base_llm import BaseLLM, LLMResponse, Message, StreamChunk
from .config import DeepSeekConfig

log = structlog.get_logger()


class DeepSeekLLM(BaseLLM):
    """
    DeepSeek LLM implementation.
    
    DeepSeek uses OpenAI-compatible API, so this implementation is similar
    to OpenAI but with DeepSeek-specific models and endpoint.
    
    Supported models:
    - deepseek-chat: DeepSeek's chat model
    - deepseek-coder: DeepSeek's coding model
    
    Example:
        >>> from src.llm import DeepSeekLLM, DeepSeekConfig
        >>> 
        >>> config = DeepSeekConfig(
        ...     model="deepseek-chat",
        ...     temperature=0.7,
        ...     max_tokens=1000
        ... )
        >>> llm = DeepSeekLLM(config)
        >>> 
        >>> messages = [{"role": "user", "content": "Hello!"}]
        >>> response = llm.generate(messages)
        >>> print(response.content)
    """
    
    def __init__(self, config: DeepSeekConfig):
        """
        Initialize DeepSeek LLM.
        
        Args:
            config: DeepSeek configuration
            
        Raises:
            RuntimeError: If openai package is not installed
        """
        super().__init__(config)
        self._client = None
        self._initialize_client()
        
        log.info(
            "deepseek_llm_initialized",
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
    
    def _validate_config(self) -> None:
        """Validate DeepSeek configuration."""
        if not self.config.api_key:
            # Check environment variable
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError(
                    "DeepSeek API key is required. Set it in config or DEEPSEEK_API_KEY environment variable."
                )
    
    def _initialize_client(self) -> None:
        """Initialize DeepSeek client (using OpenAI SDK)."""
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError(
                "OpenAI package is required for DeepSeek. Install with: pip install openai"
            ) from e
        
        # Get API key from config or environment
        api_key = self.config.api_key or os.getenv("DEEPSEEK_API_KEY")
        
        self._client = OpenAI(
            api_key=api_key,
            base_url=self.config.base_url,
        )
        
        log.debug("deepseek_client_initialized", base_url=self.config.base_url)
    
    def generate(
        self,
        messages: Union[List[Dict[str, str]], List[Message]],
        **kwargs: Any
    ) -> LLMResponse:
        """
        Generate completion using DeepSeek.
        
        Args:
            messages: List of message dicts or Message objects
            **kwargs: Additional generation parameters
            
        Returns:
            LLMResponse with generated content
        """
        # Normalize and validate messages
        normalized = self._normalize_messages(messages)
        self._validate_messages(normalized)
        
        # Convert to OpenAI format
        openai_messages = [msg.to_dict() for msg in normalized]
        
        # Build parameters
        params = {
            "model": self.config.model,
            "messages": openai_messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "frequency_penalty": kwargs.get("frequency_penalty", self.config.frequency_penalty),
            "presence_penalty": kwargs.get("presence_penalty", self.config.presence_penalty),
        }
        
        # Add extra parameters
        params.update(self.config.extra_params)
        
        log.info(
            "deepseek_generate_started",
            model=params["model"],
            num_messages=len(openai_messages),
        )
        
        start_time = time.time()
        
        try:
            response = self._client.chat.completions.create(**params)
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract content
            content = response.choices[0].message.content or ""
            
            # Extract usage
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            
            log.info(
                "deepseek_generate_completed",
                model=response.model,
                tokens=usage["total_tokens"],
                latency_ms=round(latency_ms, 2),
            )
            
            return LLMResponse(
                content=content,
                model=response.model,
                usage=usage,
                finish_reason=response.choices[0].finish_reason or "stop",
                latency_ms=latency_ms,
                metadata={"id": response.id},
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            log.error(
                "deepseek_generate_failed",
                model=params["model"],
                error=str(e),
                latency_ms=round(latency_ms, 2),
            )
            raise RuntimeError(f"DeepSeek generation failed: {e}") from e
    
    def stream(
        self,
        messages: Union[List[Dict[str, str]], List[Message]],
        **kwargs: Any
    ) -> Generator[StreamChunk, None, None]:
        """
        Stream completion using DeepSeek.
        
        Args:
            messages: List of message dicts or Message objects
            **kwargs: Additional generation parameters
            
        Yields:
            StreamChunk objects with incremental content
        """
        # Normalize and validate messages
        normalized = self._normalize_messages(messages)
        self._validate_messages(normalized)
        
        # Convert to OpenAI format
        openai_messages = [msg.to_dict() for msg in normalized]
        
        # Build parameters
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
        
        # Add extra parameters
        params.update(self.config.extra_params)
        
        log.info(
            "deepseek_stream_started",
            model=params["model"],
            num_messages=len(openai_messages),
        )
        
        try:
            stream = self._client.chat.completions.create(**params)
            
            chunk_count = 0
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    finish_reason = chunk.choices[0].finish_reason
                    
                    content = delta.content if hasattr(delta, "content") else ""
                    
                    if content or finish_reason:
                        chunk_count += 1
                        yield StreamChunk(
                            content=content or "",
                            finish_reason=finish_reason,
                            metadata={
                                "chunk_index": chunk_count,
                                "model": chunk.model if hasattr(chunk, "model") else self.config.model,
                            },
                        )
            
            log.info("deepseek_stream_completed", chunks=chunk_count)
            
        except Exception as e:
            log.error(
                "deepseek_stream_failed",
                model=params["model"],
                error=str(e),
            )
            raise RuntimeError(f"DeepSeek streaming failed: {e}") from e
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Uses tiktoken if available, otherwise approximates.
        
        Args:
            text: Text to tokenize
            
        Returns:
            Number of tokens
        """
        try:
            import tiktoken
            
            # Use cl100k_base encoding (similar to GPT-4)
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            # Fallback: approximate 1 token ≈ 4 characters
            log.debug("tiktoken_not_available", using_approximation=True)
            return len(text) // 4
    
    def count_messages_tokens(self, messages: List[Union[Dict[str, str], Message]]) -> int:
        """
        Count tokens in messages.
        
        Args:
            messages: List of messages to count tokens for
            
        Returns:
            Approximate number of tokens
        """
        normalized = self._normalize_messages(messages)
        
        # Count tokens in each message
        total_tokens = 0
        for msg in normalized:
            # Content tokens
            total_tokens += self.count_tokens(msg.content)
            
            # Role tokens (approximate)
            total_tokens += self.count_tokens(msg.role)
            
            # Message overhead (approximate 4 tokens per message)
            total_tokens += 4
        
        # Add conversation overhead
        total_tokens += 3
        
        return total_tokens
    
    def __repr__(self) -> str:
        """String representation."""
        return f"DeepSeekLLM(model={self.config.model})"
