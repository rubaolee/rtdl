# Goal881 External Review

Date: 2026-04-24  
Reviewer: Claude (claude-sonnet-4-6)  
Scope: uncommitted diff on branch `codex/rtx-cloud-run-2026-04-22`

## Verdict

**ACCEPT**

The implementation is correct, internally consistent, and honestly bounded. All three of the handoff's key questions are satisfied. Minor observations are noted below but none block merge.

---

## Key Question Responses

### 1. Does `--backend optix --optix-summary-mode coverage_threshold_prepared --require-rt-core` honestly use prepared fixed-radius OptiX traversal for only the facility service-coverage decision?

**Yes.** The code path is:

```
run_case("optix", optix_summary_mode="coverage_threshold_prepared")
  → _run_optix_coverage_threshold(case, radius=service_radius)
  → rt.prepare_optix_fixed_radius_count_threshold_2d(depots, max_radius=radius)
  → prepared.run(customers, radius=radius, threshold=1)
  → _coverage_threshold_from_count_rows(...)
```

This is the same `prepare_optix_fixed_radius_count_threshold_2d` primitive used by `service_coverage_gaps` and `event_hotspot_screening`. The sub-path answers a boolean coverage question ("is there at least one depot within `service_radius` for every customer?") using threshold=1. The oracle independently computes the same result via `math.hypot(...) <= radius`, and the payload includes a `matches_oracle` field comparing both `all_customers_covered` and `uncovered_customer_ids`. The semantics are equivalent.

### 2. Is the no-ranked-KNN / no-assignment-speedup boundary preserved?

**Yes.** Two independent guards enforce it:

- `run_case("optix")` without `optix_summary_mode="coverage_threshold_prepared"` unconditionally raises `RuntimeError("...limited to --optix-summary-mode coverage_threshold_prepared")`. This is the real enforcement gate and fires regardless of `--require-rt-core`.
- `_run_rows()` still raises `ValueError("unsupported backend 'optix'")` on the KNN rows path. Goal813 test `test_runtime_helper_still_rejects_optix_backend` keeps this guard tested directly.

The payload's `boundary` field explicitly states "Coverage-threshold decision only; this is not nearest-depot ranking, not K=3 fallback assignment, and not a facility-location optimizer." The notes in `app_support_matrix.py`, the performance matrix, and the RT-core maturity table all carry matching language that the Goal813 boundary tests check phrase-by-phrase.

### 3. Are RTX claims gated on future real-artifact review?

**Yes.** `optix_app_benchmark_readiness` is `NEEDS_REAL_RTX_ARTIFACT` (not `EXCLUDE_FROM_RTX_BENCHMARK`, which was the previous, stronger exclusion). The report (`goal881_facility_coverage_optix_subpath_2026-04-24.md`) explicitly states "no public speedup claim is authorized until a phase profiler, same-semantics baselines, a real RTX artifact, and independent review exist." The RTX gate tests (Goal759, Goal822, Goal824, Goal849, Goal862) are reported passing.

---

## Observations (non-blocking)

### O1: `rt_core_accelerated=True` is hardcoded

The payload unconditionally sets `"rt_core_accelerated": True` when the `coverage_threshold_prepared` path runs. There is no runtime check that the rtdsl layer actually dispatched to GPU hardware vs. a CPU fallback. This is the same pattern used by `service_coverage_gaps` and `event_hotspot_screening`, so it is a codebase-wide convention, not a Goal881-specific defect. It should be understood as a code-path label ("this branch calls the RT-core primitive"), not a hardware confirmation. Worth documenting as a known limitation in a future clean-up but does not block this PR.

### O2: `_enforce_rt_core_requirement` is redundant for the `optix` backend

When `backend == "optix"` and `optix_summary_mode != "coverage_threshold_prepared"` (default "rows"), the enforcement function raises `RuntimeError`. But the unconditional gate at line 194–198 of `run_case` would raise the same `RuntimeError` regardless. The only non-redundant case the function handles is `require_rt_core=True` with a non-optix backend (raises `ValueError`). This is not wrong, but the function's docstring comment would be misleading if someone reads it expecting it to be the primary enforcement mechanism. Not a bug.

### O3: Oracle equivalence assumes the prepared primitive uses Euclidean `<=` semantics

`facility_coverage_oracle` uses `math.hypot(customer.x - depot.x, customer.y - depot.y) <= radius` (inclusive, 2D Euclidean). The prepared traversal uses `threshold=1` at `radius`. The oracle match is implicitly verified by the `matches_oracle` field at runtime, but there are no tests that force a mismatch scenario to confirm the detection works. `test_missing_rows_are_uncovered` tests `_coverage_threshold_from_count_rows` in isolation with missing rows, which covers the structural logic. The end-to-end oracle mismatch path is not tested because the prepared traversal is mocked in Goal881 tests. This is acceptable for a unit-test-level PR but a phase profiler PR should include a harder oracle test.

### O4: No phase profiler or same-semantics baseline in this PR

Explicitly deferred per design and consistent with analogous apps. The `needs_real_rtx_artifact` gate ensures this cannot be claimed as complete.

---

## Test Coverage Assessment

| Test | What it covers | Status |
|---|---|---|
| `goal881` `test_optix_coverage_threshold_mode_uses_prepared_traversal` | Prepared primitive is called; result fields correct; oracle match | Covers happy path via mock |
| `goal881` `test_optix_default_rows_mode_rejected` | Plain `--backend optix` rejected at `run_case` level | ✓ |
| `goal881` `test_require_rt_core_rejects_non_optix_backend` | `require_rt_core=True` + non-optix backend → ValueError | ✓ |
| `goal881` `test_negative_service_radius_rejected` | Input validation | ✓ |
| `goal881` `test_missing_rows_are_uncovered` | Missing-row → uncovered logic in `_coverage_threshold_from_count_rows` | ✓ |
| `goal813` `test_facility_knn_is_only_partially_promoted_to_optix` | Matrix status values after promotion | ✓ |
| `goal813` `test_facility_knn_notes_explain_ranking_gap` | Required boundary phrases present in all notes | ✓ |
| `goal813` `test_public_cli_accepts_only_explicit_optix_coverage_mode` | `run_case("optix")` raises RuntimeError | ✓ (replaces old "invalid choice" test correctly) |
| `goal813` `test_runtime_helper_still_rejects_optix_backend` | `_run_rows("optix")` → ValueError | ✓ (unchanged, still valid) |
| `goal813` `test_doc_records_no_fixed_radius_substitution` | Markdown boundary phrases present | ✓ |

The removal of `redirect_stderr` / `StringIO` imports from goal813 is clean; the old test checked argparse rejection which no longer applies since `optix` is now a valid `--backend` choice.

---

## Summary

Goal881 correctly narrows the new OptiX surface to the service-coverage decision sub-problem, blocks all other OptiX entry points, carries honest boundary language through every matrix and test, and gates any RTX speedup claim on future artifact review. The implementation follows established codebase patterns. No source-level fixes required.
