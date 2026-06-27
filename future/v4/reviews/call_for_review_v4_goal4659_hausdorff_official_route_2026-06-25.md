# Call For Review: V4 Goal4659 Hausdorff Official V4 Route

Date: 2026-06-25

Requested verdict labels:

- `accept_goal4659_app_route_progress_not_release`
- `accept_with_required_fixes`
- `reject_goal4659_route_or_evidence`

## Review Materials

- Report:
  `future/v4/v4_goal4659_hausdorff_official_v4_route_evidence_2026-06-25.md`
- Machine summary:
  `future/v4/evidence/v4_goal4659_hausdorff_v4_route_20260625/summary.json`
- Code:
  - `src/rtdsl/partner_adapters.py`
  - `examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
- Tests:
  - `tests/v4_goal4659_hausdorff_official_route_test.py`

## Context

Goal4659 tries to move `hausdorff_xhd` from partial operator coverage toward a
real V4 app route. It adds a generic Torch
`global_argmax_u32_f64_partner_columns` continuation and uses the official V4
point-group nearest-witness front door inside the Hausdorff
`optix_device_max_nearest` route.

This is not a release authorization request.

## Questions For Reviewer

1. Is the added Torch `global_argmax_u32_f64_partner_columns` a generic
   continuation rather than a Hausdorff-specific app kernel?
2. Does the Hausdorff route actually use the official V4
   `v4_point_group_nearest_witness_2d_device_arrays` surface for
   `partner="torch"`?
3. Is the coordinate-normalized chunk mode generic V4 route-strengthening
   work, not a Hausdorff-specific native kernel?
4. Is the evidence interpretation honest: real app-route progress, hot-path win
   at smaller correctness-passing scales, 1M exactness repaired by coordinate
   normalization, but no broad V4 speed claim and no unrestricted exact
   Hausdorff claim?
5. Is the 1,048,576 points/side evidence correctly treated as a correctness
   repair rather than hidden as a speed win?
6. Are the next blockers correct: prepare overhead, deciding whether
   coordinate normalization or higher-precision native distance is the public
   route, and app-level scorecard rerun?

## Non-Authorization To Preserve

This review must not authorize V4 release, broad V4 speedup wording,
all-benchmark speedup wording, unrestricted exact Hausdorff claims, public
true-zero-copy claims, Tier-3 callback support, C ABI, embedding, non-Python host
support, or app-specific native kernels.
