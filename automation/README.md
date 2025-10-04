# 🤖 Digital Garden Automation System

Intelligent content processing pipeline that automatically transforms audio, video, and text inputs into structured digital garden content with AI-powered classification, research enhancement, and Git automation.

## 🌟 Features

### 🎙️ **Whisper Transcription**
- Japanese-optimized transcription using `kotoba-tech/kotoba-whisper-v2.0`
- Quality assessment and confidence scoring
- Support for multiple audio/video formats
- Batch processing with concurrency control

### 🧠 **Claude Classification**
- Intelligent content categorization (insight, diary, resume, profile)
- Automatic title and summary generation
- Priority assessment and tagging
- Structured content generation for Astro

### 🔍 **Perplexity Research**
- Fact-checking and verification
- Current information enhancement
- Credibility scoring of sources
- Context-aware research queries

### 📦 **Git Automation**
- Automatic branching and commits
- Pull request creation
- GitHub Pages deployment
- Intelligent commit messages

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+** with pip
2. **Git** installed and configured
3. **GitHub CLI** (optional, for PR creation)
4. **API Keys**:
   - Anthropic API key for Claude
   - Perplexity API key for research

### Installation

1. **Clone and setup**:
   ```bash
   git clone <your-repo>
   cd <your-repo>
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r automation/requirements.txt
   ```

3. **Configure API keys**:
   ```bash
   export ANTHROPIC_API_KEY="your-claude-api-key"
   export PERPLEXITY_API_KEY="your-perplexity-api-key"
   ```

4. **Test the system**:
   ```bash
   python automation/run_automation.py --test-components
   ```

### Basic Usage

1. **Add content to input directories**:
   - Audio files: `input/audio/`
   - Video files: `input/video/`
   - Text files: `input/text/`

2. **Run automation**:
   ```bash
   python automation/run_automation.py
   ```

3. **Check results** in your digital garden:
   - `digital-garden/src/content/insights/`
   - `digital-garden/src/content/diary/`
   - `digital-garden/src/content/resume/`
   - `digital-garden/src/content/profile/`

## 📁 Project Structure

```
automation/
├── digital_garden_processor.py     # Main orchestration system
├── run_automation.py               # CLI entry point
├── requirements.txt                # Python dependencies
├── config/
│   ├── settings.py                 # Configuration management
│   └── default.yaml                # Default configuration
├── components/
│   ├── transcription/
│   │   └── whisper_processor.py    # Whisper transcription
│   ├── classification/
│   │   └── claude_classifier.py    # Claude classification
│   ├── research/
│   │   └── perplexity_researcher.py # Perplexity research
│   └── deployment/
│       └── git_automation.py       # Git operations
├── utils/
│   ├── logging_setup.py            # Logging utilities
│   └── file_handler.py             # File operations
└── templates/                      # Content templates

input/
├── audio/                          # Audio files (.mp3, .wav, etc.)
├── video/                          # Video files (.mp4, .mov, etc.)
├── text/                           # Text files (.txt, .md, etc.)
└── processed/                      # Processed files archive
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required API Keys
export ANTHROPIC_API_KEY="your-claude-api-key"
export PERPLEXITY_API_KEY="your-perplexity-api-key"

# Optional Overrides
export WHISPER_MODEL="kotoba-tech/kotoba-whisper-v2.0"
export WHISPER_DEVICE="auto"  # auto, cpu, cuda, mps
export MAX_CONCURRENT_TRANSCRIPTIONS="2"
export GIT_AUTO_PUSH="true"
export GIT_CREATE_PR="true"
```

### Custom Configuration

Create `automation/config/custom.yaml`:

```yaml
# Custom configuration example
transcription:
  model_name: "kotoba-tech/kotoba-whisper-v2.0"
  device: "cuda"  # Use GPU if available
  min_confidence: 0.8

classification:
  model: "claude-3-5-sonnet-20241022"
  temperature: 0.5

performance:
  max_concurrent_transcriptions: 1  # Reduce for limited resources
  memory_limit_mb: 4096

git:
  auto_push: false  # Manual push
  create_pr: false  # Manual PR creation
```

Run with custom config:
```bash
python automation/run_automation.py --config automation/config/custom.yaml
```

## 🔧 Command Line Interface

### Basic Commands

