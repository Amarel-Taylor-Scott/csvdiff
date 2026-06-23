# Security Policy

`csvdiff` reads CSV files locally and makes no network calls. It parses input with the
standard-library `csv` module and never executes input data.

- Input CSVs may contain sensitive data; handle them and any JSON output under your own
  data-governance rules.

## Reporting

Email **amarel.taylor.s@gmail.com** for any security concern rather than opening a public
issue.
