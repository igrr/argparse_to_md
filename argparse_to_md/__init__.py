try:
    from ._version import __version__
except ImportError:
    # This happens when the package is not installed, e.g. when running pre-commit in CI
    __version__ = "0.0.0"

from .loader import FunctionLoader
from .markdown_processor import process_markdown

__all__ = ["process_markdown", "FunctionLoader", "__version__"]
