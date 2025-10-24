"""
Tests for MetadataExtractor module.

This test suite validates metadata extraction functionality with various
domain-agnostic scenarios.
"""

import pytest

from src.data_pipeline.processors.metadata_extractor import (
    MetadataExtractor,
    extract_metadata,
)


class TestMetadataExtractorInitialization:
    """Test MetadataExtractor initialization."""

    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        extractor = MetadataExtractor()
        
        assert extractor.metadata_fields is not None
        assert len(extractor.metadata_fields) > 0
        assert extractor.include_stats is True
        assert extractor.custom_extractors == {}

    def test_init_with_custom_fields(self):
        """Test initialization with custom metadata fields."""
        fields = ["filename", "category", "region"]
        extractor = MetadataExtractor(metadata_fields=fields)
        
        assert extractor.metadata_fields == fields

    def test_init_with_custom_extractors(self):
        """Test initialization with custom extractor functions."""
        def custom_extractor(text, **kwargs):
            return "custom_value"
        
        extractors = {"custom_field": custom_extractor}
        extractor = MetadataExtractor(custom_extractors=extractors)
        
        assert "custom_field" in extractor.custom_extractors

    def test_init_without_stats(self):
        """Test initialization without text statistics."""
        extractor = MetadataExtractor(include_stats=False)
        
        assert extractor.include_stats is False


class TestMetadataExtractorBasicExtraction:
    """Test basic metadata extraction."""

    def test_extract_from_empty_text(self):
        """Test extraction from empty text."""
        extractor = MetadataExtractor(metadata_fields=["filename"])
        
        metadata = extractor.extract(text="", source_path="test.pdf")
        
        assert "filename" in metadata
        assert metadata["filename"] == "test.pdf"

    def test_extract_filename(self):
        """Test filename extraction from source path."""
        extractor = MetadataExtractor(metadata_fields=["filename"])
        
        metadata = extractor.extract(
            text="Sample text",
            source_path="./data/documents/sample.pdf"
        )
        
        assert metadata["filename"] == "sample.pdf"

    def test_extract_source_path(self):
        """Test source path extraction."""
        extractor = MetadataExtractor(metadata_fields=["source_path"])
        path = "./data/sample.pdf"
        
        metadata = extractor.extract(text="Text", source_path=path)
        
        assert metadata["source_path"] == path

    def test_extract_created_at(self):
        """Test created_at timestamp extraction."""
        extractor = MetadataExtractor(metadata_fields=["created_at"])
        
        metadata = extractor.extract(text="Text")
        
        assert "created_at" in metadata
        assert isinstance(metadata["created_at"], str)
        # Should be ISO format timestamp

    def test_extract_multiple_fields(self):
        """Test extraction of multiple fields."""
        extractor = MetadataExtractor(
            metadata_fields=["filename", "source_path", "created_at"]
        )
        
        metadata = extractor.extract(
            text="Sample text",
            source_path="./data/test.pdf"
        )
        
        assert "filename" in metadata
        assert "source_path" in metadata
        assert "created_at" in metadata


class TestMetadataExtractorStatistics:
    """Test text statistics extraction."""

    def test_extract_stats_included(self):
        """Test that statistics are included when enabled."""
        extractor = MetadataExtractor(
            metadata_fields=["filename"],
            include_stats=True
        )
        text = "Sample text with multiple words"
        
        metadata = extractor.extract(text=text, source_path="test.pdf")
        
        assert "char_count" in metadata
        assert "word_count" in metadata
        assert "line_count" in metadata

    def test_extract_stats_excluded(self):
        """Test that statistics are excluded when disabled."""
        extractor = MetadataExtractor(
            metadata_fields=["filename"],
            include_stats=False
        )
        
        metadata = extractor.extract(text="Text", source_path="test.pdf")
        
        assert "char_count" not in metadata
        assert "word_count" not in metadata
        assert "line_count" not in metadata

    def test_stats_char_count(self):
        """Test character count calculation."""
        extractor = MetadataExtractor(include_stats=True)
        text = "Hello"
        
        metadata = extractor.extract(text=text)
        
        assert metadata["char_count"] == 5

    def test_stats_word_count(self):
        """Test word count calculation."""
        extractor = MetadataExtractor(include_stats=True)
        text = "One two three four"
        
        metadata = extractor.extract(text=text)
        
        assert metadata["word_count"] == 4

    def test_stats_line_count(self):
        """Test line count calculation."""
        extractor = MetadataExtractor(include_stats=True)
        text = "Line 1\nLine 2\nLine 3"
        
        metadata = extractor.extract(text=text)
        
        assert metadata["line_count"] == 3

    def test_stats_empty_text(self):
        """Test statistics for empty text."""
        extractor = MetadataExtractor(include_stats=True)
        
        metadata = extractor.extract(text="")
        
        assert metadata["char_count"] == 0
        assert metadata["word_count"] == 0
        assert metadata["line_count"] == 0


