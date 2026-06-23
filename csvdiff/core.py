"""Diff two CSV files by a key column. Pure stdlib.

Rows are matched on one or more **key** columns. The result classifies every row as:

- **added**   — key present only in the new file
- **removed** — key present only in the old file
- **changed** — key in both, but one or more compared values differ (per-field deltas)
- **unchanged** — key in both, all compared values equal

By default every column the two files share (minus the key and any ``ignore``d
columns) is compared; pass ``columns`` to compare only a subset.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FieldChange:
    column: str
    old: str
    new: str


@dataclass
class ChangedRow:
    key: tuple[str, ...]
    changes: list[FieldChange]


@dataclass
class DiffResult:
    key_columns: list[str]
    compared_columns: list[str]
    added: list[dict] = field(default_factory=list)
    removed: list[dict] = field(default_factory=list)
    changed: list[ChangedRow] = field(default_factory=list)
    unchanged: int = 0
    dup_keys_old: list[tuple[str, ...]] = field(default_factory=list)
    dup_keys_new: list[tuple[str, ...]] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> dict:
        return {
            "added": len(self.added),
            "removed": len(self.removed),
            "changed": len(self.changed),
            "unchanged": self.unchanged,
        }


def read_csv(path: str | Path) -> tuple[list[str], list[dict]]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        rows = [dict(r) for r in reader]
    return list(header), rows


def _key_of(row: dict, key_columns: list[str]) -> tuple[str, ...]:
    return tuple(row.get(k, "") for k in key_columns)


def _index_by_key(rows: list[dict], key_columns: list[str]):
    index: dict[tuple[str, ...], dict] = {}
    dups: list[tuple[str, ...]] = []
    for row in rows:
        k = _key_of(row, key_columns)
        if k in index:
            dups.append(k)
        index[k] = row          # last-wins on duplicates
    return index, dups


def diff_rows(old_header: list[str], old_rows: list[dict],
              new_header: list[str], new_rows: list[dict], *,
              key: list[str], columns: list[str] | None = None,
              ignore: list[str] | None = None) -> DiffResult:
    for k in key:
        if k not in old_header or k not in new_header:
            raise ValueError(f"key column {k!r} not present in both files")

    if columns is not None:
        compared = list(columns)
    else:
        shared = [c for c in new_header if c in old_header]
        ignore_set = set(ignore or []) | set(key)
        compared = [c for c in shared if c not in ignore_set]

    old_idx, dup_old = _index_by_key(old_rows, key)
    new_idx, dup_new = _index_by_key(new_rows, key)

    result = DiffResult(key_columns=list(key), compared_columns=compared,
                        dup_keys_old=dup_old, dup_keys_new=dup_new)

    for k, row in new_idx.items():
        if k not in old_idx:
            result.added.append(row)

    for k, row in old_idx.items():
        if k not in new_idx:
            result.removed.append(row)

    for k, new_row in new_idx.items():
        if k not in old_idx:
            continue
        old_row = old_idx[k]
        changes = [
            FieldChange(col, old_row.get(col, ""), new_row.get(col, ""))
            for col in compared
            if old_row.get(col, "") != new_row.get(col, "")
        ]
        if changes:
            result.changed.append(ChangedRow(key=k, changes=changes))
        else:
            result.unchanged += 1

    return result


def diff_files(old_path: str | Path, new_path: str | Path, *,
               key: list[str], columns: list[str] | None = None,
               ignore: list[str] | None = None) -> DiffResult:
    oh, orows = read_csv(old_path)
    nh, nrows = read_csv(new_path)
    return diff_rows(oh, orows, nh, nrows, key=key, columns=columns, ignore=ignore)
