# Two-AI Goal1437 v1.5.1 COLLECT_K_BOUNDED Result Validator Capacity Metadata Consensus

## Verdict

ACCEPTED for commit as fail-clear result-validator metadata hardening.

This consensus does not authorize stable `COLLECT_K_BOUNDED` promotion, public speedup wording, zero-copy wording, whole-app speedup claims, release tags, or release action.

## Reviewed Scope

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `tests/goal1413_v1_5_1_collect_k_result_validator_test.py`
- `docs/reports/goal1437_v1_5_1_collect_k_result_validator_capacity_metadata_hardening_2026-05-07.md`

## Consensus

Codex accepts the patch because `validate_collect_k_bounded_result(...)` now rejects result dictionaries that omit both `capacity` and `valid_count`, preserving fail-closed behavior with a clearer error.

Claude reviewed the patch and returned `ACCEPT WITH NOTES`. Claude confirmed that the silent missing-capacity fallback was correctly replaced and that `valid_count`-only transition compatibility is preserved. Claude noted that the `valid_count`-only path should be tested and that the old `0` fallback was now unreachable.

Both Claude notes were addressed before commit: a `valid_count`-only compatibility regression test was added, and the unreachable `0` fallback was removed.

Gemini was not rerun for this non-key traceability patch because the immediately preceding Goal1435 Gemini review attempts timed out twice without usable output. No Gemini review is claimed for this patch.

## Validation

Windows focused slice after addressing Claude notes:

```text
Ran 33 tests in 0.026s
OK
```

Linux GPU pod focused slice with the OptiX environment loaded after addressing Claude notes:

```text
Ran 33 tests in 1.888s
OK
```

`git diff --check` passed with only expected Windows LF-to-CRLF warnings.
