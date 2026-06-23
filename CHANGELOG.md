# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-23

### Added
- `csvdiff diff OLD NEW --key ...` — diff two CSVs by one or more key columns, classifying
  rows as added / removed / changed (with per-field old→new deltas) / unchanged.
- `--columns`, `--ignore`, composite keys, `--format text|summary|json`, and `--exit-code`
  for CI gating; duplicate-key detection (last-wins, warned).
- Library API: `diff_files`, `diff_rows`, `read_csv`, and the `DiffResult` / `ChangedRow` /
  `FieldChange` dataclasses.
- Pure-standard-library implementation (csv + argparse), offline test suite, and CI on
  Python 3.10–3.12.

[0.1.0]: https://github.com/Amarel-Taylor-Scott/csvdiff/releases/tag/v0.1.0
