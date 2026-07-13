# Goal5420 - X-HD Figure 5 Level-B Matrix Consolidation Decision

## Verdict

```text
completed_figure5_level_b_graphics_matrix_consolidated__bounded_geo_packet_next__no_ratio
```

Goal5420 consolidates the Goal5419 same-POD graphics matrix and decides the
next bounded X-HD work item.  It does not run POD commands, does not add a new
performance route, and does not reopen the explicit `-lb` row-identity line.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5420_figure5_level_b_matrix_consolidation_decision.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.goal5420.figure5_level_b_matrix_consolidation_decision.v1
status = figure5_level_b_graphics_matrix_consolidated__bounded_geo_packet_next__no_ratio
matched = true
```

## Consolidated Graphics Matrix

Goal5419 already executed the three value-matched Level-B graphics cases on the
same POD:

```text
dragon_happy
thai_happy_scaled
thai_asian_scaled
```

The matrix contains:

```text
graphics_case_count = 3
route_result_count = 6
same_pod_execution_claimed = true
matched = true
```

All three author reruns match the paper-branch author-log scalar within
`1e-6`.  All six RTDL route rows match the same-POD author rerun scalar within
`1e-6`.

Every graphics RTDL row carries the required preprocessing contract:

```text
required_rtdl_preprocessing = ["translate_each_input_to_min_bound"]
```

This remains mandatory.  A prior Dragon/HappyBuddha smoke without this
preprocessing returned the wrong scalar HDResult.

## Decision

Goal5420 makes the following decision:

```text
graphics_matrix_ready_for_strict_review = true
bounded_geo_matrix_packet_authorized_next = true
bounded_geo_matrix_execution_authorized_now = false
recommended_next_goal = Goal5421_bounded_geo_same_pod_packet_plan
continue_route_micro_optimization_by_default = false
return_to_exact_dataset_work_without_geo_packet = false
```

Interpretation:

- The graphics matrix is ready to send for strict review.
- The next work item should be a bounded-geo same-POD packet plan, not another
  route micro-optimization.
- Geo execution is not authorized by this goal; the next goal should first
  define the packet and denominator boundary.
- Exact dataset work remains important, but the immediate next step is to
  package the already-known bounded geo candidates cleanly.

## Bounded Geo Candidates Authorized For Planning

Goal5420 authorizes planning, not execution, for two bounded geo rows:

| Case | Identity Level | Prior Author HDResult | Prior RTDL HDResult | Abs Diff | Tolerance | Point Counts | Route Family |
|---|---|---:|---:|---:|---:|---:|---|
| `county_zcta_bounded` | `level_b_bounded_geo_fixture` | 65.44752502441406 | 65.44751976280666 | 5.2616073986655465e-06 | 1e-5 | 38034 / 50272 | `directed_max_of_nearest_distance_2d_partner_columns_triton` |
| `water_bg_bounded` | `level_b_bounded_geo_fixture` | 72.38665008544922 | 72.38664516014835 | 4.925300871150284e-06 | 1e-5 | 124 / 894 | `directed_max_of_nearest_distance_2d_partner_columns_triton` |

These rows are intentionally kept out of the graphics packet because they use a
different runner family: generic partner/Triton column route rather than the
graphics `hd_exec`-compatible packet.

## Claim Boundary

Goal5420 authorizes none of the following:

```text
figure5_reproduction_claimed = false
exact_paper_dataset_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
performance_ratio_claimed = false
bounded_geo_execution_claimed = false
route_micro_optimization_goal_authorized = false
explicit_lb_reopened = false
```

No author-vs-RTDL performance ratio is authorized.  Author `Running.AvgTime`,
author process wall, RTDL route wall, RTDL process wall, and RTDL input-load
time remain separate denominators.

## Why Not Continue Route Micro-Optimization By Default?

The immediate blocker is not a missing graphics timing column.  It is evidence
coverage and denominator discipline:

- the three graphics rows are already executed on the same POD and scalar-match;
- the bounded geo rows are known but use a separate runner family and need their
  own packet;
- exact paper datasets are still unavailable;
- explicit `-lb` remains fail-closed under the current RTDL execution model.

Continuing route micro-engineering now would repeat the drift called out by the
midterm review: optimizing implementation details while the paper-level
blockers are dataset identity, figure denominator alignment, and coverage.

## Validation

Focused validation:

```text
$env:PYTHONPATH='src'; py -m unittest tests.goal5420_figure5_level_b_matrix_consolidation_decision_test tests.goal5419_figure5_level_b_same_pod_graphics_matrix_test tests.goal5418_figure5_level_b_same_pod_matrix_readiness_test tests.goal5417_figure5_level_b_same_pod_matrix_plan_test tests.goal5416_full_reproduction_priority_refresh_test
```

Result:

```text
Ran 26 tests OK
```

The builder was also compiled, and the generated JSON passed `json.tool`.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5420_figure5_level_b_matrix_consolidation_decision.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5420_figure5_level_b_matrix_consolidation_decision.json
tests/goal5420_figure5_level_b_matrix_consolidation_decision_test.py
history/internal_docs/goal5420_xhd_figure5_level_b_matrix_consolidation_decision_2026-07-10.md
history/internal_docs/call_for_review_goal5420_xhd_figure5_level_b_matrix_consolidation_decision_2026-07-10.md
```

## Next Recommended Goal

```text
Goal5421_bounded_geo_same_pod_packet_plan
```

Goal5421 should define a bounded geo same-POD packet for the two known geo
fixtures, specify author/RTDL commands, keep the partner/Triton route family
separate from the graphics packet, and preserve the same claim boundary:

```text
no exact dataset claim
no Figure 5 claim
no author-vs-RTDL ratio
no explicit -lb reopening
no route micro-optimization by default
```
