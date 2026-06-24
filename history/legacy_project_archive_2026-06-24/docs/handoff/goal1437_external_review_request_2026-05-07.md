# Goal 1437 External Review Request

Please review the current uncommitted Goal1437 patch in this repository.

## Scope

Goal1437 hardens `validate_collect_k_bounded_result(...)` for v1.5.1 `COLLECT_K_BOUNDED`. The validator previously inferred capacity as `0` when both `capacity` and `valid_count` metadata were missing. This was fail-closed for non-empty rows, but surprising. The patch now rejects that missing-metadata case explicitly while preserving transition compatibility for result dictionaries that provide `valid_count` without `capacity`.

## Files To Review

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `tests/goal1413_v1_5_1_collect_k_result_validator_test.py`
- `docs/reports/goal1437_v1_5_1_collect_k_result_validator_capacity_metadata_hardening_2026-05-07.md`

## Validation

Windows focused slice:

```text
Ran 32 tests in 0.025s
OK
```

Linux GPU pod focused slice with the OptiX environment loaded:

```text
Ran 32 tests in 0.359s
OK
```

`git diff --check` passed with only expected Windows LF-to-CRLF warnings.

## Review Questions

1. Does this patch correctly replace the silent missing-capacity fallback with a clear fail-closed metadata error?
2. Does it preserve compatibility for callers that provide `valid_count` without `capacity`?
3. Are there any blockers that should prevent committing this hardening patch?

Please answer with `ACCEPT`, `ACCEPT WITH NOTES`, or `REJECT`, and list any precise blockers if rejected.