```bash
# Run full automation pipeline
python automation/run_automation.py

# Dry run (no changes made)
python automation/run_automation.py --dry-run

# Verbose logging
python automation/run_automation.py --verbose

# Show system status
python automation/run_automation.py --status

# Test all components
python automation/run_automation.py --test-components

# Clean up old files and cache
python automation/run_automation.py --cleanup

# Use custom configuration
python automation/run_automation.py --config custom.yaml
```

### Status Check Example

```bash
$ python automation/run_automation.py --status

🤖 Digital Garden Automation System Status
==================================================
🎙️  Whisper Transcription: ✅ Available
    Model: kotoba-tech/kotoba-whisper-v2.0
    Device: cuda
🧠 Claude Classification: ✅ Available
    Model: claude-3-5-sonnet-20241022
    Categories: insight, diary, resume, profile
🔍 Perplexity Research: ✅ Available
    Model: llama-3.1-sonar-small-128k-online
    Cache entries: 5
📦 Git Automation: ✅ Available
    Repository: /path/to/your/repo
    Current branch: main
    Auto-push: ✅
    Create PR: ✅
```

## 🎯 Content Processing Flow

1. **Input Discovery**: Scans input directories for new files
2. **Transcription**: Converts audio/video to text using Whisper
3. **Classification**: Categorizes content using Claude API
4. **Research**: Enhances insights with Perplexity research
5. **Generation**: Creates structured Markdown for digital garden
6. **Deployment**: Commits to Git and creates pull requests
7. **Cleanup**: Archives processed files

## 📊 Supported Content Types

### Input Formats

- **Audio**: MP3, WAV, FLAC, M4A, OGG
- **Video**: MP4, AVI, MOV, MKV, WEBM
- **Text**: TXT, MD, RTF

### Output Categories

- **Insights** (`insights/`): Business insights, technical learnings
- **Diary** (`diary/`): Personal reflections, daily notes
- **Resume** (`resume/`): Skills, experience, achievements
- **Profile** (`profile/`): Personal information, goals, values

## 🛠️ Development

### Adding Custom Components

1. **Create component class**:
   ```python
   # automation/components/custom/my_processor.py
   class MyProcessor:
       def __init__(self, config):
           self.config = config

       async def process(self, content):
           # Your processing logic
           return processed_content
   ```

2. **Update main processor**:
   ```python
   # In digital_garden_processor.py
   from automation.components.custom.my_processor import MyProcessor

   self.my_processor = MyProcessor(config)
   ```

### Testing

```bash
# Run tests
pytest automation/

# Run with coverage
pytest automation/ --cov=automation

# Test specific component
pytest automation/components/transcription/
```

### Code Quality

```bash
# Format code
black automation/
isort automation/

# Type checking
mypy automation/

# Linting
flake8 automation/
```

## 🔒 Security

- API keys stored in environment variables
- Content sanitization and PII removal options
- File type validation and size limits
- Git operations with backup creation

## 📈 Performance

### Optimization Tips

1. **GPU Acceleration**: Use CUDA for Whisper transcription
2. **Concurrency**: Adjust concurrent processing limits
3. **Caching**: Research results cached for 24 hours
4. **File Size**: Limit input files to 500MB per file

### Memory Management

- Automatic memory cleanup after processing
- Configurable memory limits
- Batch processing for large files

## 🐛 Troubleshooting

### Common Issues

1. **"Transformers not available"**
   ```bash
   pip install torch transformers accelerate
   ```

2. **"Claude API key missing"**
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

3. **"Git not found"**
   - Install Git and ensure it's in PATH
   - Configure user.name and user.email

4. **"CUDA out of memory"**
   ```yaml
   # In config
   transcription:
     device: "cpu"  # Use CPU instead
   ```

### Debug Mode

```bash
python automation/run_automation.py --verbose --dry-run
```

### Log Files

Check logs at: `logs/automation.log`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is part of a personal digital garden system. See the main repository for license information.

## 🙏 Acknowledgments

- [Kotoba-tech](https://huggingface.co/kotoba-tech) for Japanese-optimized Whisper
- [Anthropic](https://anthropic.com) for Claude API
- [Perplexity](https://perplexity.ai) for research capabilities
- [Astro](https://astro.build) for the digital garden framework