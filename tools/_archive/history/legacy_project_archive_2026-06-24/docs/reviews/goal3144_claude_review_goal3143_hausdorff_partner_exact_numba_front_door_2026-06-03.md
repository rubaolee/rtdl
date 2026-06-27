# Goal3144: Independent Claude Review of Goal3143
## Hausdorff `partner_exact` Numba Front Door

Date: 2026-06-03  
Reviewer: Claude Sonnet 4.6 (independent review, not present during Goal3143 implementation)  
Verdict: **accept-with-boundary**

---

## Files Reviewed

- `src/rtdsl/partner_adapters.py` (sections: `point_rows_to_partner_columns`, `_numba_runtime_for_point_columns`, `_directed_hausdorff_2d_numba_partner_columns`, `directed_hausdorff_2d_partner_columns`, `group_argmin_then_global_argmax_partner_columns`)
- `src/rtdsl/numba_partner_continuation.py` (full file)
- `src/rtdsl/__init__.py` (full file)
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py` (full file)
- `scripts/goal3143_hausdorff_partner_exact_numba_pod_probe.py` (full file)
- `tests/goal3143_hausdorff_partner_exact_numba_front_door_test.py` (full file)
- `docs/reports/goal3143_hausdorff_partner_exact_numba_front_door_2026-06-03.md`
- `docs/reports/goal3143_pod_artifacts/hausdorff_partner_exact_numba_pod_probe_2026-06-03.json`

---

## Findings by Severity

### Medium — `v2_8_partner_continuation_operations` always declares `sqrt_f64` regardless of execution

**Location:** `partner_adapters.py:3350-3355`

```python
"v2_8_partner_continuation_operations": (
    score_operation,
    "grouped_argmin_f64",
    "grouped_argmax_f64",
    "sqrt_f64",  # always present even when materialize_nearest_distances=False
),
```

When `materialize_nearest_distances=False` (the app path), `run_numba_sqrt_f64` is not called, but `"sqrt_f64"` is still listed in `v2_8_partner_continuation_operations`. The correct execution indicator is `nearest_distance_column_materialized: false` (also present in the metadata). The test at line 119 checks that `"sqrt_f64"` is in the operations list when CUDA is available and also that `nearest_distance_column_materialized` is false for the app invocation—these two signals conflict for an auditor relying on the operations list alone.

**This is a documentation-clarity concern, not a correctness bug.** `nearest_distance_column_materialized` is the authoritative field. However, if `v2_8_partner_continuation_operations` is used as an execution record by future reviewers, it will mislead. Acceptable for current internal use; should be addressed before any wider review surfaces.

**Required before next step:** Either document that `v2_8_partner_continuation_operations` describes the adapter's capability set (not a per-call execution log) or make it conditional on `materialize_nearest_distances`.

---

### Low — Claim-boundary key versioning is inconsistent across artifact rows

**Location:** `docs/reports/goal3143_pod_artifacts/hausdorff_partner_exact_numba_pod_probe_2026-06-03.json`, per-row claim boundaries

The `partner_exact_numba` rows carry `"v2_8_release_authorized": false` while the `partner_numba_block_nearest_exact` rows carry `"v2_6_release_authorized": false`. Both evaluate to false and the top-level `claim_boundary` object is internally consistent (all false). The test at lines 76-77 validates only the top-level object. This does not affect claim enforcement but indicates the old bespoke backend's metadata hasn't been updated to the current version nomenclature.

**Not blocking.**

---

### Low — Single-shot timing methodology; non-monotonic speed ratio should not be cited as evidence

**Location:** `docs/reports/goal3143_hausdorff_partner_exact_numba_front_door_2026-06-03.md`, timing table

The probe script performs one warmup per mode and then one timed measurement per (mode × copies) combination. The report table shows:

| size | `partner_exact_numba` | old bespoke | ratio |
|---|---|---|---|
| 1024×1024 | 0.013123 s | 0.011802 s | 1.11× slower |
| 4096×4096 | 0.024319 s | 0.022515 s | 1.08× slower |
| 8192×8192 | 0.044065 s | 0.086373 s | **0.51×** (2× faster) |

The reversal at 8192×8192 is plausible (kernel cache from Goal3142 benefits the new path at large sizes while the old bespoke path's kernel may not be cached the same way), but single-shot observations at these sizes are sensitive to scheduling noise. The timing numbers are acceptable as internal evidence that the new path is competitive, but cannot be cited as a performance claim between the two backends.

The report correctly says "not an RT-core path" and "does not authorize public speedup," so this is informational only.

**Not blocking.** Do not use this table to justify a speedup claim of the new path over the old bespoke backend.

---

### Informational — `point_rows_to_partner_columns` with `partner="numba"` uses `int64` IDs, not `uint32`

**Location:** `partner_adapters.py:1863`

```python
id_dtype = partner["int64"] if partner["name"] == "numba" else partner["uint32"]
```

This is correct and intentional—the Numba pairwise kernels require `target_ids: int64`. The test at line 100 verifies this. No action needed; documenting for completeness.

---

## Review Question Answers

### Q1: Does `partner_exact + partner="numba"` now use a shared generic front door?

**Yes.** `directed_hausdorff_2d_partner_columns` (`partner_adapters.py:3392`) now dispatches on `partner == "numba"` at line 3409, routing to `_directed_hausdorff_2d_numba_partner_columns`. The Hausdorff app's `_run_partner_exact_directed` function calls this shared adapter with `partner=partner` for any partner including `"numba"` (app line 286). The argparse choices now include `"numba"` (app line 986). The test confirms the app-level wiring (`choices=("torch", "cupy", "numba")` present in source, line 50).

The old bespoke backends (`partner_numba_witness_exact`, `partner_numba_block_nearest_exact`) remain in the app for backwards compatibility but are no longer the recommended path.

### Q2: Is the implementation app-agnostic at the engine/runtime layer?

**Yes.** `_directed_hausdorff_2d_numba_partner_columns` (`partner_adapters.py:3272-3389`) composes only:

1. `pairwise_l2_sq_block_nearest_rows_2d_partner_columns` (or the dense variant) — generic typed-column score-row generator
2. `group_argmin_then_global_argmax_partner_columns` with `partner="numba"` — generic group-reduce continuation
3. Optionally `run_numba_sqrt_f64` — generic elementwise transform

None of these call OptiX traversal. The metadata explicitly carries `"native_engine_row_contract": "not_called_partner_reference_only"` and `"rt_core_speedup_claim_authorized": False`. There is no app-specific logic at the engine layer; the adapter knows only typed CUDA columns.

### Q3: Is the `materialize_nearest_distances` distinction correct?

**Structurally correct with a documentation caveat (see findings above).**

The public adapter default is `materialize_nearest_distances=True` (line 3401), preserving the `nearest_distances` column for rich caller use. The Hausdorff app hardcodes `materialize_nearest_distances=partner != "numba"` (app line 290), which is `False` for Numba — correct because the scalar app derives the final Hausdorff distance from `math.sqrt(winner_score)` at the witness level, not from the nearest-distance column.

The test (line 133) confirms `nearest_distance_column_materialized` is False in the app path. The test (line 117-118) confirms it is True in the adapter-level executable test that calls the public API directly.

The caveat: `v2_8_partner_continuation_operations` always includes `"sqrt_f64"` as a static capability declaration even when it does not execute. See finding above.

### Q4: Do the tests and RTX 4000 Ada artifact support the claimed correctness and warmed timing observations?

**Yes for correctness. Timing evidence is single-shot and should not be cited as a performance claim.**

Artifact (`hausdorff_partner_exact_numba_pod_probe_2026-06-03.json`):
- `all_match: true`
- All 6 rows: `matches_oracle: true`, `rt_core_accelerated: false`, `host_score_row_materialization_used: false`, `score_rows_generated_on_partner_device: true`
- GPU: `NVIDIA RTX 4000 Ada Generation`, Python 3.12.3
- Commit `3b0bfbd9` matches the Goal3143 commit in git history

The test suite covers: source presence checks, descriptor correctness, report and artifact claim-boundary validation, adapter-level executable validation (skipped without CUDA), and app-level executable validation (skipped without CUDA).

The test correctly skips executable tests when `rt.numba_partner_available()` returns False, which is the right behavior for non-CUDA environments.

### Q5: Are all public/release/speedup/RT-core/zero-copy claim boundaries still blocked?

**Yes, at all levels.**

The metadata produced by `_directed_hausdorff_2d_numba_partner_columns` explicitly carries:
- `rt_core_speedup_claim_authorized: False`
- `v2_0_release_authorized: False`
- `v2_5_release_authorized: False`
- `v2_8_release_authorized: False`
- `whole_app_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `direct_device_handoff_authorized: False`

The `run_app` function in the Hausdorff app (lines 606-613) carries:
- `v2_8_release_authorized: False`
- `public_speedup_claim_authorized: False`
- `numba_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `whole_app_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`

The probe script artifact (top-level `claim_boundary`) also has all six flags false. The test validates this at lines 76-77.

---

## Verdict: `accept-with-boundary`

Goal3143 is accepted for internal preview. The shared generic front door is correctly implemented, app-agnostic, and validated on RTX 4000 Ada hardware. Correctness is confirmed. All claim boundaries are blocked.

**Required before next step:**

1. Clarify (in code comment or metadata description) whether `v2_8_partner_continuation_operations` is a capability declaration or a per-call execution log. The current behavior (always includes `sqrt_f64`) is unambiguous if documented; otherwise rename the field or make it conditional.

**Not required but recommended:**

2. If the non-monotonic timing ratio (new path 2× faster at 8192×8192) is ever cited in a future review, add a note to the report explaining the likely cause (Goal3142 kernel caching) and the single-shot nature of the measurement.

**This review does not authorize:**

- v2.8 release
- Public speedup claim for Numba vs. any other path
- RT-core or true-zero-copy claims
- Whole-app speedup claims
