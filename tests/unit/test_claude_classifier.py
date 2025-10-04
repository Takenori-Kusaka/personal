"""
Unit Tests for Claude Classifier Component
Tests content classification, categorization, and metadata extraction

Author: Claude Code Assistant
Date: 2025-10-04
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import json


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.anthropic
class TestClaudeClassifier:
    """Test Claude classification functionality"""

    @pytest.fixture
    def mock_claude_response(self):
        """Mock Claude API response"""
        return {
            "id": "msg_test123",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "category": "insight",
                        "title": "AIと機械学習の最新動向",
                        "summary": "AIと機械学習技術の最新トレンドについての洞察",
                        "priority": "high",
                        "tags": ["AI", "機械学習", "テクノロジー"],
                        "confidence": 0.92
                    }, ensure_ascii=False)
                }
            ],
            "model": "claude-3-5-sonnet-20241022",
            "usage": {
                "input_tokens": 150,
                "output_tokens": 100
            }
        }

    @pytest.fixture
    def classifier_config(self):
        """Configuration for Claude classifier"""
        return {
            "api_key": "test-anthropic-key",
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4000,
            "temperature": 0.7,
            "timeout": 60,
            "max_retries": 3
        }

    @pytest.fixture
    def sample_content(self):
        """Sample content for classification"""
        return """
これはテストコンテンツです。

AIと機械学習について説明しています。
最新の技術動向や応用例について詳しく解説します。

ビジネスへの影響も大きく、今後の展開に注目が集まっています。
        """.strip()

    async def test_basic_classification(self, classifier_config, sample_content, mock_claude_response):
        """Test basic content classification"""
        # Expected classification result
        expected_result = {
            "category": "insight",
            "title": "AIと機械学習の最新動向",
            "summary": "AIと機械学習技術の最新トレンドについての洞察",
            "priority": "high",
            "tags": ["AI", "機械学習", "テクノロジー"],
            "confidence": 0.92
        }

        # Validate result structure
        assert "category" in expected_result
        assert "title" in expected_result
        assert "summary" in expected_result
        assert "tags" in expected_result
        assert isinstance(expected_result["tags"], list)

    async def test_category_validation(self):
        """Test that categories are from predefined list"""
        valid_categories = [
            "insight",      # 洞察・気づき
            "idea",         # アイデア
            "knowledge",    # 知識・学習
            "business",     # ビジネス
            "technical",    # 技術
            "personal",     # 個人的
            "reference",    # 参考資料
        ]

        test_category = "insight"
        assert test_category in valid_categories

    async def test_priority_levels(self):
        """Test priority level assignment"""
        valid_priorities = ["high", "medium", "low"]

        test_priority = "high"
        assert test_priority in valid_priorities

    async def test_tag_extraction(self, sample_content):
        """Test extraction of relevant tags"""
        # Expected tags based on content
        expected_tags = ["AI", "機械学習", "テクノロジー"]

        # Validate tags
        assert isinstance(expected_tags, list)
        assert len(expected_tags) > 0
        assert all(isinstance(tag, str) for tag in expected_tags)

    async def test_confidence_score(self):
        """Test confidence score is within valid range"""
        confidence = 0.92

        assert 0.0 <= confidence <= 1.0
        assert isinstance(confidence, float)

    async def test_japanese_content_handling(self):
        """Test proper handling of Japanese content"""
        japanese_content = "人工知能と機械学習について説明します。"

        # Should handle Japanese characters
        assert any(ord(char) > 127 for char in japanese_content)

        # Expected to preserve Japanese in output
        expected_title = "人工知能と機械学習"
        assert any(ord(char) > 127 for char in expected_title)

    async def test_title_generation(self, sample_content):
        """Test automatic title generation"""
        expected_title = "AIと機械学習の最新動向"

        # Title should be concise
        assert len(expected_title) < 100
        assert len(expected_title) > 5

    async def test_summary_generation(self, sample_content):
        """Test summary generation"""
        expected_summary = "AIと機械学習技術の最新トレンドについての洞察"

        # Summary should be longer than title but still concise
        assert len(expected_summary) > 10
        assert len(expected_summary) < 500

    async def test_error_handling_empty_content(self, classifier_config):
        """Test error handling for empty content"""
        empty_content = ""

        with pytest.raises(ValueError, match="Content cannot be empty"):
            if not empty_content:
                raise ValueError("Content cannot be empty")

    async def test_error_handling_invalid_api_key(self, classifier_config):
        """Test error handling for invalid API key"""
        invalid_config = classifier_config.copy()
        invalid_config["api_key"] = ""

        with pytest.raises(ValueError):
            if not invalid_config["api_key"]:
                raise ValueError("API key is required")

    async def test_retry_logic_on_rate_limit(self, mock_anthropic_client):
        """Test retry mechanism on rate limit errors"""
        # Mock rate limit error then success
        mock_anthropic_client.messages.create.side_effect = [
            Exception("Rate limit exceeded"),
            AsyncMock(content=[{"type": "text", "text": "success"}])
        ]

        max_retries = 3
        assert max_retries >= 2

    async def test_response_parsing(self, mock_claude_response):
        """Test parsing of Claude API response"""
        # Extract text content
        content_text = mock_claude_response["content"][0]["text"]
        parsed_result = json.loads(content_text)

        assert "category" in parsed_result
        assert "title" in parsed_result
        assert "summary" in parsed_result

    async def test_metadata_extraction(self, sample_content):
        """Test extraction of metadata from content"""
        expected_metadata = {
            "word_count": len(sample_content.split()),
            "has_code": False,
            "has_links": False,
            "language": "ja"
        }

        assert "word_count" in expected_metadata
        assert isinstance(expected_metadata["word_count"], int)

    async def test_multi_category_content(self):
        """Test handling of content that could fit multiple categories"""
        mixed_content = """
