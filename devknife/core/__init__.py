"""
Core module containing interfaces, data models, and base classes.
"""

from .interfaces import UtilityModule
from .models import Command, InputData, ProcessingResult, Config, InputSource
from .io_handler import InputHandler, OutputFormatter, ErrorHandler, OutputFormat
from .router import (
    CommandRegistry, 
    CommandRouter, 
    get_global_registry, 
    get_global_router,
    register_utility,
    discover_utilities
)

__all__ = [
    "UtilityModule",
    "Command", 
    "InputData",
    "ProcessingResult",
    "Config",
    "InputSource",
    "InputHandler",
    "OutputFormatter", 
    "ErrorHandler",
    "OutputFormat",
    "CommandRegistry",
    "CommandRouter",
    "get_global_registry",
    "get_global_router", 
    "register_utility",
    "discover_utilities",
]