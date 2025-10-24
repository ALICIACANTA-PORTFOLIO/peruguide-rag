"""
Text Cleaning Module.

This module provides text cleaning functionality with configurable rules.
Designed to be domain-agnostic and work with any type of text content.

Design Principles:
- Configurable cleaning rules
- Domain-agnostic (works with tourism, legal, academic, etc.)
- Composable cleaning functions
- Structured logging for debugging
- Type-safe with proper annotations

References:
- LLM Engineer's Handbook: Chapter 3 (Data Preprocessing)
- Clean Architecture: Dependency Inversion Principle
"""

import logging
import re
from typing import Callable, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class TextCleaner:
    """
    Domain-agnostic text cleaner with configurable rules.

    This class provides text cleaning functionality that can be customized
    through configuration. It works with any type of text content and doesn't
    make assumptions about the domain.

    Attributes:
        cleaning_rules: List of cleaning rule names to apply.
        custom_patterns: Dictionary of custom regex patterns to remove.
        preserve_newlines: Whether to preserve newline characters.
        min_length: Minimum text length after cleaning (0 = no limit).

    Example:
        >>> cleaner = TextCleaner(
        ...     cleaning_rules=["remove_urls", "normalize_spaces"],
        ...     min_length=10
        ... )
        >>> text = "Check this: https://example.com   Multiple  spaces"
        >>> clean_text = cleaner.clean(text)
        >>> print(clean_text)
        'Check this: Multiple spaces'

        >>> # Custom domain-specific patterns
        >>> legal_cleaner = TextCleaner(
        ...     cleaning_rules=["normalize_spaces"],
        ...     custom_patterns={"case_number": r"Case\\s+#\\d+-\\d+"}
        ... )
    """

    # Default cleaning patterns
    _DEFAULT_PATTERNS = {
        "urls": r"https?://\S+|www\.\S+",
        "emails": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone_numbers": r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}",
        "special_chars": r"[^\w\s\n.,;:!?¿¡áéíóúÁÉÍÓÚñÑüÜ-]",
        "extra_spaces": r"\s{2,}",
        "leading_trailing_spaces": r"^\s+|\s+$",
        "multiple_newlines": r"\n{3,}",
        "html_tags": r"<[^>]+>",
        "control_chars": r"[\x00-\x1f\x7f-\x9f]",
    }

    # Available cleaning rules
    _AVAILABLE_RULES = [
        "remove_urls",
        "remove_emails",
        "remove_phone_numbers",
        "remove_special_chars",
        "remove_html_tags",
        "remove_control_chars",
        "normalize_spaces",
        "normalize_newlines",
        "trim",
    ]

    def __init__(
        self,
        cleaning_rules: Optional[List[str]] = None,
        custom_patterns: Optional[Dict[str, str]] = None,
        preserve_newlines: bool = True,
        min_length: int = 0,
    ):
        """
        Initialize TextCleaner.

        Args:
            cleaning_rules: List of cleaning rule names to apply.
                           If None, applies default rules.
            custom_patterns: Dictionary of custom regex patterns to remove.
                           Format: {"name": "regex_pattern"}
            preserve_newlines: Whether to preserve newline characters.
            min_length: Minimum text length after cleaning (0 = no limit).

        Raises:
            ValueError: If invalid cleaning rule is specified.

        Example:
            >>> cleaner = TextCleaner(
            ...     cleaning_rules=["remove_urls", "normalize_spaces"],
            ...     custom_patterns={"custom": r"\\[REDACTED\\]"},
            ...     preserve_newlines=True,
            ...     min_length=10
            ... )
        """
        # Default rules if none specified
        if cleaning_rules is None:
            cleaning_rules = [
                "remove_urls",
                "remove_html_tags",
                "remove_control_chars",
                "normalize_spaces",
                "normalize_newlines",
                "trim",
            ]

        # Validate cleaning rules
        invalid_rules = [r for r in cleaning_rules if r not in self._AVAILABLE_RULES]
        if invalid_rules:
            raise ValueError(
                f"Invalid cleaning rules: {invalid_rules}. "
                f"Available rules: {self._AVAILABLE_RULES}"
            )

        self.cleaning_rules = cleaning_rules
        self.custom_patterns = custom_patterns or {}
        self.preserve_newlines = preserve_newlines
        self.min_length = min_length

        logger.info(
            "TextCleaner initialized",
            extra={
                "cleaning_rules": self.cleaning_rules,
                "custom_patterns": list(self.custom_patterns.keys()),
                "preserve_newlines": self.preserve_newlines,
                "min_length": self.min_length,
            },
        )

    def clean(self, text: str) -> str:
        """
        Clean text according to configured rules.

        Args:
            text: Input text to clean.

        Returns:
            Cleaned text string.

        Example:
            >>> cleaner = TextCleaner()
            >>> text = "Hello   world!  Visit: https://example.com"
            >>> cleaned = cleaner.clean(text)
            >>> print(cleaned)
            'Hello world! Visit:'
        """
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided", extra={"text_type": type(text)})
            return ""

        original_length = len(text)
        cleaned_text = text

        # Apply cleaning rules in order
        for rule in self.cleaning_rules:
            cleaned_text = self._apply_rule(rule, cleaned_text)

        # Apply custom patterns
        for pattern_name, pattern in self.custom_patterns.items():
            cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE)
            logger.debug(
                "Applied custom pattern",
                extra={"pattern_name": pattern_name, "pattern": pattern},
            )

        # Check minimum length
        if self.min_length > 0 and len(cleaned_text.strip()) < self.min_length:
            logger.warning(
                "Text below minimum length after cleaning",
                extra={
                    "original_length": original_length,
                    "cleaned_length": len(cleaned_text.strip()),
                    "min_length": self.min_length,
                },
            )
            return ""

        logger.debug(
            "Text cleaned successfully",
            extra={
                "original_length": original_length,
                "cleaned_length": len(cleaned_text),
                "reduction_pct": round((1 - len(cleaned_text) / original_length) * 100, 2)
                if original_length > 0
                else 0,
            },
        )

        return cleaned_text

    def clean_batch(self, texts: List[str]) -> List[str]:
        """
        Clean multiple texts in batch.

        Args:
            texts: List of texts to clean.

        Returns:
            List of cleaned texts.

        Example:
            >>> cleaner = TextCleaner()
            >>> texts = ["Text 1 https://url.com", "Text 2   spaces"]
            >>> cleaned = cleaner.clean_batch(texts)
            >>> print(cleaned)
            ['Text 1', 'Text 2 spaces']
        """
        if not texts:
            return []

        cleaned_texts = [self.clean(text) for text in texts]

        logger.info(
            "Batch cleaning completed",
            extra={
                "total_texts": len(texts),
                "cleaned_texts": len([t for t in cleaned_texts if t]),
                "empty_after_cleaning": len([t for t in cleaned_texts if not t]),
            },
        )

        return cleaned_texts

    def _apply_rule(self, rule: str, text: str) -> str:
        """
        Apply a specific cleaning rule to text.

        Args:
            rule: Name of the cleaning rule.
            text: Input text.

        Returns:
            Text after applying the rule.
        """
        if rule == "remove_urls":
            return re.sub(self._DEFAULT_PATTERNS["urls"], "", text)

        elif rule == "remove_emails":
            return re.sub(self._DEFAULT_PATTERNS["emails"], "", text)

        elif rule == "remove_phone_numbers":
            return re.sub(self._DEFAULT_PATTERNS["phone_numbers"], "", text)

        elif rule == "remove_special_chars":
            return re.sub(self._DEFAULT_PATTERNS["special_chars"], "", text)

        elif rule == "remove_html_tags":
            return re.sub(self._DEFAULT_PATTERNS["html_tags"], "", text)

        elif rule == "remove_control_chars":
            return re.sub(self._DEFAULT_PATTERNS["control_chars"], "", text)

        elif rule == "normalize_spaces":
            # Collapse multiple spaces into one
            text = re.sub(self._DEFAULT_PATTERNS["extra_spaces"], " ", text)
            return text

        elif rule == "normalize_newlines":
            if self.preserve_newlines:
                # Keep newlines but collapse multiple ones
                text = re.sub(self._DEFAULT_PATTERNS["multiple_newlines"], "\n\n", text)
            else:
                # Replace newlines with spaces
                text = text.replace("\n", " ")
                text = re.sub(self._DEFAULT_PATTERNS["extra_spaces"], " ", text)
            return text

        elif rule == "trim":
            # Remove leading and trailing whitespace
            return text.strip()

        else:
            logger.warning(f"Unknown cleaning rule: {rule}")
            return text

    @classmethod
    def get_available_rules(cls) -> List[str]:
        """
        Get list of available cleaning rules.

        Returns:
            List of rule names.

        Example:
            >>> rules = TextCleaner.get_available_rules()
            >>> print(rules)
            ['remove_urls', 'remove_emails', ...]
        """
        return cls._AVAILABLE_RULES.copy()


def clean_text(
    text: str,
    cleaning_rules: Optional[List[str]] = None,
    custom_patterns: Optional[Dict[str, str]] = None,
) -> str:
    """
    Convenience function for quick text cleaning.

    Args:
        text: Input text to clean.
        cleaning_rules: List of cleaning rule names.
        custom_patterns: Dictionary of custom patterns.

    Returns:
        Cleaned text.

    Example:
        >>> text = "Visit https://example.com for more   info"
        >>> cleaned = clean_text(text, cleaning_rules=["remove_urls", "normalize_spaces"])
        >>> print(cleaned)
        'Visit for more info'
    """
    cleaner = TextCleaner(cleaning_rules=cleaning_rules, custom_patterns=custom_patterns)
    return cleaner.clean(text)


__all__ = ["TextCleaner", "clean_text"]
