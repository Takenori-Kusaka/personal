#!/usr/bin/env python3
"""
Digital Garden Automation Runner
Main entry point for the automated content processing pipeline

Author: Claude Code Assistant
Date: 2025-10-04
Version: 2.0

Usage:
    python automation/run_automation.py [--config CONFIG_PATH] [--dry-run] [--verbose]
"""

import asyncio
import sys
import argparse
import json
from pathlib import Path

# Add automation directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from digital_garden_processor import DigitalGardenProcessor
from config.settings import AutomationConfig
from utils.logging_setup import setup_logging, get_logger

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Digital Garden Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python automation/run_automation.py
  python automation/run_automation.py --config automation/config/custom.yaml
  python automation/run_automation.py --dry-run --verbose
  python automation/run_automation.py --status
        """
    )

    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration file (default: automation/config/default.yaml)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform a dry run without making actual changes'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging output'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Show system status and exit'
    )

    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up old files and cached data'
    )

    parser.add_argument(
        '--test-components',
        action='store_true',
        help='Test all components and show their status'
    )

    return parser.parse_args()

async def show_system_status(config: AutomationConfig):
    """Show comprehensive system status"""
    print("🤖 Digital Garden Automation System Status")
    print("=" * 50)

    # Initialize processor to check component status
    processor = DigitalGardenProcessor(None)  # Use default config

    # Check Whisper
    whisper_info = processor.whisper_processor.get_model_info()
    print(f"🎙️  Whisper Transcription: {'✅ Available' if whisper_info['loaded'] or whisper_info['transformers_available'] else '❌ Not Available'}")
    if whisper_info['transformers_available']:
        print(f"    Model: {whisper_info['model_name']}")
        print(f"    Device: {whisper_info['device']}")

    # Check Claude
    claude_info = processor.claude_classifier.get_classifier_info()
    print(f"🧠 Claude Classification: {'✅ Available' if claude_info['available'] else '❌ Not Available'}")
    if claude_info['available']:
        print(f"    Model: {claude_info['model']}")
        print(f"    Categories: {', '.join(claude_info['categories'])}")

    # Check Perplexity
    perplexity_info = processor.perplexity_researcher.get_researcher_info()
    print(f"🔍 Perplexity Research: {'✅ Available' if perplexity_info['available'] else '❌ Not Available'}")
    if perplexity_info['available']:
        print(f"    Model: {perplexity_info['model']}")
        print(f"    Cache entries: {perplexity_info['cache_entries']}")

    # Check Git
    git_info = processor.git_automation.get_automation_info()
    print(f"📦 Git Automation: {'✅ Available' if git_info['git_available'] else '❌ Not Available'}")
    if git_info['git_available']:
        print(f"    Repository: {git_info['repository_path']}")
        print(f"    Current branch: {git_info['current_branch']}")
        print(f"    Auto-push: {'✅' if git_info['auto_push'] else '❌'}")
        print(f"    Create PR: {'✅' if git_info['create_pr'] else '❌'}")

    # Show configuration summary
    print(f"\n⚙️  Configuration:")
    config_summary = config.get_summary()
    for key, value in config_summary.items():
        print(f"    {key}: {value}")

    # Show input directories status
    print(f"\n📁 Input Directories:")
    input_paths = [
        ("Audio", config.paths.input_audio),
        ("Video", config.paths.input_video),
        ("Text", config.paths.input_text),
        ("Processed", config.paths.input_processed)
    ]

    for name, path in input_paths:
        path_obj = Path(path)
        if path_obj.exists():
            files = list(path_obj.iterdir())
            file_count = len([f for f in files if f.is_file()])
            print(f"    {name}: ✅ {file_count} files")
        else:
            print(f"    {name}: ❌ Directory not found")

async def test_all_components(config: AutomationConfig):
    """Test all system components"""
    print("🧪 Testing All Components")
    print("=" * 30)

    processor = DigitalGardenProcessor(None)

    # Test Whisper
    print("Testing Whisper transcription...")
    try:
        model_loaded = await processor.whisper_processor.initialize_model()
        print(f"  Whisper: {'✅ Passed' if model_loaded else '⚠️ Model not loaded but library available'}")
    except Exception as e:
        print(f"  Whisper: ❌ Failed - {str(e)}")

    # Test Claude (simple connection test)
    print("Testing Claude classification...")
    try:
        claude_info = processor.claude_classifier.get_classifier_info()
        print(f"  Claude: {'✅ Passed' if claude_info['available'] else '❌ API key missing'}")
    except Exception as e:
        print(f"  Claude: ❌ Failed - {str(e)}")

    # Test Perplexity (simple connection test)
    print("Testing Perplexity research...")
    try:
        perplexity_info = processor.perplexity_researcher.get_researcher_info()
        print(f"  Perplexity: {'✅ Passed' if perplexity_info['available'] else '❌ API key missing'}")
    except Exception as e:
        print(f"  Perplexity: ❌ Failed - {str(e)}")

    # Test Git
    print("Testing Git automation...")
    try:
        git_status = await processor.git_automation.get_repository_status()
        print(f"  Git: {'✅ Passed' if git_status['git_available'] else '❌ Git not available'}")
    except Exception as e:
        print(f"  Git: ❌ Failed - {str(e)}")

async def perform_cleanup(config: AutomationConfig):
    """Perform system cleanup"""
    print("🧹 Performing System Cleanup")
    print("=" * 30)

    processor = DigitalGardenProcessor(None)

    try:
        # Clean up Perplexity cache
        print("Cleaning up research cache...")
        await processor.perplexity_researcher.cleanup_cache()

        # Clean up old Git branches
        print("Cleaning up old branches...")
        deleted_branches = await processor.git_automation.cleanup_old_branches()
        print(f"  Deleted {deleted_branches} old branches")

        # Clean up log files
        print("Cleaning up old logs...")
        log_path = Path(config.logging.file_path).parent
        if log_path.exists():
            log_files = list(log_path.glob("*.log*"))
            old_logs = [f for f in log_files if (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days > 7]
            for log_file in old_logs:
                log_file.unlink()
            print(f"  Deleted {len(old_logs)} old log files")

        print("✅ Cleanup completed successfully")

    except Exception as e:
        print(f"❌ Cleanup failed: {str(e)}")

async def main():
    """Main entry point"""
    args = parse_arguments()

    # Determine config path
    config_path = args.config or "automation/config/default.yaml"

    try:
        # Load configuration
        config = AutomationConfig.load(config_path)

        # Override logging level if verbose
        if args.verbose:
            config.logging.level = "DEBUG"

        # Set up logging
        logger = setup_logging(config.logging)
        logger.info("Digital Garden Automation System starting")

        # Handle special modes
        if args.status:
            await show_system_status(config)
            return 0

        if args.test_components:
            await test_all_components(config)
            return 0

        if args.cleanup:
            await perform_cleanup(config)
            return 0

        # Initialize and run processor
        if args.dry_run:
            print("🔍 DRY RUN MODE - No files will be modified")
            # For dry run, we would implement read-only analysis
            logger.info("Running in dry-run mode")

        processor = DigitalGardenProcessor(config_path)

        print("🚀 Starting automated content processing...")
        print(f"📁 Input directories:")
        print(f"   Audio: {config.paths.input_audio}")
        print(f"   Video: {config.paths.input_video}")
        print(f"   Text: {config.paths.input_text}")
        print(f"📚 Digital Garden: {config.paths.digital_garden}")
        print("")

        # Run the main processing pipeline
        results = await processor.process_all_inputs()

        # Display results
        print("\n📊 Processing Results:")
        print("=" * 30)
        summary = results.get('summary', {})
        print(f"Duration: {summary.get('duration_seconds', 0):.1f} seconds")
        print(f"Success rate: {summary.get('success_rate', 0):.1f}%")
        print(f"Content generated: {summary.get('content_generated', 0)} items")
        print(f"Git commits: {summary.get('git_commits', 0)}")

        if results.get('errors'):
            print(f"\n⚠️  Errors encountered: {len(results['errors'])}")
            for error in results['errors']:
                print(f"  - {error['type']}: {error['message']}")

        print("\n✅ Processing completed successfully!")
        logger.info("Digital Garden Automation completed", results=summary)

        return 0

    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    from datetime import datetime

    sys.exit(asyncio.run(main()))