"""
Pytest Configuration and Shared Fixtures
Provides common test fixtures and configuration for all tests

Author: Claude Code Assistant
Date: 2025-10-04
"""

import os
import sys
import pytest
import asyncio
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock

# Add automation directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "automation"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Test environment configuration
os.environ.setdefault("TEST_MODE", "true")
os.environ.setdefault("TEST_WITH_WHISPER", "false")

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_config():
    """Provide mock configuration for testing"""
    return {
        "paths": {
            "input_audio": "input/audio",
            "input_video": "input/video",
            "input_text": "input/text",
            "input_processed": "input/processed",
            "digital_garden": "digital-garden",
            "templates": "automation/templates",
            "logs": "logs"
        },
        "transcription": {
            "model_name": "kotoba-tech/kotoba-whisper-v2.0",
            "device": "cpu",
            "compute_type": "float16",
            "supported_formats": ["mp3", "wav", "flac", "m4a", "ogg"],
            "min_confidence": 0.7,
            "language": "ja",
            "task": "transcribe"
        },
        "classification": {
            "api_key": os.getenv("ANTHROPIC_API_KEY", "test-api-key"),
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4000,
            "temperature": 0.7,
            "timeout": 60,
            "max_retries": 3
        },
        "research": {
            "api_key": os.getenv("PERPLEXITY_API_KEY", "test-api-key"),
            "model": "llama-3.1-sonar-small-128k-online",
            "max_tokens": 2000,
            "temperature": 0.2,
            "timeout": 45,
            "max_retries": 3
        },
        "git": {
            "repository_path": ".",
            "main_branch": "main",
            "feature_branch_prefix": "automation/",
            "auto_push": False,  # Disabled for tests
            "create_pr": False   # Disabled for tests
        },
        "performance": {
            "max_concurrent_transcriptions": 2,
            "max_concurrent_classifications": 5,
            "max_concurrent_research": 3
        },
        "logging": {
            "level": "DEBUG",
            "file_enabled": True,
            "console_enabled": True,
            "file_path": "logs/test_automation.log"
        }
    }

@pytest.fixture
def sample_audio_metadata():
    """Sample audio metadata for testing"""
    return {
        "duration_seconds": 120.5,
        "sample_rate": 16000,
        "channels": 1,
        "format": "mp3",
        "file_size_bytes": 1024000
    }

@pytest.fixture
def sample_transcription_result():
    """Sample transcription result for testing"""
    return {
        "text": "これはテストの転写テキストです。AIと機械学習について説明しています。",
        "confidence": 0.95,
        "segments": [
            {
                "start_time": 0.0,
                "end_time": 5.0,
                "text": "これはテストの転写テキストです。",
                "confidence": 0.96
            },
            {
                "start_time": 5.0,
                "end_time": 10.0,
                "text": "AIと機械学習について説明しています。",
                "confidence": 0.94
            }
        ],
        "language_detected": "ja",
        "processing_time": 2.5
    }

@pytest.fixture
def sample_classification_result():
    """Sample classification result for testing"""
    return {
        "category": "insight",
        "title": "AIと機械学習の最新動向",
        "summary": "AIと機械学習技術の最新トレンドについての洞察",
        "priority": "high",
        "tags": ["AI", "機械学習", "テクノロジー"],
        "confidence": 0.92
    }

@pytest.fixture
def sample_research_result():
    """Sample research result for testing"""
    return {
        "query": "AI 機械学習 最新動向",
        "summary": "AI技術は急速に進化しており、様々な分野で活用されています。",
        "sources": [
            {
                "title": "AI技術の最新動向",
                "url": "https://example.com/ai-trends",
                "snippet": "最新のAI技術動向について解説",
                "credibility_score": 0.9
            }
        ],
        "credibility_assessment": {
            "overall_score": 0.85,
            "assessment": "high_credibility"
        }
    }

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic API client"""
    mock = AsyncMock()
    mock.messages = AsyncMock()
    mock.messages.create = AsyncMock()
    return mock

@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for Perplexity API"""
    mock = AsyncMock()
    mock.post = AsyncMock()
    mock.aclose = AsyncMock()
    return mock

@pytest.fixture
def temp_test_dir(tmp_path):
    """Create temporary test directory structure"""
    test_dir = tmp_path / "test_workspace"
    test_dir.mkdir()

    # Create input directories
    (test_dir / "input" / "audio").mkdir(parents=True)
    (test_dir / "input" / "video").mkdir(parents=True)
    (test_dir / "input" / "text").mkdir(parents=True)
    (test_dir / "input" / "processed").mkdir(parents=True)

    # Create output directory
    (test_dir / "output").mkdir()

    return test_dir

@pytest.fixture
def sample_text_file(temp_test_dir):
    """Create a sample text file for testing"""
    text_file = temp_test_dir / "input" / "text" / "sample.txt"
    text_file.write_text(
        "これはテストファイルです。\n"
        "AIと機械学習について記載されています。\n"
        "ビジネスへの応用例も含まれています。",
        encoding="utf-8"
    )
    return text_file

@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test"""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def skip_if_no_api_keys():
    """Skip test if API keys are not available"""
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    perplexity_key = os.getenv("PERPLEXITY_API_KEY")

    if not anthropic_key or anthropic_key == "test-api-key":
        pytest.skip("ANTHROPIC_API_KEY not set")

    if not perplexity_key or perplexity_key == "test-api-key":
        pytest.skip("PERPLEXITY_API_KEY not set")

@pytest.fixture
def skip_if_no_whisper():
    """Skip test if Whisper testing is not enabled"""
    if os.getenv("TEST_WITH_WHISPER", "false").lower() != "true":
        pytest.skip("Whisper testing not enabled (set TEST_WITH_WHISPER=true)")

# Markers for pytest
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interaction"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests with browser automation"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer than 5 seconds"
    )
    config.addinivalue_line(
        "markers", "api: Tests that require API keys and external services"
    )
    config.addinivalue_line(
        "markers", "skip_ci: Tests to skip in CI environment"
    )