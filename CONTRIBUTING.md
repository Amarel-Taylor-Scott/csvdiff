# Contributing

Thanks for helping improve **csvdiff**!

## Dev setup

```bash
pip install -e ".[dev]"
pytest -q                    # fully offline
```

## Where things live

- **Diff engine (matching, classification, field deltas)** -> `csvdiff/core.py`
- **CLI (`diff` / `version`)** -> `csvdiff/cli.py`

Keep it **dependency-free** (csv + argparse). New behavior comes with tests built on small
in-memory row lists (`diff_rows`) and the bundled `examples/` CSVs (`diff_files`).

## Design rules

- Rows are matched on the **key**, never by position — reordering must be a no-op.
- Comparison is **string-based** (CSV is untyped); type-aware comparison belongs upstream.
- `--exit-code` makes `csvdiff` a CI gate: non-zero exit means "data changed."

## Reporting issues

Use the issue templates. For anything security-sensitive, see [SECURITY.md](SECURITY.md).
