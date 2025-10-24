"""
Tests for TextCleaner module.

This test suite validates text cleaning functionality with various scenarios
including domain-agnostic use cases.
"""

import pytest

from src.data_pipeline.processors.cleaner import TextCleaner, clean_text


class TestTextCleanerInitialization:
    """Test TextCleaner initialization."""

    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        cleaner = TextCleaner()
        
        assert cleaner.cleaning_rules is not None
        assert len(cleaner.cleaning_rules) > 0
        assert cleaner.preserve_newlines is True
        assert cleaner.min_length == 0
        assert cleaner.custom_patterns == {}

    def test_init_with_custom_rules(self):
        """Test initialization with custom cleaning rules."""
        rules = ["remove_urls", "normalize_spaces"]
        cleaner = TextCleaner(cleaning_rules=rules)
        
        assert cleaner.cleaning_rules == rules

    def test_init_with_invalid_rule(self):
        """Test initialization with invalid cleaning rule raises error."""
        with pytest.raises(ValueError, match="Invalid cleaning rules"):
            TextCleaner(cleaning_rules=["invalid_rule"])

    def test_init_with_custom_patterns(self):
        """Test initialization with custom regex patterns."""
        patterns = {"custom": r"\[REDACTED\]"}
        cleaner = TextCleaner(custom_patterns=patterns)
        
        assert cleaner.custom_patterns == patterns

    def test_init_with_min_length(self):
        """Test initialization with minimum length requirement."""
        cleaner = TextCleaner(min_length=10)
        
        assert cleaner.min_length == 10


class TestTextCleanerBasicCleaning:
    """Test basic text cleaning operations."""

    def test_clean_empty_text(self):
        """Test cleaning empty text returns empty string."""
        cleaner = TextCleaner()
        
        assert cleaner.clean("") == ""
        assert cleaner.clean("   ") == ""

    def test_clean_none_text(self):
        """Test cleaning None returns empty string."""
        cleaner = TextCleaner()
        
        assert cleaner.clean(None) == ""

    def test_clean_removes_urls(self):
        """Test cleaning removes URLs."""
        cleaner = TextCleaner(cleaning_rules=["remove_urls", "trim"])
        text = "Check this link: https://example.com for more info"
        
        result = cleaner.clean(text)
        
        assert "https://example.com" not in result
        assert "Check this link:" in result
        assert "for more info" in result

    def test_clean_removes_emails(self):
        """Test cleaning removes email addresses."""
        cleaner = TextCleaner(cleaning_rules=["remove_emails", "trim"])
        text = "Contact me at user@example.com for details"
        
        result = cleaner.clean(text)
        
        assert "user@example.com" not in result
        assert "Contact me at" in result

    def test_clean_removes_phone_numbers(self):
        """Test cleaning removes phone numbers."""
        cleaner = TextCleaner(cleaning_rules=["remove_phone_numbers", "trim"])
        text = "Call me at +1-555-123-4567 anytime"
        
        result = cleaner.clean(text)
        
        assert "+1-555-123-4567" not in result
        assert "Call me at" in result

    def test_clean_removes_html_tags(self):
        """Test cleaning removes HTML tags."""
        cleaner = TextCleaner(cleaning_rules=["remove_html_tags", "trim"])
        text = "<p>This is <b>bold</b> text</p>"
        
        result = cleaner.clean(text)
        
        assert "<p>" not in result
        assert "<b>" not in result
        assert "This is" in result
        assert "bold" in result


