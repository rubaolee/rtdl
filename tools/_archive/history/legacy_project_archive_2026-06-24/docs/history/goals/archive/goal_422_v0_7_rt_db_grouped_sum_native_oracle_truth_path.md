# Goal 422: v0.7 RT DB Grouped Sum Native Oracle Truth Path

## Goal

Replace the temporary Python-detour `run_cpu(...)` path for bounded
single-group-key `grouped_sum` with a real native/oracle implementation.

## Required outcome

- `run_cpu(...)` for bounded `grouped_sum` no longer depends on the Python
  truth helper when one group key is used
- parity is shown against:
  - Python truth path
  - PostgreSQL on Linux when available
- the grouped native boundary is explicit

## Review requirement

This goal requires at least 2-AI consensus before closure.
