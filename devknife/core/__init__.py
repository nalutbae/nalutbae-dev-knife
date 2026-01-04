"""
Core module containing interfaces, data models, and base classes.
"""

from .interfaces import UtilityModule
from .models import Command, InputData, ProcessingResult, Config

__all__ = [
    "UtilityModule",
    "Command", 
    "InputData",
    "ProcessingResult",
    "Config",
]