class TestTextCleanerSpaceNormalization:
    """Test space and newline normalization."""

    def test_normalize_spaces(self):
        """Test normalization of multiple spaces."""
        cleaner = TextCleaner(cleaning_rules=["normalize_spaces", "trim"])
        text = "Hello    world   with   spaces"
        
        result = cleaner.clean(text)
        
        assert "    " not in result
        assert "Hello world with spaces" == result

    def test_normalize_newlines_preserve(self):
        """Test newline normalization with preservation."""
        cleaner = TextCleaner(
            cleaning_rules=["normalize_newlines"],
            preserve_newlines=True
        )
        text = "Line 1\n\n\n\nLine 2"
        
        result = cleaner.clean(text)
        
        assert "\n\n\n\n" not in result
        assert "\n\n" in result
        assert "Line 1" in result
        assert "Line 2" in result

    def test_normalize_newlines_remove(self):
        """Test newline normalization without preservation."""
        cleaner = TextCleaner(
            cleaning_rules=["normalize_newlines", "normalize_spaces"],
            preserve_newlines=False
        )
        text = "Line 1\nLine 2\nLine 3"
        
        result = cleaner.clean(text)
        
        assert "\n" not in result
        assert "Line 1 Line 2 Line 3" == result

    def test_trim_whitespace(self):
        """Test trimming leading and trailing whitespace."""
        cleaner = TextCleaner(cleaning_rules=["trim"])
        text = "   Hello world   "
        
        result = cleaner.clean(text)
        
        assert result == "Hello world"


class TestTextCleanerCustomPatterns:
    """Test custom pattern cleaning."""

    def test_clean_with_custom_pattern(self):
        """Test cleaning with custom regex pattern."""
        cleaner = TextCleaner(
            cleaning_rules=["trim"],
            custom_patterns={"redacted": r"\[REDACTED\]"}
        )
        text = "This is [REDACTED] information"
        
        result = cleaner.clean(text)
        
        assert "[REDACTED]" not in result
        assert "This is" in result
        assert "information" in result

    def test_clean_with_multiple_custom_patterns(self):
        """Test cleaning with multiple custom patterns."""
        cleaner = TextCleaner(
            cleaning_rules=["trim", "normalize_spaces"],
            custom_patterns={
                "case_num": r"Case #\d+-\d+",
                "ref_num": r"Ref:\s*\d+"
            }
        )
        text = "Case #2024-001 and Ref: 12345 are confidential"
        
        result = cleaner.clean(text)
        
        assert "Case #2024-001" not in result
        assert "Ref: 12345" not in result
        assert "are confidential" in result


class TestTextCleanerMinLength:
    """Test minimum length filtering."""

    def test_min_length_returns_empty_when_too_short(self):
        """Test that text below minimum length returns empty string."""
        cleaner = TextCleaner(min_length=20)
        text = "Short text"
        
        result = cleaner.clean(text)
        
        assert result == ""

    def test_min_length_returns_text_when_long_enough(self):
        """Test that text meeting minimum length is returned."""
        cleaner = TextCleaner(
            cleaning_rules=["trim"],
            min_length=10
        )
        text = "This is long enough text"
        
        result = cleaner.clean(text)
        
        assert len(result) >= 10
        assert result == text


class TestTextCleanerBatchProcessing:
    """Test batch text cleaning."""

    def test_clean_batch_empty_list(self):
        """Test cleaning empty batch returns empty list."""
        cleaner = TextCleaner()
        
        result = cleaner.clean_batch([])
        
        assert result == []

    def test_clean_batch_multiple_texts(self):
        """Test cleaning multiple texts in batch."""
        cleaner = TextCleaner(
            cleaning_rules=["remove_urls", "normalize_spaces", "trim"]
        )
        texts = [
            "Text 1 https://url1.com",
            "Text 2   with   spaces",
            "Text 3 https://url2.com more text"
        ]
        
        results = cleaner.clean_batch(texts)
        
        assert len(results) == 3
        assert "https://url1.com" not in results[0]
        assert "Text 1" in results[0]
        assert "   " not in results[1]
        assert "Text 2 with spaces" == results[1]
        assert "https://url2.com" not in results[2]

    def test_clean_batch_with_empty_results(self):
        """Test batch cleaning with some texts becoming empty."""
        cleaner = TextCleaner(
            cleaning_rules=["remove_urls", "trim"],
            min_length=10
        )
        texts = [
            "https://only-url.com",  # Will be empty after cleaning
            "Valid text content here",
            "https://another-url.com"  # Will be empty
        ]
        
        results = cleaner.clean_batch(texts)
        
        assert len(results) == 3
        assert results[0] == ""  # Too short after cleaning
        assert results[1] != ""  # Long enough
        assert results[2] == ""  # Too short after cleaning


