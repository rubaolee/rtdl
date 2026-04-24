# Goal880 External Review — ANN Candidate Threshold RT-Core Sub-Path

Date: 2026-04-24  
Reviewer: Claude (external review, read-only)  
Verdict: **ACCEPT**

---

## Files Reviewed

- `examples/rtdl_ann_candidate_app.py`
- `src/rtdsl/app_support_matrix.py`
- `tests/goal880_ann_candidate_threshold_rt_core_subpath_test.py`
- `docs/reports/goal880_ann_candidate_threshold_rt_core_subpath_2026-04-24.md`

---

## Summary of Changes

Goal880 adds a `candidate_threshold_prepared` mode to the ANN candidate-search
app. Under this mode, `prepare_optix_fixed_radius_count_threshold_2d` is used to
answer one bounded question: does every query point have at least one
Python-selected candidate within the acceptance radius? The existing default
`rows` path (CUDA-through-OptiX KNN rows) is untouched.

The three matrix entries for `ann_candidate_search` are updated in lockstep:

| Matrix | Before | After |
|---|---|---|
| Performance class | `CUDA_THROUGH_OPTIX` | `OPTIX_TRAVERSAL_PREPARED_SUMMARY` |
| Benchmark readiness | `EXCLUDE_FROM_RTX_APP_BENCHMARK` | `NEEDS_REAL_RTX_ARTIFACT` |
| RT-core maturity | `NEEDS_RT_CORE_REDESIGN` | `RT_CORE_PARTIAL_READY` |

---

## Correctness

### Oracle math

For `copies=1`, `candidate_radius=0.2`, the three candidate points are
`(0.00, 0.00)`, `(5.00, 5.00)`, `(10.00, 0.00)` and the three queries are:

- id=1: (0.05, 0.00) → dist to (0.00, 0.00) = 0.05 ≤ 0.2 ✓  
- id=2: (5.18, 5.00) → dist to (5.00, 5.00) = 0.18 ≤ 0.2 ✓  
- id=3: (10.10, 0.00) → dist to (10.00, 0.00) = 0.10 ≤ 0.2 ✓  

All queries are covered at the default radius. The test mock sets
`threshold_reached=1` for every query, so `candidate_threshold["within_candidate_radius"]`
and `oracle_candidate_threshold["within_candidate_radius"]` both return `True`.
`matches_oracle=True` follows. Arithmetic is sound.

### Missing-row test (`test_threshold_rows_missing_queries_are_uncovered`)

Providing only query_id=1 with threshold_reached=1 causes `by_query.get(2,{})` and
`by_query.get(3,{})` to return `{"threshold_reached": 0}` (via default), so
`uncovered=[2, 3]`. The assertion `[2, 3]` is correct.

### `_enforce_rt_core_requirement` logic change

Old: always raised `RuntimeError` when `backend=optix` and `require_rt_core=True`.  
New: raises only when `optix_summary_mode != "candidate_threshold_prepared"`.

This is the correct design: `--require-rt-core` is now a guard that enforces the
traversal-backed path, not a hard "never allowed" block. The test
`test_require_rt_core_rejects_default_knn_rows` verifies the default `rows` mode
still rejects the flag. Consistent with the hausdorff pattern (Goal879).

### No pollution of the default path

The `candidate_threshold_prepared` branch returns early before `_run_rows` is
called. The base_payload branch (default `rows` mode) never sets
`rt_core_accelerated`, so no false RT-core claim propagates through the default
path.

---

## Boundary Preservation

The payload for the new mode carries three explicit boundary signals:

1. `rtdl_role` — names it a "bounded ANN candidate-coverage decision" only.
2. `boundary` — states "not a full ANN index, not nearest-neighbor ranking, not a
   recall/latency optimizer."
3. `optix_performance.note` — "candidate-coverage decisions only."

The benchmark readiness gate `NEEDS_REAL_RTX_ARTIFACT` blocks any cloud
performance claim until a real RTX artifact, same-semantics baselines, and a
phase profiler are produced. This matches the gates already in place for
`service_coverage_gaps`, `event_hotspot_screening`, `hausdorff_distance`, and
`segment_polygon_anyhit_rows`.

The no-full-ANN / no-ranking-speedup boundary is intact.

---

## RTX Claim Gate

`rt_core_accelerated: True` appears in the payload. This is acceptable because:

- The payload boundary field explicitly limits the claim to the threshold
  decision sub-path.
- Benchmark readiness is `NEEDS_REAL_RTX_ARTIFACT` — no cloud speedup claim is
  authorized yet.
- The field is present only when `optix_summary_mode="candidate_threshold_prepared"`
  is explicitly requested by the caller.

No unconditional or default-path RT-core claim is made.

---

## Test Coverage

| Test | What it checks |
|---|---|
| `test_optix_candidate_threshold_mode_uses_prepared_traversal` | prepared API called; correct radius/threshold args; `rt_core_accelerated=True`; oracle match; no `approximate_rows` key; boundary strings present |
| `test_require_rt_core_rejects_default_knn_rows` | default `rows` mode still refuses `--require-rt-core` |
| `test_negative_candidate_radius_rejected` | input validation |
| `test_threshold_rows_missing_queries_are_uncovered` | row-to-coverage logic with partial coverage |

Coverage is adequate for the scope of the change. The existing contract tests
(`goal690`, `goal705`, `goal803`) catch any accidental regression in the matrix
values.

---

## Minor Observations (non-blocking)

- `_PreparedCandidateThreshold.__exit__` returns `None` explicitly rather than
  `False`. Both correctly signal "do not suppress exceptions." No issue.
- `matches_oracle` uses list equality on `uncovered_query_ids`. List `==` in
  Python is element-wise and order-sensitive. Since both sides iterate
  `query_points` in the same order this is correct, but a reviewer should note
  the implicit order dependency.
- `candidate_radius < 0` is validated; `candidate_radius == 0` is permitted
  (degenerate but not harmful — every query must have a candidate at distance 0).

---

## Required Fixes

None.

---

## Verdict

**ACCEPT**

The change correctly scopes a prepared OptiX fixed-radius threshold traversal to
the ANN candidate-coverage decision only. It follows the established pattern for
`OPTIX_TRAVERSAL_PREPARED_SUMMARY` apps, preserves the no-full-ANN boundary,
gates any RTX claim on a future real-artifact review, and is backed by focused
unit tests that cover the new path, the validation, and the coverage-row logic.
