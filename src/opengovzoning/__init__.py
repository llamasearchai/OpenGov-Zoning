"""OpenGov Zoning API core package."""

from .core.config import get_settings

__version__ = "1.0.0"
__author__ = "Nik Jois"
__email__ = "nikjois@llamasearch.ai"
__description__ = "Production-ready FastAPI application for comprehensive land use planning and permitting intelligence system"

# Application settings
settings = get_settings()

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "settings",
]
