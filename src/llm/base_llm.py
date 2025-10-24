"""
Abstract base class for LLM providers.

This module defines the interface that all LLM implementations must follow,
ensuring consistency across different providers (OpenAI, Azure, Anthropic, etc.).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Iterator, Union
import time


@dataclass
class Message:
    """Represents a message in the conversation."""
    
    role: str
    """Message role: 'system', 'user', or 'assistant'"""
    
    content: str
    """Message content/text"""
    
    name: Optional[str] = None
    """Optional name for the message sender"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class LLMResponse:
    """Response from LLM generation."""
    
    content: str
    """Generated text content"""
    
    model: str
    """Model used for generation"""
    
    usage: Dict[str, int]
    """Token usage statistics (prompt_tokens, completion_tokens, total_tokens)"""
    
    finish_reason: str
    """Reason for completion: 'stop', 'length', 'content_filter', etc."""
    
    latency_ms: float
    """Response latency in milliseconds"""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional provider-specific metadata"""
    
    def __repr__(self) -> str:
        """String representation of response."""
        tokens = self.usage.get("total_tokens", 0)
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return (
            f"LLMResponse(model={self.model}, tokens={tokens}, "
            f"latency={self.latency_ms:.0f}ms, content='{preview}')"
        )


@dataclass
class StreamChunk:
    """Chunk from streaming LLM generation."""
    
    content: str
    """Text content in this chunk (delta)"""
    
    finish_reason: Optional[str] = None
    """Finish reason if this is the last chunk"""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional chunk metadata"""


class BaseLLM(ABC):
    """
    Abstract base class for Large Language Model providers.
    
    All LLM implementations must inherit from this class and implement
    the abstract methods. This ensures a consistent interface across
    different providers (OpenAI, Azure, Anthropic, Google, etc.).
    
    Example:
        >>> # Using OpenAI implementation
        >>> from src.llm import OpenAILLM, OpenAIConfig
        >>> config = OpenAIConfig(model="gpt-4", temperature=0.7)
        >>> llm = OpenAILLM(config)
        >>> 
        >>> messages = [
        ...     {"role": "system", "content": "You are a helpful assistant."},
        ...     {"role": "user", "content": "What is 2+2?"}
        ... ]
        >>> response = llm.generate(messages)
        >>> print(response.content)
        
        >>> # Streaming example
        >>> for chunk in llm.stream(messages):
        ...     print(chunk.content, end="", flush=True)
    """
    
    def __init__(self, config: Any):
        """
        Initialize LLM with configuration.
        
        Args:
            config: Provider-specific configuration object
        """
        self.config = config
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """
        Validate provider-specific configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    def generate(
        self,
        messages: List[Union[Dict[str, str], Message]],
        **kwargs: Any
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional generation parameters (overrides config)
        
        Returns:
            LLMResponse with generated content and metadata
            
        Raises:
            ValueError: If messages are invalid
            RuntimeError: If generation fails
            
        Example:
            >>> messages = [
            ...     {"role": "system", "content": "You are helpful."},
            ...     {"role": "user", "content": "Hello!"}
            ... ]
            >>> response = llm.generate(messages, temperature=0.5)
        """
        pass
    
    @abstractmethod
    def stream(
        self,
        messages: List[Union[Dict[str, str], Message]],
        **kwargs: Any
    ) -> Iterator[StreamChunk]:
        """
        Generate a streaming response from the LLM.
        
        Args:
            messages: List of conversation messages
            **kwargs: Additional generation parameters (overrides config)
            
        Yields:
            StreamChunk objects with incremental content
            
        Raises:
            ValueError: If messages are invalid
            RuntimeError: If streaming fails
            
        Example:
            >>> messages = [{"role": "user", "content": "Write a story"}]
            >>> for chunk in llm.stream(messages):
            ...     print(chunk.content, end="", flush=True)
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using provider's tokenizer.
        
        Args:
            text: Text to tokenize
            
        Returns:
            Number of tokens
            
        Example:
            >>> llm.count_tokens("Hello, world!")
            4
        """
        pass
    
    @abstractmethod
    def count_messages_tokens(
        self,
        messages: List[Union[Dict[str, str], Message]]
    ) -> int:
        """
        Count tokens in a list of messages.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Total number of tokens including message formatting
            
        Example:
            >>> messages = [
            ...     {"role": "system", "content": "You are helpful."},
            ...     {"role": "user", "content": "Hi!"}
            ... ]
            >>> llm.count_messages_tokens(messages)
            15
        """
        pass
    
    def _normalize_messages(
        self,
        messages: List[Union[Dict[str, str], Message]]
    ) -> List[Message]:
        """
        Normalize messages to Message objects.
        
        Args:
            messages: List of messages (dicts or Message objects)
            
        Returns:
            List of Message objects
            
        Raises:
            ValueError: If message format is invalid
        """
        normalized = []
        for msg in messages:
            if isinstance(msg, Message):
                normalized.append(msg)
            elif isinstance(msg, dict):
                if "role" not in msg or "content" not in msg:
                    raise ValueError(
                        f"Message dict must have 'role' and 'content' keys. Got: {msg}"
                    )
                normalized.append(
                    Message(
                        role=msg["role"],
                        content=msg["content"],
                        name=msg.get("name")
                    )
                )
            else:
                raise ValueError(
                    f"Message must be dict or Message object. Got: {type(msg)}"
                )
        
        return normalized
    
    def _validate_messages(self, messages: List[Message]) -> None:
        """
        Validate message list.
        
        Args:
            messages: List of Message objects
            
        Raises:
            ValueError: If messages are invalid
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")
        
        valid_roles = {"system", "user", "assistant"}
        for i, msg in enumerate(messages):
            if msg.role not in valid_roles:
                raise ValueError(
                    f"Invalid role '{msg.role}' at index {i}. "
                    f"Must be one of: {valid_roles}"
                )
            
            if not msg.content or not msg.content.strip():
                raise ValueError(f"Message content cannot be empty at index {i}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "provider": self.__class__.__name__.replace("LLM", "").lower(),
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
    
    def __repr__(self) -> str:
        """String representation of LLM."""
        provider = self.__class__.__name__
        model = self.config.model
        return f"{provider}(model={model})"
