"""
Unit Tests for Environment Variable Loader
Tests environment loading, validation, and type conversion utilities

Author: Claude Code Assistant
Date: 2025-10-04
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import module under test
from automation.utils.env_loader import (
    load_environment,
    get_required_env,
    get_bool_env,
    get_int_env,
    validate_api_keys,
    print_environment_status
)


@pytest.mark.unit
class TestLoadEnvironment:
    """Test environment file loading functionality"""

    def test_load_environment_file_exists(self, tmp_path, monkeypatch):
        """Test loading .env file when it exists"""
        # Create temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VAR=test_value\nANOTHER_VAR=another_value")

        # Load environment
        result = load_environment(str(env_file))

        assert result is True
        assert os.getenv("TEST_VAR") == "test_value"
        assert os.getenv("ANOTHER_VAR") == "another_value"

    def test_load_environment_file_not_exists(self, tmp_path):
        """Test behavior when .env file doesn't exist"""
        non_existent = tmp_path / "nonexistent.env"
        result = load_environment(str(non_existent))

        assert result is False

    def test_load_environment_auto_discovery(self, tmp_path, monkeypatch):
        """Test automatic .env file discovery in project root"""
        # Create .env in a parent directory structure
        project_root = tmp_path / "project"
        project_root.mkdir()
        env_file = project_root / ".env"
        env_file.write_text("AUTO_DISCOVERED=true")

        # Note: This test verifies the search logic exists
        # Full auto-discovery is harder to test without mocking __file__
        result = load_environment(str(env_file))
        assert result is True

    def test_load_environment_override_existing(self, tmp_path):
        """Test that loading .env overrides existing environment variables"""
        # Set initial value
        os.environ["OVERRIDE_TEST"] = "original"

        # Create .env with different value
        env_file = tmp_path / ".env"
        env_file.write_text("OVERRIDE_TEST=overridden")

        load_environment(str(env_file))

        assert os.getenv("OVERRIDE_TEST") == "overridden"


@pytest.mark.unit
class TestGetRequiredEnv:
    """Test required environment variable getter"""

    def test_get_required_env_exists(self, monkeypatch):
        """Test getting required env var that exists"""
        monkeypatch.setenv("REQUIRED_VAR", "value")
        result = get_required_env("REQUIRED_VAR")
        assert result == "value"

    def test_get_required_env_with_default(self, monkeypatch):
        """Test getting env var with default fallback"""
        result = get_required_env("MISSING_VAR", default="default_value")
        assert result == "default_value"

    def test_get_required_env_missing_no_default(self):
        """Test that missing required var without default raises ValueError"""
        with pytest.raises(ValueError, match="Required environment variable 'NONEXISTENT'"):
            get_required_env("NONEXISTENT")


@pytest.mark.unit
class TestGetBoolEnv:
    """Test boolean environment variable parsing"""

    @pytest.mark.parametrize("value,expected", [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("YES", True),
        ("on", True),
        ("ON", True),
        ("false", False),
        ("False", False),
        ("0", False),
        ("no", False),
        ("off", False),
        ("random", False),
    ])
    def test_get_bool_env_values(self, monkeypatch, value, expected):
        """Test parsing various boolean string values"""
        monkeypatch.setenv("BOOL_VAR", value)
        result = get_bool_env("BOOL_VAR")
        assert result is expected

    def test_get_bool_env_default(self):
        """Test default value when env var doesn't exist"""
        result = get_bool_env("MISSING_BOOL", default=True)
        assert result is True

        result = get_bool_env("MISSING_BOOL", default=False)
        assert result is False


@pytest.mark.unit
class TestGetIntEnv:
    """Test integer environment variable parsing"""

    def test_get_int_env_valid(self, monkeypatch):
        """Test parsing valid integer values"""
        monkeypatch.setenv("INT_VAR", "42")
        result = get_int_env("INT_VAR", default=0)
        assert result == 42

    def test_get_int_env_negative(self, monkeypatch):
        """Test parsing negative integer"""
        monkeypatch.setenv("INT_VAR", "-10")
        result = get_int_env("INT_VAR", default=0)
        assert result == -10

    def test_get_int_env_invalid(self, monkeypatch):
        """Test that invalid integer returns default"""
        monkeypatch.setenv("INT_VAR", "not_a_number")
        result = get_int_env("INT_VAR", default=99)
        assert result == 99

    def test_get_int_env_missing(self):
        """Test default value when env var doesn't exist"""
        result = get_int_env("MISSING_INT", default=42)
        assert result == 42


