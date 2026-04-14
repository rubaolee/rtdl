# Goal 370: v0.6 DuckDB out-of-scope baseline decision

## Why this goal exists

The detailed Gemini audit identified the absence of a DuckDB fallback baseline
and recommended adding it in a later `v0.6` increment.

The project direction is now explicit:

- `v0.6` uses PostgreSQL as the SQL/database baseline
- DuckDB is not part of the planned graph-baseline stack

This decision should be recorded in the repo so the audit note does not remain
an unresolved ambiguity.

## Scope

In scope:

- record the baseline decision explicitly
- resolve the DuckDB audit item by scope choice
- keep the current graph-baseline stack honest and stable

Out of scope:

- implementing DuckDB
- changing the current PostgreSQL graph baseline
- re-opening `v0.5` or `v0.6` correctness gates

## Exit condition

This goal is complete when the repo has:

- a saved decision report
- a saved external review
- a saved Codex consensus note
