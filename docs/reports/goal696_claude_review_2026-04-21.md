# Goal 696 Linux Validation — Claude Review

**Date:** 2026-04-21
**Reviewer:** Claude (claude-sonnet-4-6)
**Artifacts reviewed:**
- `docs/reports/goal696_optix_fixed_radius_summary_linux_validation_2026-04-21.md`
- `docs/reports/goal696_optix_fixed_radius_summary_linux_validation_2026-04-21.json`
- `tests/goal696_optix_fixed_radius_linux_validation_test.py`

## Verdict

**ACCEPT**

All three honesty criteria are satisfied. The report is internally consistent, the JSON and MD figures agree, the validation test suite passes, and no prohibited claims appear anywhere in the artifacts.

---

## Criterion 1: Linux native build and correctness honestly recorded

**Pass.**

The report records the exact build command, the output library path (`librtdl_optix.so`), and an OptiX version probe (`(9, 0, 0)`), providing a verifiable build trace. Correctness evidence is multi-layered:

- Direct helper (`rtdsl.fixed_radius_count_threshold_2d_optix`): `matches_oracle: true` for both outlier and DBSCAN paths.
- JSON confirms `outlier_summary_matches_oracle: true`, `dbscan_core_flags_match_oracle: true`.
- Neighbor-row materialization is zero in both the MD (`neighbor_row_count: 0`) and JSON (`outlier_neighbor_rows_materialized: 0`, `dbscan_neighbor_rows_materialized: 0`).
- 15 focused tests pass, covering Goal695 new paths, the existing `fixed_radius_neighbors` OptiX row path, and the Goal690 classification guard.
- The `cluster_rows: 0` DBSCAN result is explicitly explained as intentional — summary mode covers the core-flag predicate only, not full cluster expansion. This is honest disclosure, not a hidden failure.

One notable data point: the `outlier_rows_copies_16` case shows a max_sec of 0.4888 s against a median of 0.004079 s, a cold-start outlier likely from CUDA/BVH context init on the first of three iterations. The MD cites only medians (appropriate for a 3-run series), and the JSON retains the full min/max/median, so nothing is concealed.

The disclosure of the aborted 8192-point row-baseline timing run is also appropriately recorded ("stopped because the row-materializing baseline became too expensive for an interactive validation run") and correctly excluded from the result table.

---

## Criterion 2: No RTX speedup claims on GTX 1070

**Pass.**

The GPU boundary is stated four distinct times across the artifacts:

- MD verdict: "bounded whole-call evidence on a GTX 1070, which has no RT cores, so it is not RTX RT-core speedup evidence."
- MD interpretation: "near parity rather than a clear speedup at these scales on GTX 1070."
- MD interpretation: "GTX 1070 has no RT cores and this goal was correctness/build validation, not RTX performance closure."
- JSON `gpu_boundary` field: "GTX 1070 has no RT cores; this validates OptiX traversal correctness and whole-call behavior, not RTX RT-core speedup."
- JSON `conclusion.performance_gate`: `"bounded_near_parity_on_gtx1070"` — explicitly labeled near-parity, not speedup.
- JSON `conclusion.next_required_gate`: "RTX-class hardware phase-split benchmark before any RT-core speedup claim."

The observed timing ratios (summary vs row-path medians: ~10% faster at each scale) are presented only as whole-call evidence on non-RT-core hardware. No RT-core acceleration claim is made or implied anywhere.

---

## Criterion 3: No app classification change

**Pass.**

- MD verdict states "No performance-classification change."
- MD focused tests: "Goal690 classification tests still pass, confirming no premature classification change."
- MD boundary section: "Outlier detection and DBSCAN remain classified as `cuda_through_optix` at the app level until a future RTX-class benchmark proves that the new summary path is faster under phase-split measurement."
- JSON `conclusion.classification_change: false`.
- The validation test suite (`test_linux_validation_json_records_no_classification_change`) asserts `classification_change == false` and passes.
- The focused test command explicitly includes `tests.goal690_optix_performance_classification_test`, confirming the existing classification guard was exercised.

---

## Test Suite Assessment

The three test cases in `goal696_optix_fixed_radius_linux_validation_test.py` directly probe the honesty boundaries rather than re-implementing logic:

- `test_linux_validation_report_preserves_honesty_boundaries` — substring checks for all key honesty phrases in the MD.
- `test_linux_validation_json_records_no_classification_change` — structural checks on commit, build result, oracle booleans, row-materialization counts, and `classification_change`.
- `test_all_timing_cases_preserve_oracle_parity` — asserts ≥12 cases, all `matches_oracle: true`, all positive medians.

All three pass (`Ran 3 tests in 0.000s OK`). The suite is appropriately scoped: it guards the report's integrity claims without over-reaching into live GPU execution.

---

## Summary

| Criterion | Result |
|---|---|
| Linux native build/correctness honestly recorded | Pass |
| No RTX speedup claims on GTX 1070 | Pass |
| No app classification change | Pass |
| MD/JSON numerical consistency | Pass |
| Validation test suite | 3/3 pass |

**ACCEPT.** The artifacts are internally consistent, the honesty boundaries are explicitly stated and tested, and the report makes no hardware claims beyond what GTX 1070 can support.
