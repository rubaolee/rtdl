# Claude Review: Goal4323 Dense Group Contract Metadata

Date: 2026-06-11
Reviewer: Claude (external read-only review)
Target: Goal4323 — dense zero-based group-id contract helper and shared metadata threading

## Verdict

**reject**

The contract helper and the non-Numba front-door threading are correct. However, the direct Numba grouped argmin/argmax runner path (`_run_numba_grouped_arg_reduce_f64`) references a variable `group_contract_metadata` that is never assigned within the function, producing a guaranteed `NameError` at CUDA runtime. The Numba CUDA test that would have caught this was skipped in the Windows validation run. The stated goal of threading dense contract metadata into the Numba direct runner is not achieved.

---

## Check 1 — `make_dense_zero_based_group_id_contract` is generic and validation rejects invalid dense metadata

**Pass.**

`partner_column_contracts.py:93–108` defines a factory with only generic parameters (`operation`, `group_count`, `row_count`, `validation_mode`). No app-specific or domain-specific terms appear. The returned dataclass always sets `layout=GROUP_LAYOUT_DENSE_ZERO_BASED` and `rows_per_group=None`.

`validate_group_id_contract` at lines 111–139 correctly enforces:

- Unknown `layout` strings are rejected.
- `group_count < 0` or `row_count < 0` are rejected.
- Dense zero-based contracts with `rows_per_group is not None` are rejected with the message "dense zero-based group ids do not use rows_per_group".
- Non-empty dense contracts (`row_count > 0`) with `group_count <= 0` are rejected with "non-empty dense zero-based group ids require group_count > 0".

The test `test_dense_zero_based_contract_helper_accepts_and_rejects` exercises both the accept and the `group_count=0, row_count=1` rejection path. The validation logic is accurate and does not require CUDA.

---

## Check 2 — Non-Numba front doors emit shared dense group-id contract metadata

**Pass.**

`partner_adapters.py` adds a private helper `_dense_group_id_contract_metadata(...)` at lines 2659–2673 that calls `make_dense_zero_based_group_id_contract` + `require_group_id_contract`. This helper is thin, generic, and contains no app-shaped logic.

All three claimed front doors are wired correctly:

- **`grouped_argmin_f64_partner_columns`** (adapter line 2831): calls `_dense_group_id_contract_metadata(operation="grouped_argmin_f64", ...)` and spreads `**group_contract_metadata` into the `_generic_partner_front_door_metadata` extra dict.

- **`grouped_argmax_f64_partner_columns`** (adapter line 2909): identical pattern with `operation="grouped_argmax_f64"`.

- **`grouped_topk_f64_partner_columns`** (adapter lines 3152–3161): for non-Numba partners calls `_dense_group_id_contract_metadata(operation="grouped_topk_f64", ...)`. The Numba sub-path correctly uses `make_equal_contiguous_group_id_contract` instead (topk requires contiguous segments, not dense zero-based), which is the right decision.

The `validation_mode` values are correctly partitioned: `"numba_device_runtime_validation"` for the Numba code path, `"torch_host_group_id_bounds_check"` for Torch/Triton.

---

## Check 3 — Direct Numba grouped argmin/argmax runner emits shared dense group-id contract metadata when executed

**Fail — NameError defect.**

`_run_numba_grouped_arg_reduce_f64` (numba_partner_continuation.py:1287–1403) is the private implementation shared by `run_numba_grouped_argmin_f64` and `run_numba_grouped_argmax_f64`. At line 1401 its return assembles:

```python
extra_metadata={
    "tie_break": tie_break,
    "host_present_group_compaction_used": compact_present_groups,
    "nan_validation_host_sync_used": validate_nan_scores,
    **group_contract_metadata,   # <-- line 1401
},
```

`group_contract_metadata` is **never assigned anywhere within the function body** (lines 1303–1382 can be read in full; no assignment exists). Executing this path will unconditionally raise:

```
NameError: name 'group_contract_metadata' is not defined
```

The missing assignment would need to be something like:

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

placed between the `_validate_group_run_shape` call (line 1311) and the `cuda.synchronize()` at line 1320. The function already receives `operation`, `group_count`, `validate_group_ids`, and `row_count` is returned by `_validate_group_run_shape` — all the needed values are in scope; the assignment was simply not written.

The test `test_numba_argmin_emits_dense_contract_metadata_when_cuda_available` would catch this defect, but the Windows validation run produced "2 expected optional Numba CUDA skips." The non-CUDA test suite does not execute `_run_numba_grouped_arg_reduce_f64` at all.

---

## Check 4 — Public exports are coherent and do not create an app-shaped API

**Pass.**

`__init__.py` imports and `__all__` (lines 2154–2166) add:

```
GROUP_LAYOUT_DENSE_ZERO_BASED
make_dense_zero_based_group_id_contract
make_equal_contiguous_group_id_contract
require_group_id_contract
validate_group_id_contract
validate_partner_claim_boundary
```

All are generic contract-layer symbols with no application-domain names, no specific geometry or RT terms. The private `_dense_group_id_contract_metadata` helper in `partner_adapters.py` is correctly kept private (prefixed `_`). No app-shaped surface is introduced.

---

## Check 5 — Report is honest about scope

**Pass.**

The report (`docs/reports/goal4323_dense_group_contract_metadata_2026-06-11.md`) explicitly disclaims:

- No implementation-body split out of `partner_adapters.py`
- No algorithm change
- No new partner
- No release action authorized
- No public speedup claim authorized
- No broad RT-core claim authorized
- No true-zero-copy claim authorized
- No automatic partner selection authorized
- No app-specific native-engine logic authorized

The report's self-verdict is "accept-with-boundary" and its description ("contract hardening") accurately characterises what the non-Numba portion of the PR achieves. The report does not misrepresent the Numba runner change — it just overstates its completion status, because the NameError was not detected without CUDA.

---

## Summary of Defects

| # | File | Lines | Severity | Description |
|---|------|--------|----------|-------------|
| 1 | `numba_partner_continuation.py` | 1401 | **Blocking** | `_run_numba_grouped_arg_reduce_f64` spreads `**group_contract_metadata` but the variable is never assigned; `NameError` at CUDA runtime for both argmin and argmax Numba direct paths |

### Secondary observation (possibly pre-existing, not claimed by Goal4323)

`run_numba_grouped_vector_sum_f64x2` (lines 406–417) assigns `group_contract_metadata` using `operation=operation` where `operation` is not a parameter of that function (also a `NameError` at CUDA runtime), and the assignment result is never spread into the return. The Goal4323 report does not list `run_numba_grouped_vector_sum_f64x2` as a changed function. If it was introduced by an earlier goal, it should be fixed separately.

---

## Recommended Fix

In `numba_partner_continuation.py`, inside `_run_numba_grouped_arg_reduce_f64`, add the missing assignment after the `_validate_group_run_shape` call and before `cuda.synchronize()`:

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

After that fix, `test_numba_argmin_emits_dense_contract_metadata_when_cuda_available` should pass on a CUDA-capable machine and the contract metadata claims made by the report would become accurate.
