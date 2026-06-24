# Independent Review: Goal4323 Dense Group Contract Metadata

- Date: 2026-06-11
- Reviewer: Gemini
- Verdict: `reject`

## Summary

This review covers Goal4323, which adds dense zero-based group-id contract metadata to various grouped operations. While the core contract helper and the front-door adapters in `src/rtdsl/partner_adapters.py` are correctly implemented, the implementation within `src/rtdsl/numba_partner_continuation.py` contains critical bugs—specifically the use of undefined variables—that will cause runtime failures in the Numba path.

## Reviewer Checks

### 1. Confirm `make_dense_zero_based_group_id_contract(...)` is a generic, app-agnostic contract helper and that validation rejects invalid dense metadata.

**Yes.** The helper in `src/rtdsl/partner_column_contracts.py` is generic and correctly implements the requested validation rules. It rejects the use of `rows_per_group` (which belongs to the equal-contiguous layout) and ensures that non-empty row sets have a positive `group_count`.

### 2. Confirm grouped argmin, grouped argmax, and non-Numba grouped top-k front doors now emit shared dense group-id contract metadata.

**Yes.** In `src/rtdsl/partner_adapters.py`, the functions `grouped_argmin_f64_partner_columns`, `grouped_argmax_f64_partner_columns`, and `grouped_topk_f64_partner_columns` (non-Numba path) correctly utilize the `_dense_group_id_contract_metadata` helper to emit the shared contract metadata.

### 3. Confirm the direct Numba grouped argmin/argmax runner emits shared dense group-id contract metadata when executed.

**No.** The implementation in `src/rtdsl/numba_partner_continuation.py` is broken:
- In `_run_numba_grouped_arg_reduce_f64` (the shared implementation for argmin and argmax runners), the variable `group_contract_metadata` is used at line 1401 but is **never defined** within the function scope or the global scope. This will result in a `NameError` at runtime.
- In `run_numba_grouped_vector_sum_f64x2`, `group_contract_metadata` is defined at line 406 but is **not used** in the return result. Additionally, the definition itself (line 408) uses an undefined variable `operation`, which will also cause a `NameError`.

### 4. Confirm public exports are coherent and do not create an app-shaped API.

**Yes.** The exports in `src/rtdsl/__init__.py` include the new constants and helpers without introducing application-specific semantics. The API remains focused on generic partner-column contract metadata.

### 5. Confirm the report is honest that this is contract metadata hardening only.

**Mostly.** The report correctly identifies the scope as contract-hardening and explicitly lists the non-authorizing boundaries. However, it claims that dense contract metadata was successfully added to the direct Numba grouped argmin/argmax runner result, which is inaccurate given the runtime-breaking bugs discovered in that implementation.

## Detailed Findings (Bugs in `numba_partner_continuation.py`)

### Bug A: Undefined variable usage in `_run_numba_grouped_arg_reduce_f64`

```python
# src/rtdsl/numba_partner_continuation.py:1401
        extra_metadata={
            "tie_break": tie_break,
            "host_present_group_compaction_used": compact_present_groups,
            "nan_validation_host_sync_used": validate_nan_scores,
            **group_contract_metadata,  # <--- NameError: group_contract_metadata is not defined
        },
```

### Bug B: Undefined variable and unused result in `run_numba_grouped_vector_sum_f64x2`

```python
# src/rtdsl/numba_partner_continuation.py:406
    group_contract_metadata = require_group_id_contract(
        make_dense_zero_based_group_id_contract(
            operation=operation,  # <--- NameError: operation is not defined
            group_count=group_count,
            row_count=row_count,
            # ...
        )
    )

    # ... execution logic ...

    return _numba_run_result(
        # ...
        extra_metadata={
            # group_contract_metadata is never used here
            "group_count": group_count,
            "row_count": row_count,
            # ...
        },
    )
```

## Final Verdict

The core contract logic and front-door adapters are correct, but the Numba continuation layer has critical implementation errors that escaped validation due to Numba being skipped in the test environment.

**Verdict: `reject`**
