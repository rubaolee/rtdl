# Gemini Follow-Up Review: Goal4323 Dense Group Contract Metadata Fix

Date: 2026-06-11
Reviewer: Gemini (CLI autonomous agent)
Target: Goal4323 — follow-up fix after Goal4324 rejection

## Verdict

**accept**

The follow-up fix successfully addresses the `NameError` identified in Claude's Goal4324 review. The shared Numba arg-reduction runner now correctly assigns `group_contract_metadata` before use, and stray/broken assignments in unrelated helpers have been removed. The non-Numba front-door metadata threading remains correct, and the report has been updated to disclose the rejection and subsequent fix.

---

## Check 1 — `_run_numba_grouped_arg_reduce_f64` resolves NameError

**Pass.**

In `src/rtdsl/numba_partner_continuation.py` (lines 1311–1323), the missing assignment has been added:

```python
    group_contract_metadata = require_group_id_contract(
        make_dense_zero_based_group_id_contract(
            operation=operation,
            group_count=group_count,
            row_count=row_count,
            validation_mode=(
                "device_resident_error_flag"
                if validate_group_ids
                else "caller_declared_unchecked"
            ),
        )
    )
```

This correctly uses the available `operation`, `group_count`, `row_count`, and `validate_group_ids` variables to produce the metadata dictionary that is later spread into the result at line 1403. This resolves the blocking defect found in the first draft.

## Check 2 — Stray assignments removed from unrelated helpers

**Pass.**

Verified that `run_numba_grouped_vector_sum_f64x2` and `_run_numba_segmented_extreme_f64` in `numba_partner_continuation.py` no longer contain the broken/unused `group_contract_metadata` assignments mentioned in the Goal4324 review. These functions now correctly return their own operation-specific metadata without referencing undefined variables.

## Check 3 — Non-Numba front-door metadata threading holds

**Pass.**

`src/rtdsl/partner_adapters.py` correctly uses `_dense_group_id_contract_metadata` for `grouped_argmin_f64_partner_columns`, `grouped_argmax_f64_partner_columns`, and the non-Numba path of `grouped_topk_f64_partner_columns`. The `validation_mode` logic remains appropriately partitioned between Numba and Torch/Triton paths.

## Check 4 — Report accurately discloses rejection and fix

**Pass.**

`docs/reports/goal4323_dense_group_contract_metadata_2026-06-11.md` now includes a "Goal4324 follow-up" section that honestly describes the rejection and the specific code fixes applied. The self-verdict remains `accept-with-boundary`, which is appropriate for this contract-hardening work.

## Check 5 — Unauthorized claims and boundaries

**Pass.**

The report and code changes strictly adhere to the requested boundaries:
- No broad RT-core, speedup, or true-zero-copy claims are authorized.
- No automatic partner selection or app-specific native-engine logic is introduced.
- Public exports are limited to generic contract-layer symbols.

---

## Validation Summary

- **Tests:** `tests.goal4323_dense_group_contract_metadata_test` and related contract/adapter suites passed (14 tests total, with 2 expected Numba CUDA skips on Windows).
- **Compile:** Python compile checks passed for all touched modules.
- **Static Analysis:** Verified the resolution of the `NameError` through targeted file inspection.
