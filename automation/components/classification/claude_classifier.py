"""
Claude Classification and Content Generation System
Intelligent content classification and structured content generation using Claude API

Author: Claude Code Assistant
Date: 2025-10-04
Version: 2.0
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from automation.config.settings import ClaudeConfig
from automation.utils.logging_setup import StructuredLogger, PerformanceTracker
from automation.utils.file_handler import FileHandler

@dataclass
class ClassificationResult:
    """Content classification result structure"""
    category: str  # insight, diary, resume, profile
    title: str
    summary: str
    priority: str  # urgent, high, medium, low
    tags: List[str]
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentTemplate:
    """Template for structured content generation"""
    frontmatter: Dict[str, Any]
    content_structure: Dict[str, str]
    astro_components: List[str] = field(default_factory=list)

class ClaudeClassifier:
    """
    Claude-powered content classifier and generator
    Handles intelligent content routing and structured content creation
    """

    def __init__(self, config: ClaudeConfig):
        """Initialize the Claude classifier"""
        self.config = config
        self.logger = StructuredLogger('claude_classifier')
        self.file_handler = FileHandler()

        self.client = None
        self.templates = {}

        if not ANTHROPIC_AVAILABLE:
            self.logger.error("Anthropic library not available")
            return

        if not config.api_key:
            self.logger.error("Claude API key not configured")
            return

        self._initialize_client()
        self._load_templates()

    def _initialize_client(self):
        """Initialize Anthropic client"""
        try:
            self.client = anthropic.Anthropic(
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
            self.logger.info("Claude client initialized", model=self.config.model)
        except Exception as e:
            self.logger.error("Failed to initialize Claude client", error=e)

    def _load_templates(self):
        """Load content generation templates"""
        templates_path = Path("automation/templates")

        # Default templates if files don't exist
        self.templates = {
            "insight": {
                "frontmatter_template": """---
title: "{title}"
description: "{summary}"
category: "insight"
date: {date}
tags: {tags}
priority: "{priority}"
source: "{source_file}"
impact:
  business_value: null
  implementation_feasibility: null
  social_impact: null
  strategic_alignment: null
confidence: {confidence}
processing:
  session_id: "{session_id}"
  generated_at: "{generated_at}"
  model: "{model}"
---""",
                "content_structure": {
                    "overview": "## 概要\n\n{overview}",
                    "details": "## 詳細\n\n{details}",
                    "implications": "## 示唆\n\n{implications}",
                    "action_items": "## アクション\n\n{action_items}",
                    "references": "## 参考\n\n{references}"
                },
                "astro_components": ["ImpactAnalysis", "MermaidDiagram"]
            },
            "diary": {
                "frontmatter_template": """---
title: "{title}"
description: "{summary}"
category: "diary"
date: {date}
tags: {tags}
priority: "{priority}"
source: "{source_file}"
mood: null
location: null
weather: null
processing:
  session_id: "{session_id}"
  generated_at: "{generated_at}"
  model: "{model}"
---""",
                "content_structure": {
                    "reflection": "## 振り返り\n\n{reflection}",
                    "events": "## 出来事\n\n{events}",
                    "thoughts": "## 考え\n\n{thoughts}",
                    "learnings": "## 学び\n\n{learnings}",
                    "tomorrow": "## 明日に向けて\n\n{tomorrow}"
                },
                "astro_components": []
            },
            "resume": {
                "frontmatter_template": """---
title: "{title}"
description: "{summary}"
category: "resume"
date: {date}
tags: {tags}
priority: "{priority}"
source: "{source_file}"
skill_level: null
years_experience: null
certification: null
processing:
  session_id: "{session_id}"
  generated_at: "{generated_at}"
  model: "{model}"
---""",
                "content_structure": {
                    "experience": "## 経験\n\n{experience}",
                    "skills": "## スキル\n\n{skills}",
                    "achievements": "## 実績\n\n{achievements}",
                    "technologies": "## 技術\n\n{technologies}"
                },
                "astro_components": []
            },
            "profile": {
                "frontmatter_template": """---
title: "{title}"
description: "{summary}"
category: "profile"
date: {date}
tags: {tags}
priority: "{priority}"
source: "{source_file}"
visibility: "private"
processing:
  session_id: "{session_id}"
  generated_at: "{generated_at}"
  model: "{model}"