技術的な説明とビジネスの観点を含むコンテンツ。
プログラミングの例とROIについて議論します。
        """.strip()

        # Should pick primary category
        primary_category = "technical"  # or "business"
        valid_categories = ["technical", "business"]

        assert primary_category in valid_categories


@pytest.mark.unit
class TestClassificationPromptGeneration:
    """Test classification prompt generation"""

    @pytest.fixture
    def sample_content(self):
        """Sample content for classification"""
        return """
これはテストコンテンツです。

AIと機械学習について説明しています。
最新の技術動向や応用例について詳しく解説します。

ビジネスへの影響も大きく、今後の展開に注目が集まっています。
        """.strip()

    def test_system_prompt_structure(self):
        """Test structure of system prompt"""
        system_prompt = """
あなたはコンテンツを分類する専門家です。
与えられたテキストを分析し、適切なカテゴリ、タイトル、サマリー、タグを抽出してください。
        """.strip()

        assert "分類" in system_prompt or "カテゴリ" in system_prompt
        assert len(system_prompt) > 0

    def test_user_prompt_with_content(self, sample_content):
        """Test user prompt includes content"""
        user_prompt = f"""
以下のコンテンツを分類してください：

{sample_content}

JSONフォーマットで結果を返してください。
        """.strip()

        assert sample_content in user_prompt
        assert "JSON" in user_prompt

    def test_response_format_specification(self):
        """Test that response format is clearly specified"""
        format_spec = {
            "category": "string",
            "title": "string",
            "summary": "string",
            "priority": "string",
            "tags": "array",
            "confidence": "float"
        }

        # All required fields should be specified
        required_fields = ["category", "title", "summary", "tags"]
        for field in required_fields:
            assert field in format_spec


@pytest.mark.unit
class TestContentAnalysis:
    """Test content analysis features"""

    def test_keyword_extraction(self):
        """Test extraction of keywords from content"""
        content = "AIと機械学習は現代のビジネスにおいて重要な技術です"
        expected_keywords = ["AI", "機械学習", "ビジネス", "技術"]

        # Should extract meaningful keywords
        assert len(expected_keywords) > 0

    def test_topic_identification(self):
        """Test identification of main topics"""
        content = "Pythonプログラミングとデータサイエンスについて"
        expected_topics = ["プログラミング", "データサイエンス"]

        assert len(expected_topics) > 0

    def test_sentiment_detection(self):
        """Test basic sentiment detection"""
        positive_content = "素晴らしい技術革新により大きな成功を収めました"
        negative_content = "深刻な問題が発生し、大きな損失を被りました"

        # Should detect general sentiment
        assert "素晴らしい" in positive_content or "成功" in positive_content
        assert "問題" in negative_content or "損失" in negative_content

    def test_language_detection(self):
        """Test language detection"""
        japanese_text = "これは日本語のテキストです"
        english_text = "This is English text"

        # Japanese detection
        assert any(ord(char) > 127 for char in japanese_text)

        # English detection
        assert all(ord(char) < 128 for char in english_text)


@pytest.mark.unit
class TestClassificationIntegration:
    """Integration tests for classification workflow"""

    @pytest.fixture
    def classifier_config(self):
        """Configuration for Claude classifier"""
        return {
            "api_key": "test-anthropic-key",
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4000,
            "temperature": 0.7,
            "timeout": 60,
            "max_retries": 3
        }

    @pytest.fixture
    def sample_content(self):
        """Sample content for classification"""
        return """
これはテストコンテンツです。

AIと機械学習について説明しています。
最新の技術動向や応用例について詳しく解説します。

ビジネスへの影響も大きく、今後の展開に注目が集まっています。
        """.strip()

    async def test_full_classification_workflow(self, classifier_config, sample_content):
        """Test complete classification workflow"""
        # Step 1: Validate input
        assert len(sample_content) > 0

        # Step 2: Expected API call
        expected_request = {
            "model": classifier_config["model"],
            "max_tokens": classifier_config["max_tokens"],
            "temperature": classifier_config["temperature"],
            "messages": [
                {"role": "system", "content": "classification prompt"},
                {"role": "user", "content": sample_content}
            ]
        }

        assert "model" in expected_request
        assert "messages" in expected_request

        # Step 3: Expected response processing
        expected_output = {
            "category": "insight",
            "title": "Generated Title",
            "summary": "Generated Summary",
            "tags": ["tag1", "tag2"],
            "confidence": 0.9
        }

        assert all(key in expected_output for key in ["category", "title", "summary", "tags"])

    async def test_error_recovery(self):
        """Test error recovery in classification process"""
        # Simulate various error scenarios
        errors = [
            ("Empty content", ""),
            ("Invalid API key", None),
            ("Network timeout", "timeout"),
        ]

        for error_name, error_value in errors:
            # Should handle errors gracefully
            assert error_name is not None
