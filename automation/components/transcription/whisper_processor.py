"""
Whisper Transcription System
Enhanced Whisper-based transcription with quality assessment and metadata extraction

Author: Claude Code Assistant
Date: 2025-10-04
Version: 2.0
"""

import asyncio
from pathlib import Path
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

try:
    import torch
    import torchaudio
    from transformers import pipeline, AutoProcessor, AutoModelForSpeechSeq2Seq
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from automation.config.settings import TranscriptionConfig
from automation.utils.logging_setup import StructuredLogger, PerformanceTracker
from automation.utils.file_handler import FileHandler

@dataclass
class AudioMetadata:
    """Audio file metadata structure"""
    duration_seconds: float
    sample_rate: int
    channels: int
    format: str
    bitrate: Optional[int] = None
    file_size_bytes: int = 0
    codec: Optional[str] = None

@dataclass
class TranscriptionSegment:
    """Individual transcription segment with timing"""
    start_time: float
    end_time: float
    text: str
    confidence: float
    speaker_id: Optional[int] = None
    language_probability: Optional[float] = None

@dataclass
class TranscriptionResult:
    """Complete transcription result structure"""
    text: str
    confidence: float
    segments: List[TranscriptionSegment]
    processing_time: float
    source_file: Path
    audio_metadata: AudioMetadata
    language_detected: Optional[str] = None
    quality_assessment: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class WhisperProcessor:
    """
    Enhanced Whisper transcription processor with quality assessment
    Supports the kotoba-tech/kotoba-whisper-v2.0 model optimized for Japanese
    """

    def __init__(self, config: TranscriptionConfig):
        """Initialize the Whisper processor"""
        self.config = config
        self.logger = StructuredLogger('whisper_processor')
        self.file_handler = FileHandler()

        self.model = None
        self.processor = None
        self.pipeline = None
        self.device = self._determine_device()

        self.logger.info("WhisperProcessor initialized",
                        model=config.model_name,
                        device=self.device,
                        language=config.language)

    def _determine_device(self) -> str:
        """Determine best available device for processing"""
        if not TRANSFORMERS_AVAILABLE:
            self.logger.warning("Transformers library not available, transcription will not work")
            return "cpu"

        if self.config.device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
                self.logger.info("CUDA available, using GPU acceleration")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device = "mps"
                self.logger.info("Apple Silicon detected, using MPS acceleration")
            else:
                device = "cpu"
                self.logger.info("Using CPU for transcription")
        else:
            device = self.config.device

        return device

    async def initialize_model(self) -> bool:
        """
        Initialize the Whisper model asynchronously

        Returns:
            True if initialization successful, False otherwise
        """
        if not TRANSFORMERS_AVAILABLE:
            self.logger.error("Cannot initialize model: transformers library not available")
            return False

        if self.model is not None:
            self.logger.debug("Model already initialized")
            return True

        try:
            with PerformanceTracker(self.logger, "model_initialization"):
                self.logger.info("Initializing Whisper model", model=self.config.model_name)

                # Initialize model for automatic speech recognition
                self.pipeline = pipeline(
                    "automatic-speech-recognition",
                    model=self.config.model_name,
                    torch_dtype=torch.float16 if self.config.compute_type == "float16" else torch.float32,
                    device=self.device,
                    model_kwargs={"attn_implementation": "flash_attention_2"} if self.device == "cuda" else {}
                )

                # Set generation parameters
                self.pipeline.model.config.forced_decoder_ids = None

                # Test model with dummy input
                await self._test_model()

                self.logger.info("Whisper model initialized successfully")
                return True

        except Exception as e:
            self.logger.error("Model initialization failed", error=e)
            return False

    async def _test_model(self) -> None:
        """Test model with dummy audio to ensure it's working"""
        try:
            # Create dummy audio (1 second of silence)
            dummy_audio = torch.zeros(16000, dtype=torch.float32)

            # Test transcription
            result = await asyncio.get_event_loop().run_in_executor(
                None, self._transcribe_audio_sync, dummy_audio.numpy(), 16000
            )

            if result:
                self.logger.debug("Model test successful")
            else:
                self.logger.warning("Model test returned empty result")

        except Exception as e:
            self.logger.error("Model test failed", error=e)
            raise

    async def transcribe_file(self, file_path: Union[str, Path]) -> Optional[TranscriptionResult]:
        """
        Transcribe audio file with quality assessment

        Args:
            file_path: Path to audio/video file

        Returns:
            TranscriptionResult or None if failed
        """
        file_path = Path(file_path)

        with PerformanceTracker(self.logger, "transcription", file=str(file_path)) as tracker:
            try:
                # Validate file
                validation = self.file_handler.validate_file(
                    file_path,
                    allowed_types=self.config.supported_formats,
                    max_size_mb=self.config.max_file_size_mb
                )

                if not validation['valid']:
                    self.logger.error("File validation failed",
                                    file=str(file_path),
                                    errors=validation['errors'])
                    return None

                # Initialize model if needed
                if not await self.initialize_model():
                    return None

                # Extract audio metadata
                audio_metadata = await self._extract_audio_metadata(file_path)
                tracker.add_metric('duration_seconds', audio_metadata.duration_seconds)

                self.logger.info("Starting transcription",
                               file=str(file_path),
                               duration=f"{audio_metadata.duration_seconds:.1f}s")

                # Load and preprocess audio
                audio_data, sample_rate = await self._load_audio(file_path)
                if audio_data is None:
                    return None

                # Perform transcription
                transcription_result = await self._transcribe_audio(audio_data, sample_rate)
                if not transcription_result:
                    return None

                # Create final result
                result = TranscriptionResult(
                    text=transcription_result['text'],
                    confidence=transcription_result['confidence'],
                    segments=transcription_result['segments'],
                    processing_time=tracker.metrics.get('duration', 0),
                    source_file=file_path,
                    audio_metadata=audio_metadata,
                    language_detected=transcription_result.get('language'),
                    quality_assessment=transcription_result.get('quality_assessment', {}),
                    metadata={
                        'model_name': self.config.model_name,
                        'device': self.device,
                        'timestamp': datetime.now().isoformat(),
                        'config': {
                            'language': self.config.language,
                            'task': self.config.task,
                            'chunk_duration': self.config.chunk_duration
                        }
                    }
                )

                self.logger.info("Transcription completed",
                               file=str(file_path),
                               text_length=len(result.text),
                               confidence=f"{result.confidence:.2f}",
                               segments=len(result.segments))

                return result

            except Exception as e:
                self.logger.error("Transcription failed", error=e, file=str(file_path))
                return None

    async def _extract_audio_metadata(self, file_path: Path) -> AudioMetadata:
        """Extract metadata from audio file"""
        try:
            # Use torchaudio to get basic metadata
            if TRANSFORMERS_AVAILABLE:
                info = torchaudio.info(str(file_path))
                return AudioMetadata(
                    duration_seconds=info.num_frames / info.sample_rate,
                    sample_rate=info.sample_rate,
                    channels=info.num_channels,
                    format=file_path.suffix.lstrip('.').lower(),
                    file_size_bytes=file_path.stat().st_size
                )
            else:
                # Fallback metadata extraction
                file_stats = file_path.stat()
                return AudioMetadata(
                    duration_seconds=0.0,  # Cannot determine without proper audio library
                    sample_rate=16000,  # Assume standard rate
                    channels=1,  # Assume mono
                    format=file_path.suffix.lstrip('.').lower(),
                    file_size_bytes=file_stats.st_size
                )

        except Exception as e:
            self.logger.warning("Could not extract audio metadata", error=e)
            file_stats = file_path.stat()
            return AudioMetadata(
                duration_seconds=0.0,
                sample_rate=16000,
                channels=1,
                format=file_path.suffix.lstrip('.').lower(),
                file_size_bytes=file_stats.st_size
            )

    async def _load_audio(self, file_path: Path) -> tuple[Optional[Any], Optional[int]]:
        """Load and preprocess audio file"""
        try:
            if not TRANSFORMERS_AVAILABLE:
                self.logger.error("Cannot load audio: required libraries not available")
                return None, None

            # Load audio with torchaudio
            waveform, sample_rate = torchaudio.load(str(file_path))

            # Convert to mono if stereo
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)

            # Convert to numpy and flatten
            audio_data = waveform.squeeze().numpy()

            self.logger.debug("Audio loaded",
                            sample_rate=sample_rate,
                            duration=f"{len(audio_data) / sample_rate:.1f}s",
                            channels=waveform.shape[0])

            return audio_data, sample_rate

        except Exception as e:
            self.logger.error("Audio loading failed", error=e, file=str(file_path))
            return None, None

    async def _transcribe_audio(self, audio_data: Any, sample_rate: int) -> Optional[Dict[str, Any]]:
        """Perform the actual transcription"""
        try:
            # Prepare transcription parameters
            generate_kwargs = {
                "language": self.config.language,
                "task": self.config.task,
                "return_timestamps": True,
            }

            # Run transcription in executor to avoid blocking
            result = await asyncio.get_event_loop().run_in_executor(
                None, self._transcribe_audio_sync, audio_data, sample_rate, generate_kwargs
            )

            if not result:
                return None

            # Process segments and calculate confidence
            segments = self._process_segments(result.get("chunks", []))
            overall_confidence = self._calculate_overall_confidence(segments)

            # Quality assessment
            quality_assessment = self._assess_transcription_quality(result["text"], segments)

            return {
                "text": result["text"].strip(),
                "confidence": overall_confidence,
                "segments": segments,
                "language": result.get("language"),
                "quality_assessment": quality_assessment
            }

        except Exception as e:
            self.logger.error("Audio transcription failed", error=e)
            return None

    def _transcribe_audio_sync(self, audio_data: Any, sample_rate: int, generate_kwargs: Dict = None) -> Optional[Dict]:
        """Synchronous transcription function for executor"""
        try:
            if self.pipeline is None:
                raise RuntimeError("Pipeline not initialized")

            generate_kwargs = generate_kwargs or {}

            # Perform transcription
            result = self.pipeline(
                audio_data,
                chunk_length_s=self.config.chunk_duration,
                generate_kwargs=generate_kwargs
            )

            return result

        except Exception as e:
            self.logger.error("Synchronous transcription failed", error=e)
            return None

    def _process_segments(self, chunks: List[Dict]) -> List[TranscriptionSegment]:
        """Process transcription chunks into segments"""
        segments = []

        for chunk in chunks:
            if "timestamp" in chunk and chunk["timestamp"]:
                start_time, end_time = chunk["timestamp"]
                # Handle None end time
                if end_time is None:
                    end_time = start_time + 1.0  # Default 1 second duration

                segment = TranscriptionSegment(
                    start_time=float(start_time),
                    end_time=float(end_time),
                    text=chunk["text"].strip(),
                    confidence=1.0  # Whisper doesn't provide per-segment confidence
                )
                segments.append(segment)

        return segments

    def _calculate_overall_confidence(self, segments: List[TranscriptionSegment]) -> float:
        """Calculate overall confidence score"""
        if not segments:
            return 0.0

        # Since Whisper doesn't provide confidence scores, we use heuristics
        total_chars = sum(len(segment.text) for segment in segments)
        if total_chars == 0:
            return 0.0

        # Confidence based on text characteristics
        confidence_score = 1.0

        # Reduce confidence for very short text
        if total_chars < 10:
            confidence_score *= 0.5

        # Reduce confidence for excessive repetition
        text_set = set(''.join(segment.text for segment in segments).split())
        if len(text_set) < total_chars / 20:  # Too much repetition
            confidence_score *= 0.7

        return max(0.0, min(1.0, confidence_score))

    def _assess_transcription_quality(self, text: str, segments: List[TranscriptionSegment]) -> Dict[str, float]:
        """Assess transcription quality with various metrics"""
        assessment = {
            "text_length_score": min(1.0, len(text) / 100),  # Normalized by expected length
            "segment_consistency": 1.0,  # Default high score
            "language_consistency": 1.0,  # Default high score
            "temporal_consistency": 1.0   # Default high score
        }

        # Check temporal consistency
        if len(segments) > 1:
            time_gaps = []
            for i in range(1, len(segments)):
                gap = segments[i].start_time - segments[i-1].end_time
                time_gaps.append(gap)

            if time_gaps:
                # Penalize large time gaps or overlaps
                avg_gap = sum(abs(gap) for gap in time_gaps) / len(time_gaps)
                if avg_gap > 2.0:  # More than 2 seconds average gap
                    assessment["temporal_consistency"] *= 0.8

        # Check for repetitive patterns (possible hallucination)
        words = text.split()
        if words:
            unique_words = set(words)
            repetition_ratio = len(unique_words) / len(words)
            if repetition_ratio < 0.3:  # Too repetitive
                assessment["segment_consistency"] *= 0.6

        return assessment

    async def transcribe_batch(self, file_paths: List[Union[str, Path]]) -> Dict[str, Optional[TranscriptionResult]]:
        """
        Transcribe multiple files concurrently

        Args:
            file_paths: List of file paths to transcribe

        Returns:
            Dict mapping file paths to transcription results
        """
        self.logger.info("Starting batch transcription", file_count=len(file_paths))

        # Create semaphore to limit concurrent transcriptions
        semaphore = asyncio.Semaphore(self.config.max_concurrent_transcriptions if hasattr(self.config, 'max_concurrent_transcriptions') else 2)

        async def transcribe_with_semaphore(file_path):
            async with semaphore:
                return await self.transcribe_file(file_path)

        # Execute transcriptions
        tasks = [transcribe_with_semaphore(fp) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        batch_results = {}
        successful = 0
        failed = 0

        for file_path, result in zip(file_paths, results):
            if isinstance(result, Exception):
                self.logger.error("Batch transcription failed for file",
                                file=str(file_path), error=result)
                batch_results[str(file_path)] = None
                failed += 1
            else:
                batch_results[str(file_path)] = result
                if result:
                    successful += 1
                else:
                    failed += 1

        self.logger.info("Batch transcription completed",
                        total=len(file_paths),
                        successful=successful,
                        failed=failed)

        return batch_results

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_name": self.config.model_name,
            "device": self.device,
            "language": self.config.language,
            "task": self.config.task,
            "loaded": self.pipeline is not None,
            "transformers_available": TRANSFORMERS_AVAILABLE
        }