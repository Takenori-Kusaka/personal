# Usage Guide - Personal Digital Garden & Resume System

This guide covers both systems in this repository: the **Resume Management System** and the **Digital Garden Automation System**.

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+** with pip installed
2. **Git** configured with your credentials
3. **API Keys** (for Digital Garden Automation):
   - `ANTHROPIC_API_KEY` - For Claude AI classification
   - `PERPLEXITY_API_KEY` - For research and fact-checking

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd <your-repo-name>

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
# For both systems:
pip install -r requirements-full.txt

# OR install individually:
pip install -r requirements.txt              # Resume System only
pip install -r automation/requirements.txt   # Digital Garden only
```

## 📄 Resume Management System

Generate professional resumes from YAML data.

### Usage

1. **Edit your profile data**:
   ```bash
   # Edit the main profile file
   nano data/profile.yml
   ```

2. **Generate resume**:
   ```bash
   # Run the resume generation
   python src/main.py
   ```

3. **Check output**:
   - Markdown: `output/resume.md`
   - HTML: `output/resume.html`

### Customization

- **Template**: Edit `templates/resume_template.md`
- **Styling**: Modify `templates/styles/web_style.css`
- **Data Structure**: See `data/schema.yml` for reference

## 🤖 Digital Garden Automation System

Transform audio, video, and text into structured digital garden content using AI.

### Setup

1. **Configure API keys**:
   ```bash
   export ANTHROPIC_API_KEY="your-claude-api-key"
   export PERPLEXITY_API_KEY="your-perplexity-api-key"
   ```

2. **Test the system**:
   ```bash
   python automation/run_automation.py --test-components
   ```

### Basic Usage

1. **Add content to input directories**:
   ```bash
   # Audio files (.mp3, .wav, .flac, etc.)
   cp my_recording.mp3 input/audio/

   # Video files (.mp4, .mov, .mkv, etc.)
   cp my_video.mp4 input/video/

   # Text files (.txt, .md, .rtf)
   cp my_notes.txt input/text/
   ```

2. **Run automation**:
   ```bash
   # Process all input files
   python automation/run_automation.py

   # Or with verbose output
   python automation/run_automation.py --verbose
   ```

3. **Check results**:
   - Generated content: `digital-garden/src/content/`
   - Categories: `insights/`, `diary/`, `resume/`, `profile/`
   - Processing logs: `logs/automation.log`

### Advanced Usage

#### Custom Configuration

```bash
# Create custom config
cp automation/config/default.yaml automation/config/custom.yaml
nano automation/config/custom.yaml

# Run with custom config
python automation/run_automation.py --config automation/config/custom.yaml
```

#### Dry Run Mode

```bash
# Preview what would be processed without making changes
python automation/run_automation.py --dry-run --verbose
```

#### Status and Monitoring

```bash
# Check system status
python automation/run_automation.py --status

# Clean up old files and cache
python automation/run_automation.py --cleanup
```

## 🔧 Configuration

### Resume System Configuration

Edit `data/profile.yml` with your information:

```yaml
profile:
  personal:
    name: "Your Name"
    age: 30
    location: "Tokyo, Japan"
    email: "your@email.com"

  career:
    companies:
      - name: "Company Name"
        position: "Your Position"
        duration: "2020-2025"
        projects:
          - name: "Project Name"
            description: "What you accomplished"
```

### Digital Garden Configuration

Main settings in `automation/config/default.yaml`:

```yaml
# Transcription settings
transcription:
  model_name: "kotoba-tech/kotoba-whisper-v2.0"
  device: "auto"  # auto, cpu, cuda
  min_confidence: 0.7

# AI processing
classification:
  model: "claude-3-5-sonnet-20241022"
  temperature: 0.7

# Git automation
git:
  auto_push: true
  create_pr: true
```

### Environment Variables

```bash
# Required for Digital Garden Automation
export ANTHROPIC_API_KEY="your_claude_api_key"
export PERPLEXITY_API_KEY="your_perplexity_api_key"

# Optional optimizations
export WHISPER_DEVICE="cuda"  # Use GPU if available
export MAX_CONCURRENT_TRANSCRIPTIONS="2"
export GIT_AUTO_PUSH="true"
```

## 🎯 Content Categories

The Digital Garden Automation System automatically categorizes content:

- **📝 Insights** (`insights/`): Business insights, technical learnings, strategic thinking
- **📖 Diary** (`diary/`): Personal reflections, daily notes, experiences
- **💼 Resume** (`resume/`): Skills, experience, achievements, career history
- **👤 Profile** (`profile/`): Personal information, goals, values, interests

## 📊 Workflow Examples

### Daily Content Processing

```bash
# Morning routine: check what needs processing
python automation/run_automation.py --status

# Add yesterday's voice notes
cp voice_notes/*.m4a input/audio/

# Process and publish
python automation/run_automation.py

# Review results
git log --oneline -5
```

### Weekly Resume Update

```bash
# Update career information
nano data/profile.yml

# Generate updated resume
python src/main.py

# Review output
open output/resume.html
```

### Research and Insight Development

```bash
# Add research audio/text
cp research_material/* input/text/
cp interview_recording.mp3 input/audio/

# Process with research enhancement
python automation/run_automation.py --verbose

# Check generated insights
ls digital-garden/src/content/insights/
```

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'torch'"**
   ```bash
   pip install torch torchaudio transformers
   ```

2. **"API key not found"**
   ```bash
   echo $ANTHROPIC_API_KEY  # Check if set
   export ANTHROPIC_API_KEY="your-key-here"
   ```

3. **"Git not found"**
   - Install Git and ensure it's in your PATH
   - Configure: `git config --global user.name "Your Name"`

4. **"Permission denied"**
   ```bash
   chmod +x automation/run_automation.py
   ```

### Debug Mode

```bash
# Run with maximum verbosity
python automation/run_automation.py --verbose --dry-run

# Check logs
tail -f logs/automation.log
```

### Performance Issues

```bash
# Use CPU instead of GPU if memory issues
export WHISPER_DEVICE="cpu"

# Reduce concurrent operations
export MAX_CONCURRENT_TRANSCRIPTIONS="1"
```

## 📚 Additional Resources

- **Digital Garden Automation**: See `automation/README.md`
- **Resume System**: Check `templates/` for customization examples
- **Configuration**: Review `automation/config/default.yaml` for all options
- **API Documentation**:
  - [Anthropic Claude API](https://docs.anthropic.com/)
  - [Perplexity API](https://docs.perplexity.ai/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

## 📄 License

See the main repository for license information.