class TestMetadataExtractorCategoryInference:
    """Test category inference."""

    def test_infer_tourism_category(self):
        """Test inference of tourism category."""
        extractor = MetadataExtractor(metadata_fields=["category"])
        text = "Tourism guide to Machu Picchu with hotel recommendations"
        
        metadata = extractor.extract(text=text)
        
        assert metadata["category"] == "tourism"

    def test_infer_legal_category(self):
        """Test inference of legal category."""
        extractor = MetadataExtractor(metadata_fields=["category"])
        text = "Legal case regarding contract law and tribunal decision"
        
        metadata = extractor.extract(text=text)
        
        assert metadata["category"] == "legal"

    def test_infer_academic_category(self):
        """Test inference of academic category."""
        extractor = MetadataExtractor(metadata_fields=["category"])
        text = "Research paper on university studies and journal publications"
        
        metadata = extractor.extract(text=text)
        
        assert metadata["category"] == "academic"

    def test_infer_general_category(self):
        """Test inference of general category when no match."""
        extractor = MetadataExtractor(metadata_fields=["category"])
        text = "Generic text without specific domain indicators"
        
        metadata = extractor.extract(text=text)
        
        assert metadata["category"] == "general"

    def test_infer_category_from_filename(self):
        """Test category inference from filename."""
        extractor = MetadataExtractor(metadata_fields=["category"])
        
        metadata = extractor.extract(
            text="",
            source_path="./data/tourism/guide.pdf"
        )
        
        assert metadata["category"] == "tourism"


class TestMetadataExtractorRegionInference:
    """Test region inference (Peru example)."""

    def test_infer_cusco_region(self):
        """Test inference of Cusco region."""
        extractor = MetadataExtractor(metadata_fields=["region"])
        text = "Travel guide to Cusco and Machu Picchu"
        
        metadata = extractor.extract(text=text)
        
        assert metadata["region"] == "cusco"

    def test_infer_lima_region(self):
        """Test inference of Lima region."""
        extractor = MetadataExtractor(metadata_fields=["region"])
        text = "Restaurants in Miraflores, Lima"
        
        metadata = extractor.extract(text=text)
        
        assert metadata["region"] == "lima"

    def test_infer_arequipa_region(self):
        """Test inference of Arequipa region."""
        extractor = MetadataExtractor(metadata_fields=["region"])
        text = "Visit Arequipa and the Colca Canyon"
        
        metadata = extractor.extract(text=text)
        
        assert metadata["region"] == "arequipa"

    def test_infer_region_from_filename(self):
        """Test region inference from filename."""
        extractor = MetadataExtractor(metadata_fields=["region"])
        
        metadata = extractor.extract(
            text="",
            source_path="./data/cusco-guide.pdf"
        )
        
        assert metadata["region"] == "cusco"

    def test_infer_no_region(self):
        """Test when no region can be inferred."""
        extractor = MetadataExtractor(metadata_fields=["region"])
        text = "Generic content without location"
        
        metadata = extractor.extract(text=text)
        
        assert metadata.get("region") is None


class TestMetadataExtractorLanguageInference:
    """Test language inference."""

    def test_infer_spanish_language(self):
        """Test inference of Spanish language."""
        extractor = MetadataExtractor(metadata_fields=["language"])
        text = "Este es un texto en español con varias palabras comunes"
        
        metadata = extractor.extract(text=text)
        
        assert metadata["language"] == "es"

    def test_infer_english_language(self):
        """Test inference of English language."""
        extractor = MetadataExtractor(metadata_fields=["language"])
        text = "This is a text in English with several common words"
        
        metadata = extractor.extract(text=text)
        
        assert metadata["language"] == "en"

    def test_infer_language_short_text(self):
        """Test language inference with short text returns None."""
        extractor = MetadataExtractor(metadata_fields=["language"])
        text = "Short"
        
        metadata = extractor.extract(text=text)
        
        assert metadata.get("language") is None


