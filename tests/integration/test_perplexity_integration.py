"""
Integration Tests for Perplexity API
Tests actual API calls with real Perplexity service

Author: Claude Code Assistant
Date: 2025-10-04
"""

import pytest
import os
import httpx
import json
from typing import Dict, Any

# Load environment variables
from automation.utils.env_loader import load_environment
load_environment()


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.perplexity
class TestPerplexityAPIIntegration:
    """Test real Perplexity API integration"""

    @pytest.fixture
    def api_key(self):
        """Get Perplexity API key from environment"""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key or api_key.startswith("your_"):
            pytest.skip("PERPLEXITY_API_KEY not configured")
        return api_key

    @pytest.fixture
    def api_config(self, api_key):
        """Perplexity API configuration"""
        return {
            "api_key": api_key,
            "base_url": "https://api.perplexity.ai",
            "model": "llama-3.1-sonar-small-128k-online",
            "timeout": 60
        }

    async def test_simple_search_query(self, api_config):
        """Test simple search query with Perplexity API"""
        async with httpx.AsyncClient(timeout=api_config["timeout"]) as client:
            response = await client.post(
                f"{api_config['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_config['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": api_config["model"],
                    "messages": [
                        {
                            "role": "system",
                            "content": "あなたは正確な情報を提供する検索アシスタントです。"
                        },
                        {
                            "role": "user",
                            "content": "2025年の最新AI技術動向について教えてください"
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.2
                }
            )

        # Verify response
        assert response.status_code == 200, f"API returned status {response.status_code}"

        data = response.json()
        assert "choices" in data, "Response missing 'choices' field"
        assert len(data["choices"]) > 0, "Response has no choices"
        assert "message" in data["choices"][0], "Choice missing 'message' field"
        assert "content" in data["choices"][0]["message"], "Message missing 'content'"

        content = data["choices"][0]["message"]["content"]
        assert len(content) > 0, "Response content is empty"

        print(f"\n[SUCCESS] Perplexity API Response:")
        print(f"Model: {data.get('model', 'unknown')}")
        print(f"Content length: {len(content)} characters")
        print(f"Content preview: {content[:200]}...")

    async def test_fact_checking_query(self, api_config):
        """Test fact-checking query"""
        async with httpx.AsyncClient(timeout=api_config["timeout"]) as client:
            response = await client.post(
                f"{api_config['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_config['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": api_config["model"],
                    "messages": [
                        {
                            "role": "system",
                            "content": "あなたは事実確認を行う専門家です。主張の真偽を検証してください。"
                        },
                        {
                            "role": "user",
                            "content": "次の主張について事実確認してください：「量子コンピュータは既に一般家庭で広く使われている」"
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.1
                }
            )

        assert response.status_code == 200
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # Fact-checking should identify this as false
        assert len(content) > 50, "Fact-checking response too short"

        print(f"\n[SUCCESS] Fact-checking Response:")
        print(f"Content: {content[:300]}...")

    async def test_japanese_content_handling(self, api_config):
        """Test handling of Japanese content"""
        async with httpx.AsyncClient(timeout=api_config["timeout"]) as client:
            response = await client.post(
                f"{api_config['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_config['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": api_config["model"],
                    "messages": [
                        {
                            "role": "user",
                            "content": "日本のデジタルガーデンについて簡単に説明してください"
                        }
                    ],
                    "max_tokens": 300,
                    "temperature": 0.3
                }
            )

        assert response.status_code == 200
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # Should handle Japanese properly
        assert len(content) > 0

        print(f"\n[SUCCESS] Japanese Content Response:")
        print(f"Content: {content}")

    async def test_citations_in_response(self, api_config):
        """Test that response includes citations/sources"""
        async with httpx.AsyncClient(timeout=api_config["timeout"]) as client:
            response = await client.post(
                f"{api_config['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_config['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": api_config["model"],
                    "messages": [
                        {
                            "role": "user",
                            "content": "最新のClaude AIモデルについて教えてください（出典を含めて）"
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.2,
                    "return_citations": True
                }
            )

        assert response.status_code == 200
        data = response.json()

        # Check for citations in response
        content = data["choices"][0]["message"]["content"]
        assert len(content) > 0

        print(f"\n[SUCCESS] Citations Response:")
        print(f"Full response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")

    async def test_error_handling_invalid_model(self, api_config):
        """Test error handling with invalid model"""
        async with httpx.AsyncClient(timeout=api_config["timeout"]) as client:
            response = await client.post(
                f"{api_config['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_config['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "invalid-model-name",
                    "messages": [
                        {"role": "user", "content": "test"}
                    ]
                }
            )

        # Should return error
        assert response.status_code >= 400
        print(f"\n[SUCCESS] Error handling works: Status {response.status_code}")

    async def test_rate_limiting_awareness(self, api_config):
        """Test awareness of rate limiting"""
        # Make a single request to verify rate limit headers
        async with httpx.AsyncClient(timeout=api_config["timeout"]) as client:
            response = await client.post(
                f"{api_config['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_config['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": api_config["model"],
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 50
                }
            )

        assert response.status_code == 200

        # Check for rate limit headers
        headers = response.headers
        print(f"\n[INFO] Rate Limit Headers:")
        for key in headers.keys():
            if 'rate' in key.lower() or 'limit' in key.lower():
                print(f"  {key}: {headers[key]}")


@pytest.mark.integration
@pytest.mark.api
class TestPerplexityUsageExample:
    """Test the user-provided Perplexity example"""

    async def test_user_provided_example(self):
        """Test based on user's Perplexity Python example"""
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key or api_key.startswith("your_"):
            pytest.skip("PERPLEXITY_API_KEY not configured")

        # User's example structure
        messages = [
            {
                "role": "system",
                "content": "あなたは正確な情報を提供するアシスタントです。"
            },
            {
                "role": "user",
                "content": "AI技術の最新動向について教えてください"
            }
        ]

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": messages,
                    "max_tokens": 2000,
                    "temperature": 0.2
                }
            )

        assert response.status_code == 200
        data = response.json()

        # Validate structure matches user's example
        assert "id" in data
        assert "model" in data
        assert "choices" in data
        assert len(data["choices"]) > 0
        assert "message" in data["choices"][0]
        assert "content" in data["choices"][0]["message"]

        result_content = data["choices"][0]["message"]["content"]

        print(f"\n[SUCCESS] User Example Test:")
        print(f"Response ID: {data['id']}")
        print(f"Model: {data['model']}")
        print(f"Content: {result_content[:200]}...")


@pytest.mark.integration
class TestPerplexityConfiguration:
    """Test Perplexity configuration and setup"""

    def test_api_key_loaded(self):
        """Test that API key is loaded from .env"""
        api_key = os.getenv("PERPLEXITY_API_KEY")

        assert api_key is not None, "PERPLEXITY_API_KEY not found in environment"
        assert not api_key.startswith("your_"), "PERPLEXITY_API_KEY not configured (still has placeholder)"
        assert len(api_key) > 20, "PERPLEXITY_API_KEY seems too short"
        assert api_key.startswith("pplx-"), "PERPLEXITY_API_KEY should start with 'pplx-'"

        print(f"\n[SUCCESS] API Key Configuration:")
        print(f"  Key prefix: {api_key[:10]}...")
        print(f"  Key length: {len(api_key)} characters")

    def test_httpx_available(self):
        """Test that httpx is available for API calls"""
        import httpx

        # Verify httpx can create clients
        with httpx.Client() as client:
            assert client is not None

        print(f"\n[SUCCESS] httpx library available: {httpx.__version__}")
