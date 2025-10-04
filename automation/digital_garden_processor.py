"""
Digital Garden Automation Processor
Main orchestration system for automated content processing pipeline

Author: Claude Code Assistant
Date: 2025-10-04
Version: 2.0
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml
import json

from automation.components.transcription.whisper_processor import WhisperProcessor
from automation.components.classification.claude_classifier import ClaudeClassifier
from automation.components.research.perplexity_researcher import PerplexityResearcher
from automation.components.deployment.git_automation import GitAutomation
from automation.config.settings import AutomationConfig
from automation.utils.logging_setup import setup_logging
from automation.utils.file_handler import FileHandler

class DigitalGardenProcessor:
    """
    Main processor class that orchestrates the entire automation pipeline:
    Input → Transcription → Classification → Research → Git Automation → Deployment
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the processor with configuration"""
        self.config = AutomationConfig.load(config_path)
        self.logger = setup_logging(self.config.logging)

        # Initialize components
        self.whisper_processor = WhisperProcessor(self.config.transcription)
        self.claude_classifier = ClaudeClassifier(self.config.classification)
        self.perplexity_researcher = PerplexityResearcher(self.config.research)
        self.git_automation = GitAutomation(self.config.git)
        self.file_handler = FileHandler(self.config.file_handling)

        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.processing_stats = {
            'start_time': None,
            'end_time': None,
            'files_processed': 0,
            'files_successful': 0,
            'files_failed': 0,
            'content_generated': 0,
            'git_commits': 0,
            'errors': []
        }

        self.logger.info(f"DigitalGardenProcessor initialized - Session: {self.session_id}")

    async def process_all_inputs(self) -> Dict[str, Any]:
        """
        Process all input files through the complete automation pipeline

        Returns:
            Dict containing processing results and statistics
        """
        self.processing_stats['start_time'] = datetime.now()
        self.logger.info("Starting automated content processing pipeline")

        try:
            # Step 1: Discover input files
            input_files = await self._discover_input_files()
            self.logger.info(f"Discovered {len(input_files)} input files")

            if not input_files:
                self.logger.warning("No input files found for processing")
                return self._generate_results_summary()

            # Step 2: Process files by type
            processed_content = {}

            # Process audio/video files (transcription required)
            audio_video_files = [f for f in input_files if f['type'] in ['audio', 'video']]
            if audio_video_files:
                transcribed_content = await self._process_transcription_batch(audio_video_files)
                processed_content.update(transcribed_content)

            # Process text files (direct processing)
            text_files = [f for f in input_files if f['type'] == 'text']
            if text_files:
                text_content = await self._process_text_batch(text_files)
                processed_content.update(text_content)

            # Step 3: Classify and route content
            classified_content = await self._classify_content_batch(processed_content)

            # Step 4: Enhance with research
            enhanced_content = await self._enhance_with_research(classified_content)

            # Step 5: Generate digital garden content
            garden_content = await self._generate_garden_content(enhanced_content)

            # Step 6: Git automation and deployment
            deployment_results = await self._deploy_content(garden_content)

            # Step 7: Cleanup and archiving
            await self._cleanup_processed_files(input_files)

            self.processing_stats['end_time'] = datetime.now()
            results = self._generate_results_summary()

            self.logger.info(f"Processing completed - Session: {self.session_id}")
            self.logger.info(f"Results: {results['summary']}")

            return results

        except Exception as e:
            self.processing_stats['errors'].append({
                'type': 'pipeline_error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            })
            self.logger.error(f"Pipeline processing failed: {e}", exc_info=True)
            raise

    async def _discover_input_files(self) -> List[Dict[str, Any]]:
        """Discover all processable files in input directories"""
        input_files = []

        # Audio files
        audio_dir = Path(self.config.paths.input_audio)
        if audio_dir.exists():
            for ext in self.config.transcription.supported_formats:
                for file_path in audio_dir.glob(f"*.{ext}"):
                    input_files.append({
                        'path': file_path,
                        'type': 'audio',
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                    })

        # Video files
        video_dir = Path(self.config.paths.input_video)
        if video_dir.exists():
            video_exts = ['mp4', 'avi', 'mov', 'mkv', 'webm']
            for ext in video_exts:
                for file_path in video_dir.glob(f"*.{ext}"):
                    input_files.append({
                        'path': file_path,
                        'type': 'video',
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                    })

        # Text files
        text_dir = Path(self.config.paths.input_text)
        if text_dir.exists():
            text_exts = ['txt', 'md', 'rtf']
            for ext in text_exts:
                for file_path in text_dir.glob(f"*.{ext}"):
                    input_files.append({
                        'path': file_path,
                        'type': 'text',
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                    })

        return input_files

    async def _process_transcription_batch(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process audio/video files through Whisper transcription"""
        self.logger.info(f"Processing {len(files)} audio/video files for transcription")
        transcribed_content = {}

        # Process files concurrently with limited concurrency
        semaphore = asyncio.Semaphore(self.config.performance.max_concurrent_transcriptions)

        async def process_single_file(file_info: Dict[str, Any]) -> Optional[Tuple[str, Dict[str, Any]]]:
            async with semaphore:
                try:
                    result = await self.whisper_processor.transcribe_file(file_info['path'])
                    if result and result.confidence >= self.config.transcription.min_confidence:
                        self.processing_stats['files_successful'] += 1
                        return str(file_info['path']), {
                            'text': result.text,
                            'confidence': result.confidence,
                            'metadata': result.audio_metadata,
                            'segments': result.segments,
                            'source_type': file_info['type'],
                            'source_file': str(file_info['path']),
                            'processing_time': result.processing_time
                        }
                    else:
                        self.logger.warning(f"Transcription failed or low confidence: {file_info['path']}")
                        self.processing_stats['files_failed'] += 1
                        return None

                except Exception as e:
                    self.logger.error(f"Error transcribing {file_info['path']}: {e}")
                    self.processing_stats['files_failed'] += 1
                    self.processing_stats['errors'].append({
                        'type': 'transcription_error',
                        'file': str(file_info['path']),
                        'message': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
                    return None

        # Execute transcription tasks
        tasks = [process_single_file(file_info) for file_info in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect successful results
        for result in results:
            if result and not isinstance(result, Exception):
                file_path, content = result
                transcribed_content[file_path] = content

        self.processing_stats['files_processed'] += len(files)
        self.logger.info(f"Transcription completed: {len(transcribed_content)} successful")

        return transcribed_content

    async def _process_text_batch(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process text files directly"""
        self.logger.info(f"Processing {len(files)} text files")
        text_content = {}

        for file_info in files:
            try:
                with open(file_info['path'], 'r', encoding='utf-8') as f:
                    content = f.read()

                text_content[str(file_info['path'])] = {
                    'text': content,
                    'confidence': 1.0,  # Text files have perfect confidence
                    'metadata': {
                        'file_size': file_info['size'],
                        'modified': file_info['modified'].isoformat(),
                        'encoding': 'utf-8'
                    },
                    'source_type': 'text',
                    'source_file': str(file_info['path']),
                    'processing_time': 0.0
                }

                self.processing_stats['files_successful'] += 1

            except Exception as e:
                self.logger.error(f"Error reading text file {file_info['path']}: {e}")
                self.processing_stats['files_failed'] += 1
                self.processing_stats['errors'].append({
                    'type': 'text_processing_error',
                    'file': str(file_info['path']),
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                })

        self.processing_stats['files_processed'] += len(files)
        self.logger.info(f"Text processing completed: {len(text_content)} successful")

        return text_content

    async def _classify_content_batch(self, content_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Classify content using Claude API"""
        self.logger.info(f"Classifying {len(content_dict)} content items")
        classified_content = {}

        # Process classifications concurrently
        semaphore = asyncio.Semaphore(self.config.performance.max_concurrent_classifications)

        async def classify_single_item(file_path: str, content: Dict[str, Any]) -> Optional[Tuple[str, Dict[str, Any]]]:
            async with semaphore:
                try:
                    classification = await self.claude_classifier.classify_content(content['text'])
                    if classification:
                        enhanced_content = {**content, **classification}
                        return file_path, enhanced_content
                    return None

                except Exception as e:
                    self.logger.error(f"Error classifying content from {file_path}: {e}")
                    self.processing_stats['errors'].append({
                        'type': 'classification_error',
                        'file': file_path,
                        'message': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
                    return None

        # Execute classification tasks
        tasks = [classify_single_item(fp, content) for fp, content in content_dict.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect successful results
        for result in results:
            if result and not isinstance(result, Exception):
                file_path, content = result
                classified_content[file_path] = content

        self.logger.info(f"Classification completed: {len(classified_content)} successful")
        return classified_content

    async def _enhance_with_research(self, classified_content: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance content with Perplexity research"""
        self.logger.info(f"Enhancing {len(classified_content)} items with research")
        enhanced_content = {}

        for file_path, content in classified_content.items():
            try:
                # Only research insights and significant diary entries
                if content.get('category') in ['insight', 'diary'] and content.get('priority', 'low') in ['high', 'urgent']:
                    research_result = await self.perplexity_researcher.research_content(content)
                    if research_result:
                        enhanced_content[file_path] = {**content, 'research': research_result}
                    else:
                        enhanced_content[file_path] = content
                else:
                    enhanced_content[file_path] = content

            except Exception as e:
                self.logger.error(f"Error researching content from {file_path}: {e}")
                self.processing_stats['errors'].append({
                    'type': 'research_error',
                    'file': file_path,
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                enhanced_content[file_path] = content  # Keep original content

        self.logger.info(f"Research enhancement completed: {len(enhanced_content)} items")
        return enhanced_content

    async def _generate_garden_content(self, enhanced_content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured content for digital garden"""
        self.logger.info(f"Generating digital garden content for {len(enhanced_content)} items")
        garden_content = {}

        for file_path, content in enhanced_content.items():
            try:
                # Generate structured content based on category
                structured_content = await self.claude_classifier.generate_structured_content(content)
                if structured_content:
                    garden_content[file_path] = structured_content
                    self.processing_stats['content_generated'] += 1

            except Exception as e:
                self.logger.error(f"Error generating garden content from {file_path}: {e}")
                self.processing_stats['errors'].append({
                    'type': 'content_generation_error',
                    'file': file_path,
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                })

        self.logger.info(f"Garden content generation completed: {len(garden_content)} items")
        return garden_content

    async def _deploy_content(self, garden_content: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy content using Git automation"""
        self.logger.info(f"Deploying {len(garden_content)} content items")

        try:
            deployment_result = await self.git_automation.deploy_content_batch(garden_content)
            if deployment_result and deployment_result.success:
                self.processing_stats['git_commits'] += deployment_result.commits_created
                self.logger.info(f"Deployment successful: {deployment_result.commits_created} commits")
            return deployment_result

        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            self.processing_stats['errors'].append({
                'type': 'deployment_error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            })
            raise

    async def _cleanup_processed_files(self, input_files: List[Dict[str, Any]]) -> None:
        """Archive processed files to prevent reprocessing"""
        self.logger.info(f"Cleaning up {len(input_files)} processed files")

        processed_dir = Path(self.config.paths.input_processed)
        processed_dir.mkdir(exist_ok=True)

        session_dir = processed_dir / self.session_id
        session_dir.mkdir(exist_ok=True)

        for file_info in input_files:
            try:
                source_path = file_info['path']
                dest_path = session_dir / source_path.name
                source_path.rename(dest_path)
                self.logger.debug(f"Moved {source_path} to {dest_path}")

            except Exception as e:
                self.logger.warning(f"Failed to move processed file {file_info['path']}: {e}")

    def _generate_results_summary(self) -> Dict[str, Any]:
        """Generate comprehensive results summary"""
        duration = None
        if self.processing_stats['start_time'] and self.processing_stats['end_time']:
            duration = (self.processing_stats['end_time'] - self.processing_stats['start_time']).total_seconds()

        return {
            'session_id': self.session_id,
            'processing_stats': self.processing_stats,
            'summary': {
                'duration_seconds': duration,
                'success_rate': (
                    (self.processing_stats['files_successful'] / max(self.processing_stats['files_processed'], 1)) * 100
                    if self.processing_stats['files_processed'] > 0 else 0
                ),
                'total_errors': len(self.processing_stats['errors']),
                'content_generated': self.processing_stats['content_generated'],
                'git_commits': self.processing_stats['git_commits']
            },
            'errors': self.processing_stats['errors']
        }

# Main entry point for command-line usage
async def main():
    """Main entry point for CLI usage"""
    import sys

    config_path = sys.argv[1] if len(sys.argv) > 1 else None

    processor = DigitalGardenProcessor(config_path)

    try:
        results = await processor.process_all_inputs()
        print(json.dumps(results, indent=2, default=str))
        return 0

    except Exception as e:
        print(f"Processing failed: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))