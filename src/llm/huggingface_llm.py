"""Hugging Face LLM implementation."""

import os
import time
from typing import Any, Dict, Generator, List, Optional, Union

import structlog

from .base_llm import BaseLLM, LLMResponse, Message, StreamChunk
from .config import HuggingFaceConfig

log = structlog.get_logger()


class HuggingFaceLLM(BaseLLM):
    """
    Hugging Face LLM implementation supporting Inference API and custom endpoints.
    
    Supports both Hugging Face's Inference API and custom inference endpoints
    for text generation tasks.
    
    Example:
        >>> from src.llm import HuggingFaceLLM, HuggingFaceConfig
        >>> 
        >>> # Using Inference API
        >>> config = HuggingFaceConfig(
        ...     model="meta-llama/Llama-2-7b-chat-hf",
        ...     temperature=0.7,
        ...     max_tokens=500
        ... )
        >>> llm = HuggingFaceLLM(config)
        >>> 
        >>> # Generate response
        >>> messages = [{"role": "user", "content": "Hello!"}]
        >>> response = llm.generate(messages)
        >>> print(response.content)
        
        >>> # Using custom endpoint
        >>> config = HuggingFaceConfig(
        ...     model="my-model",
        ...     endpoint_url="https://my-endpoint.aws.endpoints.huggingface.cloud"
        ... )
        >>> llm = HuggingFaceLLM(config)
    """
    
    def __init__(self, config: HuggingFaceConfig):
        """
        Initialize Hugging Face LLM.
        
        Args:
            config: Hugging Face configuration
            
        Raises:
            RuntimeError: If huggingface_hub is not installed
        """
        super().__init__(config)
        self._client = None
        self._initialize_client()
        
        log.info(
            "huggingface_llm_initialized",
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            has_endpoint=bool(self.config.endpoint_url),
        )
    
    def _validate_config(self) -> None:
        """Validate Hugging Face configuration."""
        # Check for API token
        api_key = self.config.api_key or os.getenv("HUGGINGFACE_API_TOKEN") or os.getenv("HF_TOKEN")
        if not api_key:
            raise ValueError(
                "Hugging Face API token is required. Set config.api_key or "
                "HUGGINGFACE_API_TOKEN/HF_TOKEN environment variable."
            )
    
    def _initialize_client(self) -> None:
        """Initialize Hugging Face inference client."""
        try:
            from huggingface_hub import InferenceClient
        except ImportError as e:
            raise RuntimeError(
                "Hugging Face Hub not installed. Install with: pip install huggingface_hub"
            ) from e
        
        api_key = self.config.api_key or os.getenv("HUGGINGFACE_API_TOKEN") or os.getenv("HF_TOKEN")
        
        # Initialize client with optional custom endpoint
        if self.config.endpoint_url:
            self._client = InferenceClient(
                model=self.config.endpoint_url,
                token=api_key
            )
            log.debug(
                "huggingface_client_initialized",
                endpoint=self.config.endpoint_url
            )
        else:
            self._client = InferenceClient(
                model=self.config.model,
                token=api_key
            )
            log.debug(
                "huggingface_client_initialized",
                model=self.config.model
            )
    
    def _format_messages_for_hf(self, messages: List[Message]) -> str:
        """
        Format messages for Hugging Face models.
        
        Most HF models expect a simple text prompt, not chat messages.
        This method converts chat messages to a single prompt string.
        
        Args:
            messages: List of Message objects
            
        Returns:
            Formatted prompt string
        """
        # Check if model supports chat format (e.g., Llama-2-chat, Mistral-Instruct)
        model_lower = self.config.model.lower()
        is_chat_model = any(x in model_lower for x in ["chat", "instruct", "assistant"])
        
        if is_chat_model and "llama-2" in model_lower:
            # Llama-2-chat format
            prompt_parts = []
            for msg in messages:
                if msg.role == "system":
                    prompt_parts.append(f"<<SYS>>\n{msg.content}\n<</SYS>>\n")
                elif msg.role == "user":
                    prompt_parts.append(f"[INST] {msg.content} [/INST]")
                elif msg.role == "assistant":
                    prompt_parts.append(f"{msg.content}")
            return "\n".join(prompt_parts)
        
        elif is_chat_model:
            # Generic chat format
            prompt_parts = []
            for msg in messages:
                if msg.role == "system":
                    prompt_parts.append(f"System: {msg.content}")
                elif msg.role == "user":
                    prompt_parts.append(f"User: {msg.content}")
                elif msg.role == "assistant":
                    prompt_parts.append(f"Assistant: {msg.content}")
            prompt_parts.append("Assistant:")  # Prompt for response
            return "\n\n".join(prompt_parts)
        
        else:
            # Simple concatenation for non-chat models
            return "\n".join(msg.content for msg in messages)
    
    def generate(
        self,
        messages: Union[List[Dict[str, str]], List[Message]],
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion using Hugging Face Inference API.
        
        Args:
            messages: List of message dicts or Message objects
            **kwargs: Additional generation parameters (override config)
            
        Returns:
            LLMResponse with generated text and metadata
            
        Raises:
            RuntimeError: If generation fails
        """
        normalized = self._normalize_messages(messages)
        self._validate_messages(normalized)
        
        # Format messages to prompt
        prompt = self._format_messages_for_hf(normalized)
        
        # Prepare generation parameters
        params = {
            "max_new_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "do_sample": True if self.config.temperature > 0 else False,
        }
        
        # Add any extra parameters from config
        params.update(self.config.extra_params)
        
        log.info(
            "huggingface_generate_started",
            model=self.config.model,
            prompt_length=len(prompt),
            params=params,
        )
        
        start_time = time.time()
        
        try:
            # Call Hugging Face inference
            response = self._client.text_generation(
                prompt,
                **params,
                return_full_text=False,
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract text from response
            if isinstance(response, str):
                content = response
            else:
                content = response.get("generated_text", str(response))
            
            log.info(
                "huggingface_generate_completed",
                latency_ms=latency_ms,
                response_length=len(content),
            )
            
            return LLMResponse(
                content=content,
                model=self.config.model,
                finish_reason="stop",  # HF doesn't provide finish reason
                usage={
                    "prompt_tokens": self.count_tokens(prompt),
                    "completion_tokens": self.count_tokens(content),
                    "total_tokens": self.count_tokens(prompt) + self.count_tokens(content),
                },
                latency_ms=latency_ms,
                metadata={
                    "endpoint": self.config.endpoint_url,
                }
            )
            
        except Exception as e:
            log.error("huggingface_generate_failed", error=str(e))
            raise RuntimeError(f"Hugging Face generation failed: {e}") from e
    
    def stream(
        self,
        messages: Union[List[Dict[str, str]], List[Message]],
        **kwargs
    ) -> Generator[StreamChunk, None, None]:
        """
        Stream completion using Hugging Face Inference API.
        
        Note: Streaming support depends on the model and endpoint.
        Not all Hugging Face models support streaming.
        
        Args:
            messages: List of message dicts or Message objects
            **kwargs: Additional generation parameters
            
        Yields:
            StreamChunk objects with generated text
            
        Raises:
            RuntimeError: If streaming fails
        """
        normalized = self._normalize_messages(messages)
        self._validate_messages(normalized)
        
        # Format messages to prompt
        prompt = self._format_messages_for_hf(normalized)
        
        # Prepare generation parameters
        params = {
            "max_new_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "do_sample": True if self.config.temperature > 0 else False,
        }
        
        # Add any extra parameters
        params.update(self.config.extra_params)
        
        log.info(
            "huggingface_stream_started",
            model=self.config.model,
            prompt_length=len(prompt),
        )
        
        try:
            # Stream generation
            stream = self._client.text_generation(
                prompt,
                **params,
                stream=True,
                return_full_text=False,
            )
            
            chunk_count = 0
            for chunk_data in stream:
                # Extract token from chunk
                if hasattr(chunk_data, 'token'):
                    content = chunk_data.token.text
                    finish_reason = "stop" if chunk_data.token.special else None
                else:
                    content = str(chunk_data)
                    finish_reason = None
                
                chunk_count += 1
                
                yield StreamChunk(
                    content=content,
                    finish_reason=finish_reason,
                    metadata={
                        "chunk_index": chunk_count,
                        "model": self.config.model
                    }
                )
            
            log.info(
                "huggingface_stream_completed",
                chunks_generated=chunk_count,
            )
            
        except Exception as e:
            log.error("huggingface_stream_failed", error=str(e))
            raise RuntimeError(f"Hugging Face streaming failed: {e}") from e
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Uses rough estimation (1 token ≈ 4 characters) since tokenizer
        varies by model and loading full tokenizer is expensive.
        
        Args:
            text: Text to tokenize
            
        Returns:
            Approximate number of tokens
        """
        # Rough estimation: 1 token ≈ 4 characters
        # This is a simplification; actual tokenization varies by model
        return len(text) // 4
    
    def count_messages_tokens(self, messages: List[Union[Dict[str, str], Message]]) -> int:
        """
        Count tokens in messages.
        
        Uses rough estimation by formatting messages and counting text length.
        
        Args:
            messages: List of messages to count tokens for
            
        Returns:
            Approximate number of tokens
        """
        # Format messages as they would be sent to the API
        formatted_prompt = self._format_messages_for_hf([
            msg if isinstance(msg, Message) else Message(**msg)
            for msg in messages
        ])
        
        # Count tokens in formatted prompt
        return self.count_tokens(formatted_prompt)
    
    def __repr__(self) -> str:
        """String representation."""
        endpoint_info = f", endpoint={self.config.endpoint_url}" if self.config.endpoint_url else ""
        return f"HuggingFaceLLM(model={self.config.model}{endpoint_info})"