class TestMetadataExtractorCustomExtractors:
    """Test custom extractor functions."""

    def test_custom_extractor_called(self):
        """Test that custom extractor is called."""
        def custom_extractor(text, **kwargs):
            return "custom_value"
        
        extractor = MetadataExtractor(
            metadata_fields=["custom_field"],
            custom_extractors={"custom_field": custom_extractor}
        )
        
        metadata = extractor.extract(text="Text")
        
        assert metadata["custom_field"] == "custom_value"

    def test_custom_extractor_receives_params(self):
        """Test that custom extractor receives correct parameters."""
        received_params = {}
        
        def custom_extractor(text, source_path=None, **kwargs):
            received_params["text"] = text
            received_params["source_path"] = source_path
            return "value"
        
        extractor = MetadataExtractor(
            metadata_fields=["custom_field"],
            custom_extractors={"custom_field": custom_extractor}
        )
        
        extractor.extract(text="Sample", source_path="./test.pdf")
        
        assert received_params["text"] == "Sample"
        assert received_params["source_path"] == "./test.pdf"

    def test_multiple_custom_extractors(self):
        """Test multiple custom extractors."""
        def extractor1(text, **kwargs):
            return "value1"
        
        def extractor2(text, **kwargs):
            return "value2"
        
        extractor = MetadataExtractor(
            metadata_fields=["field1", "field2"],
            custom_extractors={
                "field1": extractor1,
                "field2": extractor2
            }
        )
        
        metadata = extractor.extract(text="Text")
        
        assert metadata["field1"] == "value1"
        assert metadata["field2"] == "value2"

    def test_custom_extractor_domain_specific(self):
        """Test custom extractor for domain-specific field."""
        def extract_case_number(text, **kwargs):
            import re
            match = re.search(r"Case #(\d+-\d+)", text)
            return match.group(1) if match else None
        
        extractor = MetadataExtractor(
            metadata_fields=["case_number"],
            custom_extractors={"case_number": extract_case_number}
        )
        
        text = "This is Case #2024-001 about..."
        metadata = extractor.extract(text=text)
        
        assert metadata["case_number"] == "2024-001"


class TestMetadataExtractorAdditionalMetadata:
    """Test merging of additional metadata."""

    def test_merge_additional_metadata(self):
        """Test that additional metadata is merged."""
        extractor = MetadataExtractor(metadata_fields=["filename"])
        additional = {"author": "John Doe", "version": "1.0"}
        
        metadata = extractor.extract(
            text="Text",
            source_path="test.pdf",
            additional_metadata=additional
        )
        
        assert "filename" in metadata
        assert metadata["author"] == "John Doe"
        assert metadata["version"] == "1.0"

    def test_additional_metadata_overrides(self):
        """Test that additional metadata can override extracted fields."""
        extractor = MetadataExtractor(metadata_fields=["category"])
        additional = {"category": "custom_category"}
        
        metadata = extractor.extract(
            text="Tourism text",
            additional_metadata=additional
        )
        
        # Additional metadata should override
        assert metadata["category"] == "custom_category"


class TestMetadataExtractorBatchProcessing:
    """Test batch metadata extraction."""

    def test_extract_batch_empty_list(self):
        """Test batch extraction with empty list."""
        extractor = MetadataExtractor()
        
        results = extractor.extract_batch([])
        
        assert results == []

    def test_extract_batch_multiple_texts(self):
        """Test batch extraction with multiple texts."""
        extractor = MetadataExtractor(metadata_fields=["filename", "category"])
        texts = [
            "Tourism guide to Cusco",
            "Legal case study",
            "Research paper abstract"
        ]
        paths = ["tourism.pdf", "legal.pdf", "research.pdf"]
        
        results = extractor.extract_batch(texts, source_paths=paths)
        
        assert len(results) == 3
        assert results[0]["filename"] == "tourism.pdf"
        assert results[0]["category"] == "tourism"
        assert results[1]["category"] == "legal"
        assert results[2]["category"] == "academic"

    def test_extract_batch_with_additional_metadata(self):
        """Test batch extraction with additional metadata."""
        extractor = MetadataExtractor(metadata_fields=["filename"])
        texts = ["Text 1", "Text 2"]
        paths = ["file1.pdf", "file2.pdf"]
        additional = [
            {"author": "Author 1"},
            {"author": "Author 2"}
        ]
        
        results = extractor.extract_batch(
            texts, source_paths=paths, additional_metadata=additional
        )
        
        assert results[0]["author"] == "Author 1"
        assert results[1]["author"] == "Author 2"

    def test_extract_batch_mismatched_lengths_raises_error(self):
        """Test that mismatched input lengths raise error."""
        extractor = MetadataExtractor()
        texts = ["Text 1", "Text 2"]
        paths = ["file1.pdf"]  # Mismatched length
        
        with pytest.raises(ValueError, match="same length"):
            extractor.extract_batch(texts, source_paths=paths)


