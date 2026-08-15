"""UNG node adapters for csvdiff — keyed record diffing without touching files.

Pure top-level function over the documented public API (``diff_rows``), fed
lists of dicts directly (headers are derived from the records in first-seen
key order), so the node bypasses file I/O entirely.  Returns a dict keyed by
the declared output port names.
"""
from __future__ import annotations

from typing import Any

from csvdiff import diff_rows


def _split(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _header(rows: list[dict]) -> list[str]:
    seen: list[str] = []
    for row in rows:
        for col in row:
            if col not in seen:
                seen.append(col)
    return seen


def diff_records(old_records: list[dict], new_records: list[dict], key: str,
                 columns: str = "", ignore: str = "") -> dict[str, Any]:
    """Diff two record lists by key column(s): added / removed / changed / unchanged."""
    key_cols = _split(key)
    result = diff_rows(
        _header(list(old_records)), list(old_records),
        _header(list(new_records)), list(new_records),
        key=key_cols,
        columns=_split(columns) or None,
        ignore=_split(ignore) or None,
    )
    return {"report": {
        "summary": result.summary(),
        "has_differences": result.has_differences,
        "key_columns": list(result.key_columns),
        "compared_columns": list(result.compared_columns),
        "added": list(result.added),
        "removed": list(result.removed),
        "changed": [
            {"key": list(ch.key),
             "changes": [{"column": c.column, "old": c.old, "new": c.new}
                         for c in ch.changes]}
            for ch in result.changed
        ],
        "unchanged": result.unchanged,
        "dup_keys_old": [list(k) for k in result.dup_keys_old],
        "dup_keys_new": [list(k) for k in result.dup_keys_new],
    }}


NODES = [
    {
        "fn": diff_records,
        "id": "amarel.csvdiff.diff-records",
        "capabilities": ["records.diff"],
        "summary": "Diff two lists of records by key column(s): added, removed, per-field changed, unchanged.",
        "inputs": [
            {"name": "old_records", "type_id": "amarel.types.records",
             "description": "Baseline records (list of flat dicts)."},
            {"name": "new_records", "type_id": "amarel.types.records",
             "description": "Updated records (list of flat dicts)."},
        ],
        "outputs": [
            {"name": "report", "type_id": "amarel.types.report",
             "description": "{summary, has_differences, added, removed, changed[{key, changes}], unchanged, dup_keys_*}."},
        ],
        "parameters": [
            {"name": "key", "value_type": "string", "required": True},
            {"name": "columns", "value_type": "string", "default": "",
             "required": False},
            {"name": "ignore", "value_type": "string", "default": "",
             "required": False},
        ],
        "effects": [],
        "determinism": "deterministic",
        "idempotency": "idempotent",
        "tags": ["license.mit", "runtime.python", "dependency-free"],
    },
]
