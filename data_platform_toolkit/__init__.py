"""Data Platform Toolkit - Utilities for data platform connections."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

try:
    __version__: str = _pkg_version("data-platform-toolkit")
except PackageNotFoundError:
    # Fallback for development environments (editable installs without metadata)
    import json
    from pathlib import Path
    __version__ = json.loads(
        (Path(__file__).parent.parent / "version.json").read_text()
    )["version"]

__all__ = ["__version__"]
