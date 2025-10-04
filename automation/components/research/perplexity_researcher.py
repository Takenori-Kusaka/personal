"""
Perplexity Research and Fact Verification System
Intelligent research enhancement and fact-checking using Perplexity API

Author: Claude Code Assistant
Date: 2025-10-04
Version: 2.0
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import re

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from automation.config.settings import PerplexityConfig
from automation.utils.logging_setup import StructuredLogger, PerformanceTracker
from automation.utils.file_handler import FileHandler

@dataclass
class ResearchQuery:
    """Research query structure"""
    query: str
    context: str
    priority: str = "medium"
    recency_filter: str = "month"
    max_results: int = 5

@dataclass
class ResearchSource:
    """Research source information"""
    title: str
    url: str
    snippet: str
    published_date: Optional[str] = None
    credibility_score: float = 0.0
    relevance_score: float = 0.0

@dataclass
class ResearchResult:
    """Complete research result structure"""
    query: str
    summary: str
    sources: List[ResearchSource]
    fact_check_results: List[Dict[str, Any]] = field(default_factory=list)
    credibility_assessment: Dict[str, Any] = field(default_factory=dict)
    research_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class PerplexityResearcher:
    """
    Perplexity-powered research and fact verification system
    Enhances content with current information and credibility checks
    """

    def __init__(self, config: PerplexityConfig):
        """Initialize the Perplexity researcher"""
        self.config = config
        self.logger = StructuredLogger('perplexity_researcher')
        self.file_handler = FileHandler()

        self.client = None
        self.cache = {}
        self.cache_ttl = timedelta(hours=24)

        if not HTTPX_AVAILABLE:
            self.logger.error("httpx library not available")
            return

        if not config.api_key:
            self.logger.error("Perplexity API key not configured")
            return

        self._initialize_client()

    def _initialize_client(self):
        """Initialize HTTP client for Perplexity API"""
        try:
            self.client = httpx.AsyncClient(
                timeout=self.config.timeout,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                }
            )
            self.logger.info("Perplexity client initialized", model=self.config.model)
        except Exception as e:
            self.logger.error("Failed to initialize Perplexity client", error=e)

    async def research_content(self, content_data: Dict[str, Any]) -> Optional[ResearchResult]:
        """
        Research content with fact verification and enhancement

        Args:
            content_data: Content data including text, category, and metadata

        Returns:
            ResearchResult or None if failed
        """
        if not self.client:
            self.logger.error("Perplexity client not initialized")
            return None

        with PerformanceTracker(self.logger, "content_research") as tracker:
            try:
                # Generate research queries from content
                queries = self._generate_research_queries(content_data)
                if not queries:
                    self.logger.warning("No research queries generated", content_length=len(content_data.get('text', '')))
                    return None

                tracker.add_metric('queries_generated', len(queries))

                # Execute research queries
                research_results = []
                for query in queries:
                    result = await self._execute_research_query(query)
                    if result:
                        research_results.append(result)

                if not research_results:
                    self.logger.warning("No research results obtained")
                    return None

                # Consolidate research results
                consolidated_result = self._consolidate_research_results(
                    research_results, content_data
                )

                # Perform fact checking
                fact_check_results = await self._perform_fact_checking(
                    content_data, consolidated_result
                )
                consolidated_result.fact_check_results = fact_check_results

                # Assess overall credibility
                credibility_assessment = self._assess_credibility(consolidated_result)
                consolidated_result.credibility_assessment = credibility_assessment

                tracker.add_metric('sources_found', len(consolidated_result.sources))
                tracker.add_metric('credibility_score', credibility_assessment.get('overall_score', 0.0))

                self.logger.info("Content research completed",
                               queries=len(queries),
                               sources=len(consolidated_result.sources),
                               credibility=f"{credibility_assessment.get('overall_score', 0.0):.2f}")

                return consolidated_result

            except Exception as e:
                self.logger.error("Content research failed", error=e)
                return None

    def _generate_research_queries(self, content_data: Dict[str, Any]) -> List[ResearchQuery]:
        """Generate research queries based on content analysis"""
        queries = []
        text = content_data.get('text', '')
        category = content_data.get('category', 'insight')
        title = content_data.get('title', '')

        if not text:
            return queries

        try:
            # Extract key concepts for research
            key_concepts = self._extract_key_concepts(text)
            factual_claims = self._extract_factual_claims(text)

            # Generate queries based on category
            if category == 'insight':
                # Research market trends, competitor analysis, industry data
                for concept in key_concepts[:3]:
                    queries.append(ResearchQuery(
                        query=f"{concept} 市場トレンド 2024",
                        context=f"Researching market trends for: {concept}",
                        priority="high",
                        recency_filter=self.config.search_recency_filter
                    ))

                # Research factual claims
                for claim in factual_claims[:2]:
                    queries.append(ResearchQuery(
                        query=f"{claim} 事実確認",
                        context=f"Fact-checking claim: {claim}",
                        priority="medium",
                        recency_filter="month"
                    ))

            elif category == 'diary':
                # Research events or topics mentioned
                if key_concepts:
                    main_concept = key_concepts[0]
                    queries.append(ResearchQuery(
                        query=f"{main_concept} 最新情報",
                        context=f"Current information about: {main_concept}",
                        priority="low",
                        recency_filter="week"
                    ))

            elif category == 'resume':
                # Research industry standards, skill requirements
                for concept in key_concepts[:2]:
                    if any(tech_keyword in concept.lower() for tech_keyword in ['技術', 'スキル', 'ツール', 'プログラミング']):
                        queries.append(ResearchQuery(
                            query=f"{concept} 業界標準 要求スキル",
                            context=f"Industry standards for: {concept}",
                            priority="medium",
                            recency_filter="month"
                        ))

            # Add title-based query if title is informative
            if title and len(title) > 10:
                queries.append(ResearchQuery(
                    query=f"{title} 関連情報",
                    context=f"General research for: {title}",
                    priority="low",
                    recency_filter=self.config.search_recency_filter
                ))

            self.logger.debug("Research queries generated",
                            concepts=len(key_concepts),
                            claims=len(factual_claims),
                            queries=len(queries))

            return queries[:5]  # Limit to 5 queries max

        except Exception as e:
            self.logger.error("Failed to generate research queries", error=e)
            return []

    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text for research"""
        concepts = []

        # Simple keyword extraction (could be enhanced with NLP)
        text_lower = text.lower()

        # Business/tech keywords
        business_keywords = [
            'ai', '人工知能', 'machine learning', '機械学習', 'データ分析', 'クラウド',
            'デジタル変革', 'dx', 'イノベーション', 'スタートアップ', 'ビジネスモデル',
            'マーケティング', 'セールス', 'カスタマー', '顧客体験', 'ux', 'ui',
            'プロダクト', '製品開発', 'アジャイル', 'scrum', 'devops'
        ]

        # Extract sentences containing business keywords
        sentences = re.split(r'[。！？\n]', text)
        for sentence in sentences:
            for keyword in business_keywords:
                if keyword in sentence.lower():
                    # Extract noun phrases around the keyword
                    words = sentence.split()
                    for i, word in enumerate(words):
                        if keyword in word.lower():
                            # Take surrounding context
                            start = max(0, i - 2)
                            end = min(len(words), i + 3)
                            concept = ' '.join(words[start:end])
                            if len(concept) > 5 and concept not in concepts:
                                concepts.append(concept[:50])
                            break

        # Extract potential company/product names (capitalized words)
        capitalized_words = re.findall(r'\b[A-Z][a-zA-Z]{2,}\b', text)
        for word in capitalized_words:
            if len(word) > 3 and word not in concepts:
                concepts.append(word)

        return concepts[:10]  # Return top 10 concepts

    def _extract_factual_claims(self, text: str) -> List[str]:
        """Extract factual claims that can be fact-checked"""
        claims = []

        # Look for numerical claims
        numerical_patterns = [
            r'\d+%',  # Percentages
            r'\d+億円',  # Yen amounts
            r'\d+万人',  # People counts
            r'20\d{2}年',  # Years
            r'\d+倍',  # Multipliers
        ]

        sentences = re.split(r'[。！？\n]', text)
        for sentence in sentences:
            # Check if sentence contains numerical data
            for pattern in numerical_patterns:
                if re.search(pattern, sentence):
                    if len(sentence.strip()) > 10:
                        claims.append(sentence.strip()[:100])
                    break

        # Look for definitive statements
        definitive_patterns = [
            r'によると',  # According to
            r'調査では',  # Survey shows
            r'発表した',  # Announced
            r'報告されている',  # Reported
            r'明らかになった',  # Revealed
        ]

        for sentence in sentences:
            for pattern in definitive_patterns:
                if re.search(pattern, sentence):
                    if len(sentence.strip()) > 15:
                        claims.append(sentence.strip()[:100])
                    break

        return list(set(claims))[:5]  # Remove duplicates, return top 5

    async def _execute_research_query(self, query: ResearchQuery) -> Optional[ResearchResult]:
        """Execute a single research query using Perplexity API"""
        try:
            # Check cache first
            cache_key = self._generate_cache_key(query.query)
            if cache_key in self.cache:
                cached_result, cached_time = self.cache[cache_key]
                if datetime.now() - cached_time < self.cache_ttl:
                    self.logger.debug("Using cached result", query=query.query[:50])
                    return cached_result

            # Prepare API request
            api_url = "https://api.perplexity.ai/chat/completions"

            # Build search-focused prompt
            search_prompt = f"""以下について最新の信頼性の高い情報を調査してください：

{query.query}

以下の形式で回答してください：
1. 要約（2-3文）
2. 主要な発見事項
3. 情報源の詳細（URL、発行日、信頼性）

回答は日本語でお願いします。最新の情報を優先してください。"""

            request_data = {
                "model": self.config.model,
                "messages": [
                    {"role": "user", "content": search_prompt}
                ],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "search_domain_filter": ["perplexity.ai"],
                "return_citations": True,
                "search_recency_filter": query.recency_filter
            }

            # Make API request with retries
            for attempt in range(self.config.max_retries):
                try:
                    response = await self.client.post(api_url, json=request_data)
                    response.raise_for_status()

                    result = response.json()

                    if "choices" in result and result["choices"]:
                        content = result["choices"][0]["message"]["content"]
                        citations = result.get("citations", [])

                        # Parse response into structured result
                        research_result = self._parse_research_response(
                            query.query, content, citations
                        )

                        # Cache result
                        self.cache[cache_key] = (research_result, datetime.now())

                        return research_result
                    else:
                        self.logger.warning("Empty response from Perplexity API")
                        return None

                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:  # Rate limit
                        wait_time = self.config.retry_delay * (2 ** attempt)
                        self.logger.warning(f"Rate limited, waiting {wait_time}s", attempt=attempt)
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        self.logger.error("HTTP error from Perplexity API", status_code=e.response.status_code)
                        break
                except Exception as e:
                    self.logger.warning(f"Perplexity API call failed (attempt {attempt + 1})", error=e)
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(self.config.retry_delay)

            return None

        except Exception as e:
            self.logger.error("Research query execution failed", error=e)
            return None

    def _parse_research_response(self, query: str, content: str, citations: List[Dict]) -> ResearchResult:
        """Parse Perplexity API response into structured result"""
        try:
            # Extract summary (first paragraph)
            paragraphs = content.split('\n\n')
            summary = paragraphs[0] if paragraphs else content[:200]

            # Convert citations to sources
            sources = []
            for citation in citations[:5]:  # Limit to 5 sources
                source = ResearchSource(
                    title=citation.get('title', 'Unknown Title'),
                    url=citation.get('url', ''),
                    snippet=citation.get('text', '')[:200],
                    published_date=citation.get('published_date'),
                    credibility_score=self._assess_source_credibility(citation),
                    relevance_score=self._assess_source_relevance(citation, query)
                )
                sources.append(source)

            return ResearchResult(
                query=query,
                summary=summary,
                sources=sources,
                research_time=0.0,  # Will be set by caller
                metadata={
                    'timestamp': datetime.now().isoformat(),
                    'api_model': self.config.model,
                    'original_content': content,
                    'citation_count': len(citations)
                }
            )

        except Exception as e:
            self.logger.error("Failed to parse research response", error=e)
            # Return minimal result
            return ResearchResult(
                query=query,
                summary=content[:200] if content else "Research completed",
                sources=[],
                metadata={'error': str(e)}
            )

    def _assess_source_credibility(self, citation: Dict[str, Any]) -> float:
        """Assess credibility of a research source"""
        credibility_score = 0.5  # Base score

        url = citation.get('url', '').lower()
        title = citation.get('title', '').lower()

        # High credibility domains
        high_credibility_domains = [
            'gov.jp', '.go.jp', 'jiji.com', 'nikkei.com', 'reuters.com',
            'bloomberg.com', 'wsj.com', 'harvard.edu', '.edu',
            'nature.com', 'science.org', 'ieee.org'
        ]

        # Medium credibility domains
        medium_credibility_domains = [
            'yahoo.co.jp', 'mainichi.jp', 'asahi.com', 'yomiuri.co.jp',
            'techcrunch.com', 'forbes.com', 'businessinsider.com'
        ]

        # Check domain credibility
        for domain in high_credibility_domains:
            if domain in url:
                credibility_score = max(credibility_score, 0.9)
                break

        for domain in medium_credibility_domains:
            if domain in url:
                credibility_score = max(credibility_score, 0.7)
                break

        # Boost for academic or official sources
        if any(term in title for term in ['研究', '調査', '報告書', 'study', 'report']):
            credibility_score += 0.1

        # Check for date recency (if available)
        published_date = citation.get('published_date')
        if published_date:
            try:
                pub_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                days_old = (datetime.now() - pub_date.replace(tzinfo=None)).days
                if days_old < 30:  # Recent content
                    credibility_score += 0.05
            except:
                pass  # Invalid date format

        return min(1.0, credibility_score)

    def _assess_source_relevance(self, citation: Dict[str, Any], query: str) -> float:
        """Assess relevance of source to the query"""
        relevance_score = 0.5  # Base score

        title = citation.get('title', '').lower()
        snippet = citation.get('text', '').lower()
        query_lower = query.lower()

        # Check for query terms in title (higher weight)
        query_terms = query_lower.split()
        title_matches = sum(1 for term in query_terms if term in title)
        relevance_score += (title_matches / len(query_terms)) * 0.3

        # Check for query terms in snippet
        snippet_matches = sum(1 for term in query_terms if term in snippet)
        relevance_score += (snippet_matches / len(query_terms)) * 0.2

        return min(1.0, relevance_score)

    def _consolidate_research_results(self, results: List[ResearchResult], content_data: Dict[str, Any]) -> ResearchResult:
        """Consolidate multiple research results into a single comprehensive result"""
        if not results:
            return ResearchResult(
                query="consolidated",
                summary="No research results to consolidate",
                sources=[]
            )

        # Combine all sources and deduplicate
        all_sources = []
        seen_urls = set()

        for result in results:
            for source in result.sources:
                if source.url not in seen_urls:
                    all_sources.append(source)
                    seen_urls.add(source.url)

        # Sort sources by credibility and relevance
        all_sources.sort(key=lambda s: s.credibility_score * s.relevance_score, reverse=True)

        # Create consolidated summary
        summaries = [result.summary for result in results if result.summary]
        consolidated_summary = self._create_consolidated_summary(summaries, content_data)

        # Calculate total research time
        total_research_time = sum(result.research_time for result in results)

        return ResearchResult(
            query=f"consolidated_{len(results)}_queries",
            summary=consolidated_summary,
            sources=all_sources[:10],  # Top 10 sources
            research_time=total_research_time,
            metadata={
                'consolidated_from': len(results),
                'total_sources': len(all_sources),
                'timestamp': datetime.now().isoformat()
            }
        )

    def _create_consolidated_summary(self, summaries: List[str], content_data: Dict[str, Any]) -> str:
        """Create a consolidated summary from multiple research summaries"""
        if not summaries:
            return "調査結果なし"

        # Simple consolidation - could be enhanced with AI summarization
        key_points = []
        for summary in summaries:
            # Extract key sentences (first sentence of each summary)
            first_sentence = summary.split('。')[0] + '。'
            if first_sentence and len(first_sentence) > 10:
                key_points.append(first_sentence)

        if not key_points:
            return summaries[0][:200] if summaries else "調査完了"

        # Combine key points
        consolidated = '\n'.join(f"• {point}" for point in key_points[:5])
        return f"調査結果:\n{consolidated}"

    async def _perform_fact_checking(self, content_data: Dict[str, Any], research_result: ResearchResult) -> List[Dict[str, Any]]:
        """Perform fact-checking of content claims against research results"""
        fact_check_results = []

        try:
            # Extract factual claims from content
            claims = self._extract_factual_claims(content_data.get('text', ''))

            for claim in claims[:3]:  # Limit to 3 claims
                fact_check = await self._verify_claim(claim, research_result)
                if fact_check:
                    fact_check_results.append(fact_check)

        except Exception as e:
            self.logger.error("Fact checking failed", error=e)

        return fact_check_results

    async def _verify_claim(self, claim: str, research_result: ResearchResult) -> Optional[Dict[str, Any]]:
        """Verify a single claim against research sources"""
        try:
            # Simple fact verification - could be enhanced with more sophisticated matching
            supporting_sources = []
            contradicting_sources = []

            # Check claim against source snippets
            claim_lower = claim.lower()
            for source in research_result.sources:
                snippet_lower = source.snippet.lower()

                # Look for supporting evidence (simple keyword matching)
                if any(word in snippet_lower for word in claim_lower.split() if len(word) > 3):
                    supporting_sources.append(source)

            # Determine verification status
            if len(supporting_sources) >= 2:
                status = "verified"
            elif len(supporting_sources) == 1:
                status = "partially_verified"
            else:
                status = "unverified"

            return {
                "claim": claim,
                "status": status,
                "supporting_sources": len(supporting_sources),
                "contradicting_sources": len(contradicting_sources),
                "confidence": min(1.0, len(supporting_sources) * 0.3),
                "sources": [{"title": s.title, "url": s.url} for s in supporting_sources[:3]]
            }

        except Exception as e:
            self.logger.error("Claim verification failed", error=e, claim=claim[:50])
            return None

    def _assess_credibility(self, research_result: ResearchResult) -> Dict[str, Any]:
        """Assess overall credibility of research results"""
        try:
            if not research_result.sources:
                return {"overall_score": 0.0, "assessment": "no_sources"}

            # Calculate average source credibility
            avg_credibility = sum(s.credibility_score for s in research_result.sources) / len(research_result.sources)

            # Factor in fact-check results
            fact_check_boost = 0.0
            if research_result.fact_check_results:
                verified_count = sum(1 for fc in research_result.fact_check_results if fc['status'] == 'verified')
                fact_check_boost = (verified_count / len(research_result.fact_check_results)) * 0.2

            # Calculate overall credibility score
            overall_score = min(1.0, avg_credibility + fact_check_boost)

            # Determine assessment category
            if overall_score >= 0.8:
                assessment = "high_credibility"
            elif overall_score >= 0.6:
                assessment = "medium_credibility"
            elif overall_score >= 0.4:
                assessment = "low_credibility"
            else:
                assessment = "unreliable"

            return {
                "overall_score": overall_score,
                "assessment": assessment,
                "source_count": len(research_result.sources),
                "avg_source_credibility": avg_credibility,
                "fact_check_boost": fact_check_boost,
                "verified_claims": sum(1 for fc in research_result.fact_check_results if fc['status'] == 'verified'),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error("Credibility assessment failed", error=e)
            return {"overall_score": 0.0, "assessment": "error"}

    def _generate_cache_key(self, query: str) -> str:
        """Generate cache key for research query"""
        return hashlib.md5(query.encode('utf-8')).hexdigest()[:16]

    def get_researcher_info(self) -> Dict[str, Any]:
        """Get information about the researcher"""
        return {
            "model": self.config.model,
            "available": self.client is not None,
            "httpx_available": HTTPX_AVAILABLE,
            "cache_entries": len(self.cache),
            "cache_ttl_hours": self.cache_ttl.total_seconds() / 3600
        }

    async def cleanup_cache(self):
        """Clean up expired cache entries"""
        current_time = datetime.now()
        expired_keys = [
            key for key, (_, cached_time) in self.cache.items()
            if current_time - cached_time > self.cache_ttl
        ]

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            self.logger.info("Cache cleanup completed", expired_entries=len(expired_keys))

    async def close(self):
        """Clean up resources"""
        if self.client:
            await self.client.aclose()
            self.logger.info("Perplexity client closed")