class TestTextCleanerComplexScenarios:
    """Test complex real-world scenarios."""

    def test_clean_tourism_text(self):
        """Test cleaning tourism-related text (domain example)."""
        cleaner = TextCleaner(
            cleaning_rules=[
                "remove_urls",
                "remove_emails",
                "normalize_spaces",
                "normalize_newlines",
                "trim"
            ]
        )
        text = """
        Visit Machu Picchu!
        
        For bookings: contact@tourism.com
        
        Website: https://tourism.com
        
        Call:  +51-123-456
        """
        
        result = cleaner.clean(text)
        
        assert "Machu Picchu" in result
        assert "contact@tourism.com" not in result
        assert "https://tourism.com" not in result
        # Text is preserved but cleaned

    def test_clean_legal_text(self):
        """Test cleaning legal document text (domain example)."""
        cleaner = TextCleaner(
            cleaning_rules=["remove_html_tags", "normalize_spaces", "trim"],
            custom_patterns={"confidential": r"\[CONFIDENTIAL\]"}
        )
        text = "<p>Case <b>Summary</b>: [CONFIDENTIAL]  information   here</p>"
        
        result = cleaner.clean(text)
        
        assert "<p>" not in result
        assert "<b>" not in result
        assert "[CONFIDENTIAL]" not in result
        assert "Case Summary:" in result

    def test_clean_academic_text(self):
        """Test cleaning academic paper text (domain example)."""
        cleaner = TextCleaner(
            cleaning_rules=[
                "remove_urls",
                "remove_html_tags",
                "normalize_spaces",
            ],
            preserve_newlines=True
        )
        text = """
        Abstract
        
        This  study   examines...
        
        
        References: https://doi.org/10.1234/example
        """
        
        result = cleaner.clean(text)
        
        assert "Abstract" in result
        assert "This study examines" in result  # Normalized spaces
        assert "https://doi.org/" not in result
        # Text is cleaned but content preserved
        assert len(result) > 0


class TestTextCleanerConvenienceFunction:
    """Test convenience function for quick cleaning."""

    def test_clean_text_function(self):
        """Test quick text cleaning with convenience function."""
        text = "Visit https://example.com   for   info"
        
        result = clean_text(
            text,
            cleaning_rules=["remove_urls", "normalize_spaces", "trim"]
        )
        
        assert "https://example.com" not in result
        assert "Visit for info" == result

    def test_clean_text_with_custom_patterns(self):
        """Test convenience function with custom patterns."""
        text = "Text with [REDACTED] content"
        
        result = clean_text(
            text,
            cleaning_rules=["trim"],
            custom_patterns={"redacted": r"\[REDACTED\]"}
        )
        
        assert "[REDACTED]" not in result


class TestTextCleanerClassMethods:
    """Test class methods."""

    def test_get_available_rules(self):
        """Test getting list of available cleaning rules."""
        rules = TextCleaner.get_available_rules()
        
        assert isinstance(rules, list)
        assert len(rules) > 0
        assert "remove_urls" in rules
        assert "normalize_spaces" in rules
        assert "trim" in rules


# Parametrized tests for comprehensive coverage
@pytest.mark.parametrize("text,expected_contains", [
    ("https://example.com", ""),
    ("user@example.com", ""),
    ("+1-555-1234", ""),
    ("<html>text</html>", "text"),
    ("multiple   spaces", "multiple spaces"),
])
def test_cleaning_various_patterns(text, expected_contains):
    """Test cleaning various patterns."""
    cleaner = TextCleaner()
    result = cleaner.clean(text)
    
    if expected_contains:
        assert expected_contains in result or expected_contains == result
