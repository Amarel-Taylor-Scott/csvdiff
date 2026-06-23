# csvdiff

Diff two CSV files **by key column** — see exactly which rows were added, removed, or
changed, with per-field before/after values. Pure standard library, no dependencies.

A line-based `diff` is useless on CSVs: reorder the rows or add a column and everything
"changes." `csvdiff` matches rows on a key you choose and compares them semantically.

```bash
$ csvdiff diff examples/old.csv examples/new.csv --key id
+ [id=5] added
- [id=4] removed
~ [id=2]
    price: '19.99' -> '17.99'
    stock: '50' -> '45'
~ [id=3]
    stock: '0' -> '30'

+1 added  -1 removed  ~2 changed  =1 unchanged
```

## Why

- **Data-pipeline regression checks.** Compare yesterday's export to today's and fail CI
  on unexpected changes (`--exit-code`).
- **Reviewing data PRs.** A reviewable, row-level summary instead of an unreadable text
  diff.
- **Reconciliation.** Find what a vendor/feed changed between two drops.

## Install

```bash
pip install -e .
```

(Or copy the `csvdiff/` package — no dependencies.)

## CLI

```bash
csvdiff diff old.csv new.csv --key id
csvdiff diff old.csv new.csv --key region,sku          # composite key
csvdiff diff old.csv new.csv --key id --ignore updated_at,checksum
csvdiff diff old.csv new.csv --key id --columns price,stock   # compare only these
csvdiff diff old.csv new.csv --key id --format summary
csvdiff diff old.csv new.csv --key id --format json
csvdiff diff old.csv new.csv --key id --exit-code      # exit 1 if anything differs
```

| Flag | Meaning |
|------|---------|
| `--key` | key column(s), comma-separated (required) |
| `--columns` | only compare these columns |
| `--ignore` | ignore these columns when comparing |
| `--format text\|summary\|json` | output style (default `text`) |
| `--exit-code` | exit `1` when differences are found (for CI gates) |

By default every column the two files share — minus the key and any `--ignore`d columns —
is compared.

## Library

```python
from csvdiff import diff_files

result = diff_files("old.csv", "new.csv", key=["id"], ignore=["updated_at"])
print(result.summary())            # {'added': 1, 'removed': 1, 'changed': 2, 'unchanged': 1}
for ch in result.changed:
    print(ch.key, [(c.column, c.old, c.new) for c in ch.changes])
```

`DiffResult` exposes `added`, `removed`, `changed` (each a `ChangedRow` with `FieldChange`
deltas), `unchanged`, `has_differences`, and `summary()`.

## Notes & limits

- All values are compared as **strings** (CSV has no types). Use `--columns`/`--ignore` to
  scope the comparison; normalize types upstream if `9.9` vs `9.90` matters.
- Rows are matched on the key; on **duplicate keys** the last occurrence wins and a warning
  is printed to stderr.
- Files are read fully into memory — fine for the millions-of-rows-and-under case.

## License

[MIT](LICENSE) © 2026 Amarel Taylor Scott
