"""csvdiff CLI — diff two CSV files by key column."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from .__version__ import __version__
from .core import DiffResult, diff_files


def _split(value: str) -> list[str]:
    return [c.strip() for c in value.split(",") if c.strip()]


def _to_json(result: DiffResult) -> dict:
    return {
        "key_columns": result.key_columns,
        "compared_columns": result.compared_columns,
        "summary": result.summary(),
        "added": result.added,
        "removed": result.removed,
        "changed": [
            {"key": list(c.key), "changes": [asdict(fc) for fc in c.changes]}
            for c in result.changed
        ],
    }


def _print_text(result: DiffResult) -> None:
    s = result.summary()
    keyname = ",".join(result.key_columns)
    for row in result.added:
        print(f"+ [{keyname}={_keyvals(row, result.key_columns)}] added")
    for row in result.removed:
        print(f"- [{keyname}={_keyvals(row, result.key_columns)}] removed")
    for ch in result.changed:
        print(f"~ [{keyname}={','.join(ch.key)}]")
        for fc in ch.changes:
            print(f"    {fc.column}: {fc.old!r} -> {fc.new!r}")
    print(f"\n+{s['added']} added  -{s['removed']} removed  ~{s['changed']} changed  "
          f"={s['unchanged']} unchanged")
    if result.dup_keys_old or result.dup_keys_new:
        print(f"warning: duplicate keys (old={len(result.dup_keys_old)}, "
              f"new={len(result.dup_keys_new)}); last occurrence wins.", file=sys.stderr)


def _keyvals(row: dict, key_columns: list[str]) -> str:
    return ",".join(row.get(k, "") for k in key_columns)


def cmd_diff(args: argparse.Namespace) -> int:
    try:
        result = diff_files(
            args.old, args.new,
            key=_split(args.key),
            columns=_split(args.columns) if args.columns else None,
            ignore=_split(args.ignore) if args.ignore else None,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(_to_json(result), indent=2))
    elif args.format == "summary":
        s = result.summary()
        print(f"+{s['added']} added  -{s['removed']} removed  ~{s['changed']} changed  "
              f"={s['unchanged']} unchanged")
    else:
        _print_text(result)
    # exit 1 when there are differences (so it works as a CI gate); 0 when identical
    return 1 if result.has_differences and args.exit_code else 0


def cmd_version(_: argparse.Namespace) -> int:
    print(f"csvdiff {__version__}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csvdiff",
        description="Diff two CSV files by key column (added / removed / changed rows).",
    )
    p.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command")

    pd = sub.add_parser("diff", help="Diff OLD against NEW")
    pd.add_argument("old", help="Old/baseline CSV")
    pd.add_argument("new", help="New/current CSV")
    pd.add_argument("--key", required=True, help="Key column(s), comma-separated")
    pd.add_argument("--columns", default="", help="Only compare these columns (comma-separated)")
    pd.add_argument("--ignore", default="", help="Ignore these columns when comparing")
    pd.add_argument("--format", choices=["text", "summary", "json"], default="text")
    pd.add_argument("--exit-code", action="store_true",
                    help="Exit 1 when differences are found (useful in CI)")
    pd.set_defaults(func=cmd_diff)

    sub.add_parser("version", help="Print version").set_defaults(func=cmd_version)
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not getattr(args, "command", None):
        parser.print_help()
        sys.exit(0)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