---""",
                "content_structure": {
                    "background": "## 背景\n\n{background}",
                    "interests": "## 興味\n\n{interests}",
                    "values": "## 価値観\n\n{values}",
                    "goals": "## 目標\n\n{goals}"
                },
                "astro_components": []
            }
        }

        self.logger.debug("Content templates loaded", categories=list(self.templates.keys()))

    async def classify_content(self, text: str, context: Dict[str, Any] = None) -> Optional[ClassificationResult]:
        """
        Classify content using Claude API

        Args:
            text: Text content to classify
            context: Additional context information

        Returns:
            ClassificationResult or None if failed
        """
        if not self.client:
            self.logger.error("Claude client not initialized")
            return None

        with PerformanceTracker(self.logger, "content_classification") as tracker:
            try:
                # Build classification prompt
                system_prompt = self._build_classification_system_prompt()
                user_prompt = self._build_classification_user_prompt(text, context)

                # Call Claude API
                response = await self._call_claude_api(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_retries=self.config.max_retries
                )

                if not response:
                    return None

                # Parse classification result
                classification = self._parse_classification_response(response)
                if classification:
                    tracker.add_metric('category', classification.category)
                    tracker.add_metric('confidence', classification.confidence)

                    self.logger.info("Content classified",
                                   category=classification.category,
                                   title=classification.title[:50],
                                   confidence=f"{classification.confidence:.2f}",
                                   priority=classification.priority)

                return classification

            except Exception as e:
                self.logger.error("Content classification failed", error=e)
                return None

    def _build_classification_system_prompt(self) -> str:
        """Build system prompt for content classification"""
        return """あなたは日本語コンテンツの分類と構造化を行う専門AIです。

コンテンツを以下の4カテゴリーに分類してください：

1. **insight** - ビジネス洞察、学習内容、技術的発見、戦略的思考
   - 新しい知識や洞察を含む
   - ビジネス価値や実装可能性がある
   - 他者との共有価値がある

2. **diary** - 日記、個人的な振り返り、日常の記録
   - 個人的な体験や感情
   - 日常の出来事や活動
   - 時系列的な記録

3. **resume** - 経歴、スキル、実績、職業経験
   - 技術的スキルや資格
   - 職歴や学歴
   - 実績や成果物

4. **profile** - 個人情報、価値観、興味、目標
   - 個人的な背景や特性
   - 価値観や信念
   - 将来の目標や計画

優先度を以下から選択：
- **urgent**: 緊急性が高く即座の対応が必要
- **high**: 重要で近々対応すべき
- **medium**: 標準的な重要度
- **low**: 参考情報程度

JSON形式で回答してください：
```json
{
  "category": "カテゴリー名",
  "title": "適切なタイトル（50文字以内）",
  "summary": "内容の要約（200文字以内）",
  "priority": "優先度",
  "tags": ["関連するタグのリスト"],
  "confidence": 0.95,
  "reasoning": "分類の根拠説明"
}
```"""

    def _build_classification_user_prompt(self, text: str, context: Dict[str, Any] = None) -> str:
        """Build user prompt for content classification"""
        context_info = ""
        if context:
            context_items = []
            if 'source_file' in context:
                context_items.append(f"ソースファイル: {context['source_file']}")
            if 'source_type' in context:
                context_items.append(f"入力タイプ: {context['source_type']}")
            if 'confidence' in context:
                context_items.append(f"転写信頼度: {context['confidence']:.2f}")

            if context_items:
                context_info = f"\n\n## コンテキスト情報\n" + "\n".join(context_items)

        return f"""以下のコンテンツを分析して分類してください：

## 分析対象コンテンツ
{text[:4000]}{'...' if len(text) > 4000 else ''}{context_info}

