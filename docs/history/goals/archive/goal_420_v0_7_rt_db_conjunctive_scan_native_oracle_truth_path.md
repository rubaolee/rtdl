# Goal 420: v0.7 RT DB Conjunctive Scan Native Oracle Truth Path

## Goal

Replace the temporary Python-detour `run_cpu(...)` path for `conjunctive_scan`
with a real native/oracle bounded implementation.

## Required outcome

- `run_cpu(...)` for `conjunctive_scan` no longer depends on the Python truth
  helper
- the native/oracle path remains bounded and honest
- parity is shown against:
  - Python truth path
  - PostgreSQL on Linux when available

## Review requirement

This goal requires at least 2-AI consensus before closure.
