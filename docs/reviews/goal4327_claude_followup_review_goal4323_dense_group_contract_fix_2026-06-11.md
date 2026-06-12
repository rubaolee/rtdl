# Claude Follow-Up Review: Goal4323 Dense Group Contract Fix (post-Goal4324 rejection)

Date: 2026-06-11
Reviewer: Claude (external read-only review)
Target: Goal4323 follow-up fix — `_run_numba_grouped_arg_reduce_f64` NameError remediation

## Verdict

**accept-with-boundary**

The blocking NameError identified in Goal4324 is fully remediated. The stray
dense-contract assignment in the unrelated helper is gone. The non-Numba
front-door wiring from the original Goal4323 draft is intact and unchanged.
The report honestly discloses the rejection and the fix. No prohibited claim
appears.

---

## Check 1 — `_run_numba_grouped_arg_reduce_f64` now assigns `group_contract_metadata` before spreading it

**Pass.**

`numba_partner_continuation.py:1305–1316` now contains:

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

This assignment appears immediately after the `_validate_group_run_shape` call
at lines 1297–1304 and before the `cuda.synchronize()` at line 1318. All
needed values (`operation`, `group_count`, `row_count`, `validate_group_ids`)
are in-scope function parameters or are the returned values from
`_validate_group_run_shape`. The spread `**group_contract_metadata` at line
1399 is now safe.

This matches exactly the remediation recommended in the Goal4324 review. The
`validation_mode` toggle is correct: it distinguishes `"device_resident_error_flag"`
(when the caller asks for in-kernel validation) from `"caller_declared_unchecked"`
(when validation is skipped by the caller). That mirrors the logic used in the
top-k path.

---

## Check 2 — Stray dense-contract assignment is gone from the unrelated helper

**Pass.**

A full grep of `group_contract_metadata` in `numba_partner_continuation.py`
yields exactly two locations:

1. `run_numba_grouped_topk_f64` (lines 771–853): uses
   `make_equal_contiguous_group_id_contract` — correct and pre-existing.
2. `_run_numba_grouped_arg_reduce_f64` (lines 1305–1399): the newly added
   dense-zero-based assignment and its spread — the fix.

Neither `_run_numba_segmented_extreme_f64` (lines 1229–1270) nor
`run_numba_grouped_vector_sum_f64x2` (lines 381–438) contains any
`group_contract_metadata` reference. Both of these functions are clean.

**Naming note.** The handoff describes "the stray assignment in the segmented
extreme helper." The Goal4324 review had flagged the secondary stray in
`run_numba_grouped_vector_sum_f64x2`. The two descriptions refer to functions
with different names. Regardless of which function held the stray in the
intermediate draft, the current code is clean in all candidate locations. No
outstanding stray assignment or undefined-variable risk remains.

---

## Check 3 — Non-Numba front-door metadata from Goal4323 still holds

**Pass.**

`partner_adapters.py` is unchanged by the follow-up fix. The three front doors
that Goal4323 introduced (confirmed intact in Goal4324 Check 2) remain wired
correctly:

- `_dense_group_id_contract_metadata(...)` helper exists at line 2659.
- `grouped_argmin_f64_partner_columns` calls it at line 2831 with
  `operation="grouped_argmin_f64"`.
- `grouped_argmax_f64_partner_columns` calls it at line 2909 with
  `operation="grouped_argmax_f64"`.
- `grouped_topk_f64_partner_columns` calls it at line 3155 for non-Numba
  partners; the Numba sub-path correctly bypasses it (top-k requires
  `equal_contiguous_segments`, not `dense_zero_based`).

No regression in the adapter layer.

---

## Check 4 — Report accurately discloses the rejection and follow-up fix

**Pass.**

`docs/reports/goal4323_dense_group_contract_metadata_2026-06-11.md` contains a
dedicated "Goal4324 follow-up" paragraph (lines 35–41) that:

- Names Goal4324 and states it rejected the first draft.
- Explains the root cause: the Windows validation skipped the CUDA execution
  test, so the missing assignment was not caught.
- Describes both parts of the fix: adding the assignment in
  `_run_numba_grouped_arg_reduce_f64` and removing the misplaced assignment
  from the unrelated helper.
- States the corrected test result: 14 tests passed with 2 expected optional
  Numba CUDA skips.

The disclosure is accurate and complete. The self-verdict in the report
(`accept-with-boundary`) is consistent with the state of the code after the
fix.

---

## Check 5 — No prohibited claim is present

**Pass.**

The report's boundary section (lines 44–53) explicitly disclaims all
prohibited categories:

- No release action authorized.
- No public speedup claim authorized.
- No broad RT-core claim authorized.
- No true-zero-copy claim authorized.
- No automatic partner selection authorized.
- No app-specific native-engine logic authorized.
- No package-install claim.

Neither the report nor the source code introduces any wording that would imply
a promoted performance path, a whole-app speedup, or a production-release
status. `NUMBA_PARTNER_CONTINUATION_STATUS` is still
`V2_5_STATUS_PREVIEW_NOT_PROMOTED` throughout. All `_numba_run_result` returns
carry `promoted_performance_path: False` and
`rt_core_speedup_claim_authorized: False`.

---

## Summary

| Check | Result |
|-------|--------|
| 1. `group_contract_metadata` assigned before spread in `_run_numba_grouped_arg_reduce_f64` | Pass |
| 2. Stray dense-contract assignment removed from unrelated helpers | Pass |
| 3. Non-Numba front-door metadata wiring intact | Pass |
| 4. Report discloses rejection and follow-up fix accurately | Pass |
| 5. No prohibited claim present | Pass |

The Goal4324 blocking defect is resolved. The code is ready to proceed as
`accept-with-boundary` under the same scope declared in the Goal4323 report:
contract-hardening work only, no release or public claim authorized.
