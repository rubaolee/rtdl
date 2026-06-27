# Goal4666 Completion Review Debt And No Release Authorization

Date: 2026-06-25

Status: engineering complete, external review debt open

Goal:

`Goal4666 - Hausdorff official CuPy route and focused rerun`

Engineering decision:

`official_cupy_route_productized__large_row_passes_hot_prepare__focused_bar_not_reopened`

## Evidence To Review

- Report:
  `future/v4/v4_goal4666_hausdorff_cupy_official_route_evidence_2026-06-25.md`
- Machine summary:
  `future/v4/evidence/v4_goal4666_hausdorff_cupy_official_20260625/summary.json`
- Raw POD evidence:
  `future/v4/evidence/v4_goal4666_hausdorff_cupy_official_20260625/`
- Code changes:
  - `src/rtdsl/v4_point_group.py`
  - `src/rtdsl/partner_adapters.py`
  - `examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
  - `src/rtdsl/v4_app_route_binding.py`
  - `tests/v4_goal4666_hausdorff_cupy_official_route_test.py`

## Local Validation

Command:

```text
py -m unittest tests.v4_goal4666_hausdorff_cupy_official_route_test tests.v4_goal4665_hausdorff_focused_candidate_test tests.v4_goal4664_next_performance_target_selection_test tests.v4_goal4652_app_route_binding_test tests.v4_goal4660_ranked_summary_candidate_test tests.v4_frontdoor_test tests.v4_scope_gate_test
```

Result:

`36 tests OK`

## External Review Debt

Claude review:

- status: open debt
- reason: Claude weekly-limit status is already known; do not keep probing it.

Antigravity review:

- status: open debt
- reason: not requested synchronously for this engineering step; reviewer can
  inspect the evidence packet above.

Third external seat:

- status: open debt
- reason: no available non-internal reviewer invoked for this step.

## Non-Authorization

This record does not authorize:

- V4 release;
- formal high-performance V4;
- all-app benchmark rerun;
- broad V4 speedup wording;
- whole-app speedup wording;
- public true-zero-copy wording;
- CuPy performance wording beyond the exact Goal4666 measured route;
- app-specific native Hausdorff kernels;
- C ABI, embedding, or non-Python host binding claims.

## Review Questions

External reviewers should answer:

1. Does the code genuinely route Hausdorff `partner="cupy"` through the V4
   point-group session and generic CuPy global-argmax continuation?
2. Is the 262,144 points/side hot/prepare repair real and correctly compared
   against Goal4665 V3 CuPy?
3. Does the 65,536 points/side failure prevent reopening the focused bar?
4. Is the decision label honest, especially the refusal to trigger all-app or
   formal V4 release?
5. Are any app-specific native-kernel or unsupported speed claims leaking into
   docs, tests, or route metadata?
