# Independent Gemini Review: Goal3572 Grouped-i64 Fastpath

**Date**: 2026-06-06
**Verdict**: accept-with-boundary

## Findings

No defects were identified during this review. The implementation aligns with the stated goals and adheres to established boundaries.

## Verification

This review is a grounded audit based on the following files:
- `docs/handoff/HANDOFF_EXTERNAL_REVIEW_GOAL3572_GROUPED_I64_FASTPATH_2026-06-06.md`
- `docs/reports/goal3572_grouped_i64_full_reduction_fastpath_2026-06-06.md`
- `docs/reports/goal3572_grouped_i64_full_reduction_fastpath_preserve_long_a5000/summary.json`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `scripts/goal3572_grouped_i64_full_reduction_fastpath_probe.py`
- `tests/goal3572_grouped_i64_full_reduction_fastpath_a5000_test.py`
- `tests/goal3572_grouped_i64_small_group_full_reduction_fastpath_test.py`
- `tests/goal3564_grouped_i64_small_group_sum_fastpath_test.py`

### 1. App-Agnostic Boundary

The implementation successfully maintains an app-agnostic boundary.
- The handoff document (`docs/handoff/HANDOFF_EXTERNAL_REVIEW_GOAL3572_GROUPED_I64_FASTPATH_2026-06-06.md`) and the report (`docs/reports/goal3572_grouped_i64_full_reduction_fastpath_2026-06-06.md`) explicitly state the goal is an app-agnostic grouped-i64 primitive, with all RayDB/database/app semantics remaining outside the native engine.
- Examination of `src/native/optix/rtdl_optix_workloads.cpp` and the relevant test files (`tests/goal3572_grouped_i64_small_group_full_reduction_fastpath_test.py`, `tests/goal3564_grouped_i64_small_group_sum_fastpath_test.py`) confirms no RayDB/database specific branching or vocabulary within the native engine's kernel logic or selection mechanisms.

### 2. Split-Kernel Design

The split-kernel design is verified as implemented:
- The original sum/sum_count path is preserved under `device_column_grouped_i64_small_group_kernel`.
- The new count/min/max/stats structural path is implemented under `device_column_grouped_i64_small_group_reduction_kernel`.
- This split is confirmed by the kernel definitions and selection logic in `src/native/optix/rtdl_optix_workloads.cpp`, as well as specific assertions in `tests/goal3572_grouped_i64_small_group_full_reduction_fastpath_test.py`.

### 3. A5000 Artifact Numbers

The A5000 artifact numbers (`docs/reports/goal3572_grouped_i64_full_reduction_fastpath_preserve_long_a5000/summary.json`) have been verified against the reported values:
- **baseline commit**: `f5090057`
- **candidate commit**: `bfcb943c`
- **dirty**: `false`
- **copies**: `120000`
- **warmup**: `3`
- **repeat**: `5000`
- **trials**: `5`
- **all_modes_ok**: `true`
- **geomean speedup**: `1.157044x`
- **median speedup**: `1.245297x`
- **Per-mode speedups**:
    - `count`: `1.324430x`
    - `min`: `1.245297x`
    - `max`: `1.263298x`
    - `avg_as_sum_count`: `1.007569x`
    - `sum`: `0.987797x`
These numbers are consistent with the assertions in `tests/goal3572_grouped_i64_full_reduction_fastpath_a5000_test.py`.

### 4. Sum Preservation and Speedup Claim

The `sum` operation's speedup of `0.987797x` is explicitly noted as near-parity. It is correctly not claimed as a new speedup by the report or handoff, aligning with the intent to preserve the existing hot path rather than optimize it further in this goal.

### 5. Stats Coverage

The `stats` operation is structurally covered by the native engine, meaning the code path exists, but it is not measured by the RayDB-style probe (`scripts/goal3572_grouped_i64_full_reduction_fastpath_probe.py`). Therefore, no performance claim for `stats` is authorized or made.

### 6. Report Claim Boundaries

The report (`docs/reports/goal3572_grouped_i64_full_reduction_fastpath_2026-06-06.md`) and its underlying artifact (`summary.json`) correctly adhere to the specified claim boundaries. There are no unauthorized claims regarding:
- release or tag action
- public speedup claims
- whole-app acceleration claims
- broad RT-core speedup claims
- true zero-copy claims
- paper reproduction claims
- package-install claims

### Residual Risks / Test Gaps

- The `sum` operation's slightly regressed performance (`0.987797x`) compared to baseline, while within an acceptable near-parity band, indicates that future optimizations should carefully consider potential side effects on existing hot paths.
- The `stats` operation is structurally supported but lacks specific performance measurements from the provided probe. This is an acknowledged boundary, but future work might include a probe that can validate its performance if a speedup claim is ever intended.
