"""
Automation Configuration Management
Centralized configuration for the Digital Garden automation system

Author: Claude Code Assistant
Date: 2025-10-04
Version: 2.0
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

@dataclass
class PathsConfig:
    """File paths configuration"""
    input_audio: str = "input/audio"
    input_video: str = "input/video"
    input_text: str = "input/text"
    input_processed: str = "input/processed"
    digital_garden: str = "digital-garden"
    templates: str = "automation/templates"
    logs: str = "logs"

@dataclass
class TranscriptionConfig:
    """Whisper transcription configuration"""
    model_name: str = "kotoba-tech/kotoba-whisper-v2.0"
    device: str = "auto"  # "auto", "cpu", "cuda"
    compute_type: str = "float16"
    supported_formats: List[str] = field(default_factory=lambda: ["mp3", "wav", "flac", "m4a", "ogg"])
    min_confidence: float = 0.7
    language: str = "ja"  # Japanese by default
    task: str = "transcribe"  # "transcribe" or "translate"
    chunk_duration: int = 30  # seconds
    max_file_size_mb: int = 500
    output_format: str = "segments"  # "text", "segments", "word_timestamps"

@dataclass
class ClaudeConfig:
    """Claude API configuration"""
    api_key: Optional[str] = None
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0

@dataclass
class PerplexityConfig:
    """Perplexity API configuration"""
    api_key: Optional[str] = None
    model: str = "llama-3.1-sonar-small-128k-online"
    max_tokens: int = 2000
    temperature: float = 0.2
    timeout: int = 45
    max_retries: int = 3
    retry_delay: float = 1.0
    search_recency_filter: str = "month"  # "hour", "day", "week", "month", "year"

@dataclass
class GitConfig:
    """Git automation configuration"""
    repository_path: str = "."
    main_branch: str = "main"
    feature_branch_prefix: str = "automation/"
    commit_message_template: str = "🤖 Automated content: {category} - {title}\n\nGenerated from: {source_file}\nSession: {session_id}\n\n🤖 Generated with Claude Code Automation"
    auto_push: bool = True
    create_pr: bool = True
    pr_template: str = "## Automated Content Update\n\n**Category**: {category}\n**Source**: {source_file}\n**Processing Time**: {processing_time}s\n\nThis PR contains automatically processed content from the digital garden automation system.\n\n### Changes\n{changes_summary}\n\n🤖 Generated with Claude Code Automation"
    enable_gh_pages: bool = True

@dataclass
class PerformanceConfig:
    """Performance and concurrency configuration"""
    max_concurrent_transcriptions: int = 2
    max_concurrent_classifications: int = 5
    max_concurrent_research: int = 3
    memory_limit_mb: int = 2048
    disk_cleanup_threshold_gb: int = 10
    cache_ttl_hours: int = 24

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    file_enabled: bool = True
    console_enabled: bool = True
    file_path: str = "logs/automation.log"
    max_file_size_mb: int = 50
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

@dataclass
class QualityConfig:
    """Content quality configuration"""
    min_text_length: int = 50
    max_text_length: int = 50000
    min_transcription_confidence: float = 0.7
    min_classification_confidence: float = 0.8
    required_metadata_fields: List[str] = field(default_factory=lambda: ["category", "title", "priority"])
    content_validation: bool = True

@dataclass
class SecurityConfig:
    """Security configuration"""
    sanitize_content: bool = True
    remove_pii: bool = True
    allowed_file_types: List[str] = field(default_factory=lambda: [
        "mp3", "wav", "flac", "m4a", "ogg",  # Audio
        "mp4", "avi", "mov", "mkv", "webm",  # Video
        "txt", "md", "rtf"  # Text
    ])
    max_file_size_mb: int = 500
    virus_scan: bool = False  # Optional virus scanning

@dataclass
class AutomationConfig:
    """Main automation configuration class"""
    paths: PathsConfig = field(default_factory=PathsConfig)
    transcription: TranscriptionConfig = field(default_factory=TranscriptionConfig)
    classification: ClaudeConfig = field(default_factory=ClaudeConfig)
    research: PerplexityConfig = field(default_factory=PerplexityConfig)
    git: GitConfig = field(default_factory=GitConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    file_handling: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'AutomationConfig':
        """
        Load configuration from file or environment variables

        Args:
            config_path: Path to YAML configuration file

        Returns:
            AutomationConfig instance
        """
        config = cls()

        # Load from YAML file if provided
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
                config = cls._merge_config(config, yaml_config)

        # Override with environment variables
        config = cls._load_env_overrides(config)

        # Validate configuration
        config._validate()

        return config

    @classmethod
    def _merge_config(cls, base_config: 'AutomationConfig', yaml_config: Dict[str, Any]) -> 'AutomationConfig':
        """Merge YAML configuration with base configuration"""
        def merge_dataclass(base_obj, yaml_obj, dataclass_type):
            if not isinstance(yaml_obj, dict):
                return base_obj

            kwargs = {}
            for field_name, field_def in dataclass_type.__dataclass_fields__.items():
                if field_name in yaml_obj:
                    field_value = yaml_obj[field_name]
                    # Handle nested dataclasses
                    if hasattr(field_def.type, '__dataclass_fields__'):
                        current_value = getattr(base_obj, field_name)
                        kwargs[field_name] = merge_dataclass(current_value, field_value, field_def.type)
                    else:
                        kwargs[field_name] = field_value
                else:
                    kwargs[field_name] = getattr(base_obj, field_name)

            return dataclass_type(**kwargs)

        return merge_dataclass(base_config, yaml_config, cls)

    @classmethod
    def _load_env_overrides(cls, config: 'AutomationConfig') -> 'AutomationConfig':
        """Load configuration overrides from environment variables"""

        # API Keys
        if os.getenv('ANTHROPIC_API_KEY'):
            config.classification.api_key = os.getenv('ANTHROPIC_API_KEY')
        if os.getenv('CLAUDE_API_KEY'):
            config.classification.api_key = os.getenv('CLAUDE_API_KEY')
        if os.getenv('PERPLEXITY_API_KEY'):
            config.research.api_key = os.getenv('PERPLEXITY_API_KEY')

        # Performance overrides
        if os.getenv('MAX_CONCURRENT_TRANSCRIPTIONS'):
            config.performance.max_concurrent_transcriptions = int(os.getenv('MAX_CONCURRENT_TRANSCRIPTIONS'))
        if os.getenv('MEMORY_LIMIT_MB'):
            config.performance.memory_limit_mb = int(os.getenv('MEMORY_LIMIT_MB'))

        # Path overrides
        if os.getenv('DIGITAL_GARDEN_PATH'):
            config.paths.digital_garden = os.getenv('DIGITAL_GARDEN_PATH')
        if os.getenv('INPUT_PATH'):
            base_path = os.getenv('INPUT_PATH')
            config.paths.input_audio = f"{base_path}/audio"
            config.paths.input_video = f"{base_path}/video"
            config.paths.input_text = f"{base_path}/text"
            config.paths.input_processed = f"{base_path}/processed"

        # Transcription overrides
        if os.getenv('WHISPER_MODEL'):
            config.transcription.model_name = os.getenv('WHISPER_MODEL')
        if os.getenv('WHISPER_DEVICE'):
            config.transcription.device = os.getenv('WHISPER_DEVICE')

        # Git overrides
        if os.getenv('GIT_AUTO_PUSH'):
            config.git.auto_push = os.getenv('GIT_AUTO_PUSH').lower() == 'true'
        if os.getenv('GIT_CREATE_PR'):
            config.git.create_pr = os.getenv('GIT_CREATE_PR').lower() == 'true'

        return config

    def _validate(self) -> None:
        """Validate configuration settings"""
        errors = []

        # Validate API keys
        if not self.classification.api_key:
            errors.append("Claude API key is required (set ANTHROPIC_API_KEY or CLAUDE_API_KEY)")

        if not self.research.api_key:
            errors.append("Perplexity API key is required (set PERPLEXITY_API_KEY)")

        # Validate paths
        required_paths = [
            self.paths.input_audio,
            self.paths.input_video,
            self.paths.input_text,
            self.paths.digital_garden
        ]

        for path in required_paths:
            if not Path(path).parent.exists():
                errors.append(f"Parent directory does not exist: {path}")

        # Validate performance settings
        if self.performance.max_concurrent_transcriptions < 1:
            errors.append("max_concurrent_transcriptions must be >= 1")

        if self.performance.memory_limit_mb < 512:
            errors.append("memory_limit_mb must be >= 512")

        # Validate quality settings
        if not (0.0 <= self.transcription.min_confidence <= 1.0):
            errors.append("min_confidence must be between 0.0 and 1.0")

        if self.quality.min_text_length > self.quality.max_text_length:
            errors.append("min_text_length cannot be greater than max_text_length")

        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors))

    def save(self, config_path: str) -> None:
        """Save current configuration to YAML file"""
        def dataclass_to_dict(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {k: dataclass_to_dict(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [dataclass_to_dict(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: dataclass_to_dict(v) for k, v in obj.items()}
            else:
                return obj

        config_dict = dataclass_to_dict(self)

        # Remove sensitive information
        if 'classification' in config_dict and 'api_key' in config_dict['classification']:
            config_dict['classification']['api_key'] = "***MASKED***"
        if 'research' in config_dict and 'api_key' in config_dict['research']:
            config_dict['research']['api_key'] = "***MASKED***"

        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True, indent=2)

    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary for logging"""
        return {
            'transcription_model': self.transcription.model_name,
            'classification_model': self.classification.model,
            'research_model': self.research.model,
            'max_concurrent_transcriptions': self.performance.max_concurrent_transcriptions,
            'max_concurrent_classifications': self.performance.max_concurrent_classifications,
            'auto_push': self.git.auto_push,
            'create_pr': self.git.create_pr,
            'min_confidence': self.transcription.min_confidence,
            'content_validation': self.quality.content_validation
        }