上記のシステムプロンプトの指示に従って、適切なカテゴリー、タイトル、要約、優先度、タグを決定し、JSON形式で回答してください。"""

    async def _call_claude_api(self, system_prompt: str, user_prompt: str, max_retries: int = 3) -> Optional[str]:
        """Call Claude API with retry logic"""
        for attempt in range(max_retries):
            try:
                message = await asyncio.to_thread(
                    self.client.messages.create,
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )

                if message.content and len(message.content) > 0:
                    return message.content[0].text

                self.logger.warning("Empty response from Claude API")
                return None

            except Exception as e:
                self.logger.warning(f"Claude API call failed (attempt {attempt + 1}/{max_retries})", error=e)

                if attempt < max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                else:
                    self.logger.error("All Claude API retry attempts failed", error=e)

        return None

    def _parse_classification_response(self, response: str) -> Optional[ClassificationResult]:
        """Parse Claude's classification response"""
        try:
            # Extract JSON from response (handle cases where Claude adds explanation)
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without code blocks
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    self.logger.error("No JSON found in response", response=response[:200])
                    return None

            data = json.loads(json_str)

            # Validate required fields
            required_fields = ['category', 'title', 'summary', 'priority', 'tags', 'confidence']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.logger.error("Missing required fields in classification", fields=missing_fields)
                return None

            # Validate category
            valid_categories = ['insight', 'diary', 'resume', 'profile']
            if data['category'] not in valid_categories:
                self.logger.error("Invalid category", category=data['category'], valid=valid_categories)
                return None

            # Validate priority
            valid_priorities = ['urgent', 'high', 'medium', 'low']
            if data['priority'] not in valid_priorities:
                self.logger.warning("Invalid priority, defaulting to medium", priority=data['priority'])
                data['priority'] = 'medium'

            # Ensure tags is a list
            if not isinstance(data['tags'], list):
                data['tags'] = [str(data['tags'])]

            # Validate confidence
            confidence = float(data['confidence'])
            if not 0.0 <= confidence <= 1.0:
                self.logger.warning("Invalid confidence score, clamping to range", confidence=confidence)
                confidence = max(0.0, min(1.0, confidence))

            return ClassificationResult(
                category=data['category'],
                title=str(data['title'])[:100],  # Limit title length
                summary=str(data['summary'])[:500],  # Limit summary length
                priority=data['priority'],
                tags=data['tags'],
                confidence=confidence,
                metadata={
                    'reasoning': data.get('reasoning', ''),
                    'raw_response': response,
                    'timestamp': datetime.now().isoformat()
                }
            )

        except json.JSONDecodeError as e:
            self.logger.error("Failed to parse JSON response", error=e, response=response[:200])
            return None
        except Exception as e:
            self.logger.error("Failed to parse classification response", error=e)
            return None

    async def generate_structured_content(self, content_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate structured content for digital garden

        Args:
            content_data: Dictionary containing content and classification info

        Returns:
            Dictionary with structured content ready for digital garden
        """
        if not self.client:
            self.logger.error("Claude client not initialized")
            return None

        category = content_data.get('category')
        if not category or category not in self.templates:
            self.logger.error("Invalid or missing category", category=category)
            return None

        with PerformanceTracker(self.logger, "content_generation", category=category) as tracker:
            try:
                # Build content generation prompt
                system_prompt = self._build_generation_system_prompt(category)
                user_prompt = self._build_generation_user_prompt(content_data)

                # Call Claude API
                response = await self._call_claude_api(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_retries=self.config.max_retries
                )

                if not response:
                    return None

                # Parse generated content
                generated_content = self._parse_generation_response(response, category)
                if not generated_content:
                    return None

                # Create final structured content
                structured_content = self._create_structured_content(content_data, generated_content)

                tracker.add_metric('content_length', len(structured_content['content']))

                self.logger.info("Structured content generated",
                               category=category,
                               title=structured_content['frontmatter']['title'][:50],
                               content_length=len(structured_content['content']))

                return structured_content

            except Exception as e:
                self.logger.error("Content generation failed", error=e, category=category)
                return None

    def _build_generation_system_prompt(self, category: str) -> str:
        """Build system prompt for content generation"""
        template = self.templates[category]

        structure_desc = "\n".join([
            f"- {key}: {desc.split('\\n')[0]}"
            for key, desc in template['content_structure'].items()
        ])

        return f"""あなたは{category}カテゴリーのコンテンツを構造化して生成する専門AIです。

生成するコンテンツの構造：
{structure_desc}

以下のガイドラインに従ってください：

1. **正確性**: 元のコンテンツの情報を正確に反映する
2. **構造性**: 指定されたセクション構造に従う
3. **簡潔性**: 要点を明確に、冗長さを避ける
4. **実用性**: 読みやすく、アクションにつながる内容
5. **一貫性**: 全体を通じて一貫したトーンとスタイル

JSON形式で回答してください：
```json
{{
  "sections": {{
    "section_name": "そのセクションの内容"
  }},
  "metadata": {{
    "word_count": 推定文字数,
    "reading_time": "読了時間（分）",
    "key_points": ["主要ポイントのリスト"]
  }}
}}
```"""

    def _build_generation_user_prompt(self, content_data: Dict[str, Any]) -> str:
        """Build user prompt for content generation"""
        context_info = []

        # Add basic information
        if 'title' in content_data:
            context_info.append(f"タイトル: {content_data['title']}")
        if 'summary' in content_data:
            context_info.append(f"要約: {content_data['summary']}")
        if 'priority' in content_data:
            context_info.append(f"優先度: {content_data['priority']}")
        if 'tags' in content_data:
            context_info.append(f"タグ: {', '.join(content_data['tags'])}")

        # Add source information
        if 'source_file' in content_data:
            context_info.append(f"ソース: {content_data['source_file']}")
        if 'source_type' in content_data:
            context_info.append(f"入力形式: {content_data['source_type']}")

        # Add research information if available
        if 'research' in content_data:
            context_info.append("研究情報: あり")

        context_str = "\n".join(context_info) if context_info else ""

        return f"""以下のコンテンツを構造化して生成してください：

## 基本情報
{context_str}

## 元のコンテンツ
{content_data.get('text', '')[:3000]}{'...' if len(content_data.get('text', '')) > 3000 else ''}

{f"## 研究情報\\n{json.dumps(content_data['research'], indent=2, ensure_ascii=False)[:1000]}" if 'research' in content_data else ""}

上記の情報を基に、指定された構造に従ってコンテンツを生成し、JSON形式で回答してください。"""

    def _parse_generation_response(self, response: str, category: str) -> Optional[Dict[str, Any]]:
        """Parse Claude's content generation response"""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    self.logger.error("No JSON found in generation response")
                    return None

            data = json.loads(json_str)

            # Validate sections
            if 'sections' not in data:
                self.logger.error("No sections found in generation response")
                return None

            return data

        except json.JSONDecodeError as e:
            self.logger.error("Failed to parse generation JSON response", error=e)
            return None
        except Exception as e:
            self.logger.error("Failed to parse generation response", error=e)
            return None

    def _create_structured_content(self, content_data: Dict[str, Any], generated_content: Dict[str, Any]) -> Dict[str, Any]:
        """Create final structured content with frontmatter and body"""
        category = content_data['category']
        template = self.templates[category]

        # Prepare frontmatter data
        frontmatter_data = {
            'title': content_data.get('title', 'Untitled'),
            'summary': content_data.get('summary', ''),
            'date': datetime.now().isoformat(),
            'tags': json.dumps(content_data.get('tags', []), ensure_ascii=False),
            'priority': content_data.get('priority', 'medium'),
            'source_file': content_data.get('source_file', ''),
            'confidence': content_data.get('confidence', 1.0),
            'session_id': content_data.get('session_id', ''),
            'generated_at': datetime.now().isoformat(),
            'model': self.config.model
        }

        # Generate frontmatter
        frontmatter = template['frontmatter_template'].format(**frontmatter_data)

        # Generate content body
        content_sections = []
        sections_data = generated_content.get('sections', {})

        for section_key, section_template in template['content_structure'].items():
            if section_key in sections_data:
                section_content = section_template.format(
                    **{section_key: sections_data[section_key]}
                )
                content_sections.append(section_content)

        content_body = "\n\n".join(content_sections)

        # Add Astro components if needed
        if template['astro_components']:
            components_section = "\n\n## コンポーネント\n\n"
            for component in template['astro_components']:
                if component == 'ImpactAnalysis':
                    components_section += f"<ImpactAnalysis />\n\n"
                elif component == 'MermaidDiagram':
                    components_section += f"<MermaidDiagram />\n\n"
            content_body += components_section

        # Calculate file path
        safe_title = "".join(c for c in content_data.get('title', 'untitled') if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '-').lower()[:50]
        date_prefix = datetime.now().strftime('%Y-%m-%d')
        file_name = f"{date_prefix}-{safe_title}.md"

        return {
            'frontmatter': frontmatter_data,
            'content': f"{frontmatter}\n\n{content_body}",
            'category': category,
            'file_name': file_name,
            'file_path': f"digital-garden/src/content/{category}/{file_name}",
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'word_count': generated_content.get('metadata', {}).get('word_count', len(content_body.split())),
                'sections': list(sections_data.keys()),
                'astro_components': template['astro_components']
            }
        }

    def get_classifier_info(self) -> Dict[str, Any]:
        """Get information about the classifier"""
        return {
            "model": self.config.model,
            "available": self.client is not None,
            "anthropic_available": ANTHROPIC_AVAILABLE,
            "categories": list(self.templates.keys()),
            "templates_loaded": len(self.templates)
        }