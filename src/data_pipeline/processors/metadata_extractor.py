"""
Metadata Extraction Module.

This module provides flexible metadata extraction from documents.
Designed to be domain-agnostic with configurable field extractors.

Design Principles:
- Configurable metadata fields
- Injectable custom extractors
- Domain-agnostic design
- Structured logging
- Type-safe operations

References:
- LLM Engineer's Handbook: Chapter 3 (Data Preprocessing)
- Clean Architecture: Dependency Injection
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class MetadataExtractor:
    """
    Domain-agnostic metadata extractor with configurable fields.

    This class extracts metadata from documents based on configurable field
    definitions. It supports custom extractors for domain-specific metadata.

    Attributes:
        metadata_fields: List of metadata field names to extract.
        custom_extractors: Dictionary of custom extraction functions.
        include_stats: Whether to include text statistics (length, word count).

    Example:
        >>> extractor = MetadataExtractor(
        ...     metadata_fields=["filename", "category", "region"],
        ...     include_stats=True
        ... )
        >>> metadata = extractor.extract(
        ...     text="Sample text content",
        ...     source_path="./data/cusco-tourism.pdf"
        ... )
        >>> print(metadata)
        {'filename': 'cusco-tourism.pdf', 'category': 'tourism', ...}

        >>> # Custom extractors for legal domain
        >>> def extract_case_number(text: str, **kwargs) -> Optional[str]:
        ...     import re
        ...     match = re.search(r"Case #(\\d+-\\d+)", text)
        ...     return match.group(1) if match else None
        >>>
        >>> legal_extractor = MetadataExtractor(
        ...     metadata_fields=["filename", "case_number"],
        ...     custom_extractors={"case_number": extract_case_number}
        ... )
    """

    # Default metadata fields (minimal, domain-agnostic)
    _DEFAULT_FIELDS = ["filename", "source_path", "created_at"]

    def __init__(
        self,
        metadata_fields: Optional[List[str]] = None,
        custom_extractors: Optional[Dict[str, Callable]] = None,
        include_stats: bool = True,
    ):
        """
        Initialize MetadataExtractor.

        Args:
            metadata_fields: List of metadata field names to extract.
                           If None, extracts only default fields.
            custom_extractors: Dictionary of custom extraction functions.
                             Format: {"field_name": extractor_function}
                             Each function should accept (text: str, **kwargs)
            include_stats: Whether to include text statistics in metadata.

        Example:
            >>> extractor = MetadataExtractor(
            ...     metadata_fields=["filename", "category"],
            ...     custom_extractors={"category": my_category_extractor},
            ...     include_stats=True
            ... )
        """
        self.metadata_fields = metadata_fields or self._DEFAULT_FIELDS.copy()
        self.custom_extractors = custom_extractors or {}
        self.include_stats = include_stats

        logger.info(
            "MetadataExtractor initialized",
            extra={
                "metadata_fields": self.metadata_fields,
                "custom_extractors": list(self.custom_extractors.keys()),
                "include_stats": self.include_stats,
            },
        )

    def extract(
        self,
        text: str,
        source_path: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Extract metadata from text and source information.

        Args:
            text: Document text content.
            source_path: Path to source document (if available).
            additional_metadata: Additional metadata to merge.

        Returns:
            Dictionary containing extracted metadata.

        Example:
            >>> extractor = MetadataExtractor(metadata_fields=["filename", "category"])
            >>> metadata = extractor.extract(
            ...     text="Tourism guide for Cusco",
            ...     source_path="./data/cusco.pdf",
            ...     additional_metadata={"language": "es"}
            ... )
            >>> print(metadata)
            {'filename': 'cusco.pdf', 'category': 'tourism', 'language': 'es', ...}
        """
        metadata: Dict[str, Any] = {}

        # Extract each configured field
        for field in self.metadata_fields:
            try:
                value = self._extract_field(
                    field=field,
                    text=text,
                    source_path=source_path,
                    additional_metadata=additional_metadata,
                )
                if value is not None:
                    metadata[field] = value
            except Exception as e:
                logger.warning(
                    f"Failed to extract field: {field}",
                    extra={"field": field, "error": str(e)},
                )

        # Add text statistics if enabled
        if self.include_stats:
            metadata.update(self._extract_stats(text))

        # Merge additional metadata
        if additional_metadata:
            metadata.update(additional_metadata)

        logger.debug(
            "Metadata extraction completed",
            extra={"extracted_fields": list(metadata.keys())},
        )

        return metadata

    def extract_batch(
        self,
        texts: List[str],
        source_paths: Optional[List[str]] = None,
        additional_metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract metadata from multiple texts in batch.

        Args:
            texts: List of document texts.
            source_paths: List of source paths (optional).
            additional_metadata: List of additional metadata dicts (optional).

        Returns:
            List of metadata dictionaries.

        Example:
            >>> extractor = MetadataExtractor()
            >>> texts = ["Text 1", "Text 2"]
            >>> paths = ["doc1.pdf", "doc2.pdf"]
            >>> metadata_list = extractor.extract_batch(texts, paths)
        """
        if not texts:
            return []

        # Ensure lists have same length
        source_paths = source_paths or [None] * len(texts)
        additional_metadata = additional_metadata or [None] * len(texts)

        if len(texts) != len(source_paths) or len(texts) != len(additional_metadata):
            raise ValueError("All input lists must have the same length")

        results = []
        for text, path, extra in zip(texts, source_paths, additional_metadata):
            metadata = self.extract(
                text=text, source_path=path, additional_metadata=extra
            )
            results.append(metadata)

        logger.info(
            "Batch metadata extraction completed",
            extra={"total_documents": len(texts)},
        )

        return results

    def _extract_field(
        self,
        field: str,
        text: str,
        source_path: Optional[str],
        additional_metadata: Optional[Dict[str, Any]],
    ) -> Optional[Any]:
        """
        Extract a specific metadata field.

        Args:
            field: Field name to extract.
            text: Document text.
            source_path: Source path.
            additional_metadata: Additional metadata.

        Returns:
            Extracted field value or None.
        """
        # Check if custom extractor exists
        if field in self.custom_extractors:
            return self.custom_extractors[field](
                text=text,
                source_path=source_path,
                additional_metadata=additional_metadata,
            )

        # Built-in extractors
        if field == "filename":
            return self._extract_filename(source_path)

        elif field == "source_path":
            return source_path

        elif field == "created_at":
            return datetime.utcnow().isoformat()

        elif field == "category":
            return self._infer_category(text, source_path)

        elif field == "region":
            return self._infer_region(text, source_path)

        elif field == "language":
            return self._infer_language(text)

        else:
            logger.debug(f"No extractor found for field: {field}")
            return None

    def _extract_filename(self, source_path: Optional[str]) -> Optional[str]:
        """Extract filename from source path."""
        if not source_path:
            return None
        return Path(source_path).name

    def _extract_stats(self, text: str) -> Dict[str, Any]:
        """
        Extract text statistics.

        Args:
            text: Document text.

        Returns:
            Dictionary with statistics (char_count, word_count, line_count).
        """
        if not text:
            return {
                "char_count": 0,
                "word_count": 0,
                "line_count": 0,
            }

        stats = {
            "char_count": len(text),
            "word_count": len(text.split()),
            "line_count": text.count("\n") + 1,
        }

        return stats

    def _infer_category(
        self, text: str, source_path: Optional[str]
    ) -> Optional[str]:
        """
        Infer document category from text and filename.

        This is a basic implementation. For production, consider:
        - Using a classification model
        - Keyword-based classification
        - Domain-specific heuristics

        Args:
            text: Document text.
            source_path: Source path.

        Returns:
            Inferred category or None.
        """
        if not text and not source_path:
            return None

        # Combine text and filename for analysis
        content = (text[:500] if text else "") + " " + (source_path or "")
        content_lower = content.lower()

        # Tourism keywords (example)
        tourism_keywords = [
            "turismo",
            "tourism",
            "hotel",
            "restaurant",
            "viaje",
            "travel",
            "destino",
            "destination",
            "guía",
            "guide",
        ]

        # Legal keywords (example)
        legal_keywords = [
            "legal",
            "law",
            "court",
            "case",
            "sentencia",
            "tribunal",
            "derecho",
            "contract",
        ]

        # Academic keywords (example)
        academic_keywords = [
            "research",
            "investigación",
            "study",
            "estudio",
            "paper",
            "journal",
            "universidad",
            "university",
        ]

        # Check keywords
        if any(keyword in content_lower for keyword in tourism_keywords):
            return "tourism"
        elif any(keyword in content_lower for keyword in legal_keywords):
            return "legal"
        elif any(keyword in content_lower for keyword in academic_keywords):
            return "academic"

        return "general"

    def _infer_region(self, text: str, source_path: Optional[str]) -> Optional[str]:
        """
        Infer geographic region from text and filename.

        This is a basic implementation for Peru regions (example).
        Can be customized for any geography.

        Args:
            text: Document text.
            source_path: Source path.

        Returns:
            Inferred region or None.
        """
        if not text and not source_path:
            return None

        content = (text[:500] if text else "") + " " + (source_path or "")
        content_lower = content.lower()

        # Peru regions (example - easily customizable)
        regions = {
            "cusco": ["cusco", "machu picchu", "valle sagrado"],
            "lima": ["lima", "miraflores", "barranco"],
            "arequipa": ["arequipa", "colca", "misti"],
            "puno": ["puno", "titicaca", "uros"],
            "iquitos": ["iquitos", "amazonia", "amazon"],
        }

        for region, keywords in regions.items():
            if any(keyword in content_lower for keyword in keywords):
                return region

        return None

    def _infer_language(self, text: str) -> Optional[str]:
        """
        Infer text language using simple heuristics.

        For production, consider using langdetect or similar library.

        Args:
            text: Document text.

        Returns:
            Inferred language code (ISO 639-1) or None.
        """
        if not text or len(text) < 50:
            return None

        text_lower = text.lower()

        # Spanish indicators
        spanish_words = ["el", "la", "de", "en", "que", "es", "por", "los", "del", "se"]
        spanish_count = sum(
            1 for word in spanish_words if f" {word} " in f" {text_lower} "
        )

        # English indicators
        english_words = ["the", "of", "and", "to", "in", "is", "for", "on", "at", "by"]
        english_count = sum(
            1 for word in english_words if f" {word} " in f" {text_lower} "
        )

        if spanish_count > english_count:
            return "es"
        elif english_count > spanish_count:
            return "en"

        return None


def extract_metadata(
    text: str,
    source_path: Optional[str] = None,
    metadata_fields: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Convenience function for quick metadata extraction.

    Args:
        text: Document text.
        source_path: Path to source document.
        metadata_fields: List of fields to extract.

    Returns:
        Dictionary of extracted metadata.

    Example:
        >>> text = "Tourism guide for Cusco, Peru"
        >>> metadata = extract_metadata(
        ...     text=text,
        ...     source_path="./cusco.pdf",
        ...     metadata_fields=["filename", "category", "language"]
        ... )
        >>> print(metadata)
        {'filename': 'cusco.pdf', 'category': 'tourism', 'language': 'es', ...}
    """
    extractor = MetadataExtractor(metadata_fields=metadata_fields)
    return extractor.extract(text=text, source_path=source_path)


__all__ = ["MetadataExtractor", "extract_metadata"]
