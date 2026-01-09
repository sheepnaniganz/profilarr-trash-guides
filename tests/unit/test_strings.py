"""
Unit tests for scripts/utils/strings.py
"""

import sys
from pathlib import Path

import pytest


# Add scripts directory to path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from utils.strings import get_name, get_regex_pattern_name, get_safe_name


class TestGetSafeName:
    """Test cases for get_safe_name function."""

    def test_replace_forward_slash(self):
        """Test that forward slashes are replaced with hyphens."""
        assert get_safe_name("Test/Format") == "Test-Format"

    def test_replace_square_brackets(self):
        """Test that square brackets are replaced with parentheses."""
        assert get_safe_name("Test[Bracket]") == "Test(Bracket)"

    def test_replace_hdr10plus(self):
        """Test that HDR10Plus is replaced with HDR10+."""
        assert get_safe_name("HDR10Plus") == "HDR10+"

    def test_replace_10_bit(self):
        """Test that '10 bit' is replaced with '10bit'."""
        assert get_safe_name("10 bit") == "10bit"

    def test_replace_atmos(self):
        """Test that Atmos is replaced with ATMOS."""
        assert get_safe_name("Atmos") == "ATMOS"

    def test_combined_replacements(self):
        """Test multiple replacements in one string."""
        result = get_safe_name("Test[Format]/HDR10Plus/10 bit/Atmos")
        assert result == "Test(Format)-HDR10+-10bit-ATMOS"

    def test_no_replacement_needed(self):
        """Test that strings without special characters are unchanged."""
        assert get_safe_name("SimpleFormat") == "SimpleFormat"

    def test_empty_string(self):
        """Test that empty string returns empty string."""
        assert get_safe_name("") == ""

    @pytest.mark.parametrize("input_str,expected", [
        ("Test/Path[Bracket]", "Test-Path(Bracket)"),
        ("HDR10Plus/10 bit", "HDR10+-10bit"),
        ("Multiple[Brackets][Here]", "Multiple(Brackets)(Here)"),
    ])
    def test_parameterized_replacements(self, input_str, expected):
        """Test various replacement combinations."""
        assert get_safe_name(input_str) == expected


class TestGetName:
    """Test cases for get_name function."""

    def test_radarr_prefix(self):
        """Test that Radarr service gets correct prefix."""
        assert get_name("radarr", "Test Format") == "Radarr - Test Format"

    def test_sonarr_prefix(self):
        """Test that Sonarr service gets correct prefix."""
        assert get_name("sonarr", "Test Format") == "Sonarr - Test Format"

    def test_capitalization(self):
        """Test that service name is capitalized."""
        assert get_name("RADARR", "Test") == "Radarr - Test"
        assert get_name("SoNaRr", "Test") == "Sonarr - Test"

    def test_applies_safe_name(self):
        """Test that get_name applies get_safe_name transformation."""
        result = get_name("radarr", "Test[Bracket]/Format")
        assert result == "Radarr - Test(Bracket)-Format"

    @pytest.mark.parametrize("service,name,expected", [
        ("radarr", "Test Format", "Radarr - Test Format"),
        ("sonarr", "Test Format", "Sonarr - Test Format"),
        ("radarr", "Test/Path", "Radarr - Test-Path"),
        ("sonarr", "HDR10Plus", "Sonarr - HDR10+"),
    ])
    def test_parameterized_names(self, service, name, expected):
        """Test various service and name combinations."""
        assert get_name(service, name) == expected


class TestGetRegexPatternName:
    """Test cases for get_regex_pattern_name function."""

    def test_basic_regex_pattern_name(self):
        """Test basic regex pattern naming."""
        result = get_regex_pattern_name("radarr", "Test Pattern")
        assert result == "Radarr - Test Pattern"

    def test_removes_not_prefix(self):
        """Test that 'Not ' prefix is removed from pattern names."""
        result = get_regex_pattern_name("radarr", "Not Test Pattern")
        assert result == "Radarr - Test Pattern"

    def test_removes_not_prefix_only(self):
        """Test that only leading 'Not ' is removed."""
        result = get_regex_pattern_name("radarr", "Not In The Middle")
        assert result == "Radarr - In The Middle"

    def test_handles_not_in_middle(self):
        """Test that 'Not ' anywhere in the string is removed."""
        # The function replaces ALL occurrences of "Not "
        result = get_regex_pattern_name("radarr", "Test Not Pattern")
        assert result == "Radarr - Test Pattern"

    def test_case_sensitive_not(self):
        """Test that 'not' (lowercase) at the end is not removed."""
        result = get_regex_pattern_name("radarr", "Pattern not Test")
        assert result == "Radarr - Pattern not Test"

    @pytest.mark.parametrize("service,name,expected", [
        ("radarr", "Pattern", "Radarr - Pattern"),
        ("sonarr", "Not Pattern", "Sonarr - Pattern"),
        ("radarr", "Not HDR10Plus", "Radarr - HDR10+"),
        ("sonarr", "Not Test[Format]", "Sonarr - Test(Format)"),
    ])
    def test_parameterized_regex_patterns(self, service, name, expected):
        """Test various regex pattern combinations."""
        assert get_regex_pattern_name(service, name) == expected