class TestMetadataExtractorComplexScenarios:
    """Test complex real-world scenarios."""

    def test_extract_tourism_metadata(self):
        """Test extraction from tourism document."""
        extractor = MetadataExtractor(
            metadata_fields=["filename", "category", "region", "language"],
            include_stats=True
        )
        text = "Guía de turismo para Cusco y Machu Picchu con hoteles"
        
        metadata = extractor.extract(
            text=text,
            source_path="./data/cusco-guide.pdf"
        )
        
        assert metadata["filename"] == "cusco-guide.pdf"
        assert metadata["category"] == "tourism"
        assert metadata["region"] == "cusco"
        assert metadata["language"] == "es"
        assert "word_count" in metadata

    def test_extract_legal_metadata(self):
        """Test extraction from legal document."""
        def extract_case_number(text, **kwargs):
            import re
            match = re.search(r"Case #(\d+-\d+)", text)
            return match.group(1) if match else None
        
        extractor = MetadataExtractor(
            metadata_fields=["filename", "category", "case_number"],
            custom_extractors={"case_number": extract_case_number}
        )
        text = "Legal case Case #2024-001 regarding contract law"
        
        metadata = extractor.extract(
            text=text,
            source_path="./legal/case-2024-001.pdf"
        )
        
        assert metadata["category"] == "legal"
        assert metadata["case_number"] == "2024-001"

    def test_extract_academic_metadata(self):
        """Test extraction from academic document."""
        extractor = MetadataExtractor(
            metadata_fields=["filename", "category", "language"],
            include_stats=True
        )
        text = "Research study on university education published in academic journal"
        
        metadata = extractor.extract(
            text=text,
            source_path="./papers/study-2024.pdf",
            additional_metadata={"doi": "10.1234/example"}
        )
        
        assert metadata["category"] == "academic"
        assert metadata["language"] == "en"
        assert metadata["doi"] == "10.1234/example"
        assert metadata["char_count"] > 0


class TestMetadataExtractorConvenienceFunction:
    """Test convenience function."""

    def test_extract_metadata_function(self):
        """Test quick extraction with convenience function."""
        text = "Tourism guide for Cusco"
        
        metadata = extract_metadata(
            text=text,
            source_path="./cusco.pdf",
            metadata_fields=["filename", "category"]
        )
        
        assert metadata["filename"] == "cusco.pdf"
        assert metadata["category"] == "tourism"


# Parametrized tests for comprehensive coverage
@pytest.mark.parametrize("text,expected_category", [
    ("Tourism guide to Lima", "tourism"),
    ("Legal case study", "legal"),
    ("University research paper", "academic"),
    ("Generic content here", "general"),
])
def test_category_inference_various_texts(text, expected_category):
    """Test category inference with various texts."""
    extractor = MetadataExtractor(metadata_fields=["category"])
    metadata = extractor.extract(text=text)
    
    assert metadata["category"] == expected_category


@pytest.mark.parametrize("text,expected_language", [
    ("Este es un texto en español con más palabras para detectar el idioma correctamente", "es"),
    ("This is an English text with more words to properly detect the language", "en"),
])
def test_language_inference_various_texts(text, expected_language):
    """Test language inference with various texts."""
    extractor = MetadataExtractor(metadata_fields=["language"])
    metadata = extractor.extract(text=text)
    
    assert metadata.get("language") == expected_language
