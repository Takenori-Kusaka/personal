"""
Digital Garden Automation System
Main automation package for intelligent content processing

Author: Claude Code Assistant
Date: 2025-10-04
Version: 2.0
"""

from .digital_garden_processor import DigitalGardenProcessor
from .config.settings import AutomationConfig

__version__ = "2.0.0"
__author__ = "Claude Code Assistant"

__all__ = [
    "DigitalGardenProcessor",
    "AutomationConfig"
]