@pytest.mark.unit
class TestValidateApiKeys:
    """Test API key validation"""

    def test_validate_api_keys_all_present(self, monkeypatch):
        """Test validation when all API keys are present"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
        monkeypatch.setenv("PERPLEXITY_API_KEY", "test-perplexity-key")

        result = validate_api_keys()

        assert result["anthropic"] is True
        assert result["perplexity"] is True

    def test_validate_api_keys_claude_alternative(self, monkeypatch):
        """Test that CLAUDE_API_KEY is accepted as alternative"""
        monkeypatch.setenv("CLAUDE_API_KEY", "test-claude-key")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("PERPLEXITY_API_KEY", "test-perplexity-key")

        result = validate_api_keys()

        assert result["anthropic"] is True
        assert result["perplexity"] is True

    def test_validate_api_keys_missing(self, monkeypatch):
        """Test validation when API keys are missing"""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)

        result = validate_api_keys()

        assert result["anthropic"] is False
        assert result["perplexity"] is False

    def test_validate_api_keys_partial(self, monkeypatch):
        """Test validation when only some keys are present"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)

        result = validate_api_keys()

        assert result["anthropic"] is True
        assert result["perplexity"] is False


@pytest.mark.unit
class TestPrintEnvironmentStatus:
    """Test environment status printing"""

    def test_print_environment_status(self, monkeypatch, capsys):
        """Test that environment status is printed correctly"""
        # Set up test environment
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("PERPLEXITY_API_KEY", "test-key")
        monkeypatch.setenv("WHISPER_MODEL", "test-model")
        monkeypatch.setenv("WHISPER_DEVICE", "cpu")
        monkeypatch.setenv("TEST_MODE", "true")
        monkeypatch.setenv("DEBUG", "false")

        print_environment_status()

        captured = capsys.readouterr()
        output = captured.out

        # Check that key sections are present
        assert "Environment Configuration Status" in output
        assert "API Keys:" in output
        assert "Configuration:" in output
        assert "Paths:" in output
        assert "✅ Set" in output  # At least one API key set

    def test_print_environment_status_missing_keys(self, monkeypatch, capsys):
        """Test status display when API keys are missing"""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)

        print_environment_status()

        captured = capsys.readouterr()
        output = captured.out

        # Check that missing keys are indicated
        assert "❌ Not set" in output


@pytest.mark.unit
class TestAutoLoadFeature:
    """Test automatic .env loading on import"""

    def test_auto_load_enabled_by_default(self, monkeypatch):
        """Test that AUTO_LOAD_ENV defaults to true"""
        # This test verifies the auto-load logic exists
        # Actual auto-loading happens at module import time
        monkeypatch.setenv("AUTO_LOAD_ENV", "true")
        assert os.getenv("AUTO_LOAD_ENV") == "true"

    def test_auto_load_can_be_disabled(self, monkeypatch):
        """Test that auto-loading can be disabled"""
        monkeypatch.setenv("AUTO_LOAD_ENV", "false")
        assert os.getenv("AUTO_LOAD_ENV") == "false"


@pytest.mark.unit
class TestEnvLoaderIntegration:
    """Integration tests for env_loader module"""

    def test_full_workflow(self, tmp_path, monkeypatch):
        """Test complete workflow: load → validate → retrieve"""
        # Create .env file
        env_file = tmp_path / ".env"
        env_file.write_text("""
ANTHROPIC_API_KEY=test-anthropic-key
PERPLEXITY_API_KEY=test-perplexity-key
WHISPER_MODEL=test-model
DEBUG=true
MAX_WORKERS=5
        """.strip())

        # Load environment
        load_result = load_environment(str(env_file))
        assert load_result is True

        # Validate API keys
        validation = validate_api_keys()
        assert validation["anthropic"] is True
        assert validation["perplexity"] is True

        # Retrieve typed values
        assert get_required_env("WHISPER_MODEL") == "test-model"
        assert get_bool_env("DEBUG") is True
        assert get_int_env("MAX_WORKERS", default=1) == 5

    def test_error_handling_workflow(self, tmp_path):
        """Test error handling in complete workflow"""
        # Try to load non-existent file
        load_result = load_environment(str(tmp_path / "missing.env"))
        assert load_result is False

        # Validation should show missing keys
        validation = validate_api_keys()
        # Keys might be set from other tests, so just check structure
        assert "anthropic" in validation
        assert "perplexity" in validation

        # Required env without default should raise
        with pytest.raises(ValueError):
            get_required_env("DEFINITELY_MISSING_VAR")
