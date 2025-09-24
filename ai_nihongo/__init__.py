"""
AI-Nihongo: An AI agent for Japanese language learning and processing.
"""

__version__ = "0.1.0"
__author__ = "HungVuLong"
__email__ = "your.email@example.com"

from .core.agent import AIAgent
from .core.config import Settings

__all__ = ["AIAgent", "Settings"]