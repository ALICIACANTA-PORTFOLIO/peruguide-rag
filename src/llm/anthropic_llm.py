"""
Anthropic Claude LLM implementation.

This module provides integration with Anthropic's Claude models
using the official Anthropic SDK.
"""

import os
import time
from typing import List, Dict, Any, Iterator, Union, Optional
import structlog

from src.llm.base_llm import BaseLLM, Message, LLMResponse, StreamChunk
from src.llm.config import AnthropicConfig

log = structlog.get_logger(__name__)


class AnthropicLLM(BaseLLM):
    """
    Anthropic Claude LLM implementation.
    
    Supports Claude models including Claude 3 Opus, Sonnet, and Haiku.
    
    Example:
        >>> from src.llm import AnthropicLLM, AnthropicConfig
        >>> 
        >>> config = AnthropicConfig(
        ...     model="claude-3-sonnet-20240229",
        ...     temperature=0.7,
        ...     max_tokens=1000,
        ...     api_key="sk-ant-..."  # or set ANTHROPIC_API_KEY
        ... )
        >>> llm = AnthropicLLM(config)
        >>> 
        >>> messages = [{"role": "user", "content": "Hello!"}]
        >>> response = llm.generate(messages)
        >>> 
        >>> # Streaming
        >>> for chunk in llm.stream(messages):
        ...     print(chunk.content, end="", flush=True)
    """
    
    def __init__(self, config: AnthropicConfig):
        """
        Initialize Anthropic LLM.
        
        Args:
            config: AnthropicConfig with model and API settings
        """
        super().__init__(config)
        self.config: AnthropicConfig = config
        self._client: Optional[Any] = None
        self._initialize_client()
        
        log.info(
            "anthropic_llm_initialized",
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
    
    def _validate_config(self) -> None:
        """Validate Anthropic configuration."""
        if not self.config.model:
            raise ValueError("Anthropic model name is required")
        
        # Check for API key
        api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "Anthropic API key is required. Set config.api_key or "
                "ANTHROPIC_API_KEY environment variable."
            )
    
    def _initialize_client(self) -> None:
        """Initialize Anthropic client."""
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise RuntimeError(
                "Anthropic SDK not installed. Install with: pip install anthropic"
            ) from e
        
        # Get API key from config or environment
        api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
        
        self._client = Anthropic(api_key=api_key)
        
        log.debug("anthropic_client_initialized")
    
    def _extract_system_message(
        self,
        messages: List[Message]
    ) -> tuple[Optional[str], List[Message]]:
        """
        Extract system message from messages.
        
        Anthropic handles system message separately from conversation messages.
        
        Args:
            messages: List of messages
            
        Returns:
            Tuple of (system_message, remaining_messages)
        """
        system_message = None
        remaining_messages = []
        
        for msg in messages:
            if msg.role == "system":
                # Concatenate multiple system messages
                if system_message:
                    system_message += "\n\n" + msg.content
                else:
                    system_message = msg.content
            else:
                remaining_messages.append(msg)
        
        return system_message, remaining_messages
    
    def generate(
        self,
        messages: List[Union[Dict[str, str], Message]],
        **kwargs: Any
    ) -> LLMResponse:
        """
        Generate response from Anthropic Claude.
        
        Args:
            messages: Conversation messages
            **kwargs: Override config parameters
        
        Returns:
            LLMResponse with generated content
        """
        # Normalize and validate messages
        normalized_messages = self._normalize_messages(messages)
        self._validate_messages(normalized_messages)
        
        # Extract system message (Anthropic handles it separately)
        system_message, conversation_messages = self._extract_system_message(
            normalized_messages
        )
        
        # Convert to Anthropic format
        anthropic_messages = [msg.to_dict() for msg in conversation_messages]
        
        # Build parameters
        params = {
            "model": self.config.model,
            "messages": anthropic_messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", self.config.top_p),
        }
        
        if system_message:
            params["system"] = system_message
        
        log.info(
            "anthropic_generate_started",
            model=params["model"],
            num_messages=len(anthropic_messages),
            has_system=bool(system_message),
        )
        
        start_time = time.time()
        
        try:
            response = self._client.messages.create(**params)
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract content (Anthropic returns list of content blocks)
            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text
            
            # Extract usage
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }
            
            log.info(
                "anthropic_generate_completed",
                model=response.model,
                tokens=usage["total_tokens"],
                latency_ms=round(latency_ms, 2),
                stop_reason=response.stop_reason,
            )
            
            return LLMResponse(
                content=content,
                model=response.model,
                usage=usage,
                finish_reason=response.stop_reason or "stop",
                latency_ms=latency_ms,
                metadata={
                    "id": response.id,
                    "type": response.type,
                    "role": response.role,
                },
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            log.error(
                "anthropic_generate_failed",
                model=params["model"],
                error=str(e),
                latency_ms=round(latency_ms, 2),
            )
            raise RuntimeError(f"Anthropic generation failed: {e}") from e
    
    def stream(
        self,
        messages: List[Union[Dict[str, str], Message]],
        **kwargs: Any
    ) -> Iterator[StreamChunk]:
        """
        Stream response from Anthropic Claude.
        
        Args:
            messages: Conversation messages
            **kwargs: Override config parameters
            
        Yields:
            StreamChunk objects with incremental content
        """
        # Normalize and validate messages
        normalized_messages = self._normalize_messages(messages)
        self._validate_messages(normalized_messages)
        
        # Extract system message
        system_message, conversation_messages = self._extract_system_message(
            normalized_messages
        )
        
        # Convert to Anthropic format
        anthropic_messages = [msg.to_dict() for msg in conversation_messages]
        
        # Build parameters
        params = {
            "model": self.config.model,
            "messages": anthropic_messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "stream": True,
        }
        
        if system_message:
            params["system"] = system_message
        
        log.info(
            "anthropic_stream_started",
            model=params["model"],
            num_messages=len(anthropic_messages),
        )
        
        try:
            stream = self._client.messages.create(**params)
            
            chunk_count = 0
            for event in stream:
                # Anthropic streaming events
                if event.type == "content_block_delta":
                    if hasattr(event.delta, "text"):
                        chunk_count += 1
                        yield StreamChunk(
                            content=event.delta.text,
                            finish_reason=None,
                            metadata={
                                "chunk_index": chunk_count,
                                "event_type": event.type,
                            },
                        )
                
                elif event.type == "message_stop":
                    # Final chunk with finish reason
                    yield StreamChunk(
                        content="",
                        finish_reason="stop",
                        metadata={
                            "chunk_index": chunk_count + 1,
                            "event_type": event.type,
                        },
                    )
            
            log.info("anthropic_stream_completed", chunks=chunk_count)
            
        except Exception as e:
            log.error(
                "anthropic_stream_failed",
                model=params["model"],
                error=str(e),
            )
            raise RuntimeError(f"Anthropic streaming failed: {e}") from e
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Note: Anthropic uses their own tokenizer. This is an approximation
        based on Claude's average token-to-character ratio (~3.5 chars/token).
        For exact counts, use Anthropic's token counting API.
        
        Args:
            text: Text to tokenize
            
        Returns:
            Approximate number of tokens
        """
        # Rough approximation: ~3.5 characters per token for Claude
        return len(text) // 3.5
    
    def count_messages_tokens(
        self,
        messages: List[Union[Dict[str, str], Message]]
    ) -> int:
        """
        Count tokens in messages.
        
        Args:
            messages: List of messages
            
        Returns:
            Approximate total tokens
        """
        normalized_messages = self._normalize_messages(messages)
        
        total_tokens = 0
        
        for msg in normalized_messages:
            # Add tokens for role
            total_tokens += 3
            
            # Add tokens for content
            total_tokens += self.count_tokens(msg.content)
        
        # Add overhead
        total_tokens += 5
        
        return int(total_tokens)
