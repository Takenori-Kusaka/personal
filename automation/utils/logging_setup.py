"""
Logging Setup Utility
Configures centralized logging for the Digital Garden automation system

Author: Claude Code Assistant
Date: 2025-10-04
Version: 2.0
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from automation.config.settings import LoggingConfig

def setup_logging(config: LoggingConfig) -> logging.Logger:
    """
    Setup centralized logging with file and console handlers

    Args:
        config: LoggingConfig instance with logging settings

    Returns:
        Configured logger instance
    """

    # Create root logger
    logger = logging.getLogger('automation')
    logger.setLevel(getattr(logging, config.level.upper()))

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(config.format)

    # Console handler
    if config.console_enabled:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config.level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler with rotation
    if config.file_enabled:
        # Ensure log directory exists
        log_path = Path(config.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            filename=config.file_path,
            maxBytes=config.max_file_size_mb * 1024 * 1024,
            backupCount=config.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, config.level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f'automation.{name}')

def log_function_call(logger: logging.Logger, func_name: str, **kwargs):
    """
    Log function call with parameters

    Args:
        logger: Logger instance
        func_name: Function name
        **kwargs: Function parameters to log
    """
    params = ', '.join(f'{k}={v}' for k, v in kwargs.items() if not k.startswith('_'))
    logger.debug(f"Calling {func_name}({params})")

def log_performance(logger: logging.Logger, operation: str, duration: float, **metrics):
    """
    Log performance metrics

    Args:
        logger: Logger instance
        operation: Operation name
        duration: Duration in seconds
        **metrics: Additional performance metrics
    """
    metrics_str = ', '.join(f'{k}={v}' for k, v in metrics.items())
    logger.info(f"Performance [{operation}]: {duration:.2f}s ({metrics_str})")

def log_error_with_context(logger: logging.Logger, error: Exception, context: dict = None):
    """
    Log error with additional context

    Args:
        logger: Logger instance
        error: Exception instance
        context: Additional context information
    """
    context_str = ""
    if context:
        context_str = " | " + ', '.join(f'{k}={v}' for k, v in context.items())

    logger.error(f"Error: {str(error)}{context_str}", exc_info=True)

class StructuredLogger:
    """
    Structured logger for consistent logging across components
    """

    def __init__(self, name: str):
        self.logger = get_logger(name)
        self.name = name

    def info(self, message: str, **context):
        """Log info message with context"""
        self._log_with_context(self.logger.info, message, context)

    def warning(self, message: str, **context):
        """Log warning message with context"""
        self._log_with_context(self.logger.warning, message, context)

    def error(self, message: str, error: Optional[Exception] = None, **context):
        """Log error message with context and exception"""
        if error:
            context['error_type'] = type(error).__name__
            context['error_message'] = str(error)

        self._log_with_context(self.logger.error, message, context)

        if error:
            self.logger.debug("Exception details:", exc_info=error)

    def debug(self, message: str, **context):
        """Log debug message with context"""
        self._log_with_context(self.logger.debug, message, context)

    def performance(self, operation: str, duration: float, **metrics):
        """Log performance metrics"""
        log_performance(self.logger, operation, duration, **metrics)

    def function_call(self, func_name: str, **kwargs):
        """Log function call"""
        log_function_call(self.logger, func_name, **kwargs)

    def _log_with_context(self, log_func, message: str, context: dict):
        """Log message with structured context"""
        if context:
            context_str = " | " + ', '.join(f'{k}={v}' for k, v in context.items())
            log_func(f"[{self.name}] {message}{context_str}")
        else:
            log_func(f"[{self.name}] {message}")

class PerformanceTracker:
    """
    Context manager for tracking operation performance
    """

    def __init__(self, logger: StructuredLogger, operation: str, **initial_metrics):
        self.logger = logger
        self.operation = operation
        self.metrics = initial_metrics
        self.start_time = None

    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.debug(f"Starting operation: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time

        if exc_type is not None:
            self.logger.error(
                f"Operation failed: {self.operation}",
                error=exc_val,
                duration=duration,
                **self.metrics
            )
        else:
            self.logger.performance(self.operation, duration, **self.metrics)

    def add_metric(self, key: str, value):
        """Add a metric to be logged"""
        self.metrics[key] = value

    def update_metrics(self, **metrics):
        """Update multiple metrics"""
        self.metrics.update(metrics)