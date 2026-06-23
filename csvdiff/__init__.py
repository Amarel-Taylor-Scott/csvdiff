"""csvdiff — diff two CSV files by key column (pure stdlib)."""

from __future__ import annotations

from .__version__ import __version__
from .core import (ChangedRow, DiffResult, FieldChange, diff_files, diff_rows,
                   read_csv)

__all__ = [
    "__version__", "diff_files", "diff_rows", "read_csv",
    "DiffResult", "ChangedRow", "FieldChange",
]
