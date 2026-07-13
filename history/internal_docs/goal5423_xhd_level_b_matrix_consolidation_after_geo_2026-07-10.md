# Goal5423 - X-HD Level-B Matrix Consolidation After Bounded Geo

## Verdict

```text
completed_level_b_same_pod_matrix_consolidated_after_geo__review_node__no_ratio
```

Goal5423 consolidates the current same-POD Level-B evidence after Goal5419
graphics execution and Goal5422 bounded-geo execution.

This is a review node.  It does not run POD commands, does not add a new route,
does not reopen explicit `-lb`, and does not claim Figure 5 reproduction.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5423_level_b_matrix_consolidation_after_geo.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.goal5423.level_b_matrix_consolidation_after_geo.v1
status = level_b_same_pod_matrix_consolidated_after_geo__review_node__no_ratio
matched = true
```

Coverage:

```text
graphics_case_count = 3
graphics_route_result_count = 6
bounded_geo_case_count = 2
bounded_geo_route_result_count = 2
total_case_count = 5
```

## Consolidated Evidence

### Graphics Rows

The three graphics rows come from Goal5419:

| Case | Identity Level | Author HDResult | Author AvgTime ms | Author process wall s | Routes | Scalar-only route | Exact-witness route |
|---|---|---:|---:|---:|---:|---|---|
| `dragon_happy` | `level_b_same_source_public_graphics` | 0.12572988867759705 | 8.128 | 1.934 | 2 | `cell-mbr-fast-scalar` | `cell-mbr-exact-witness` |
| `thai_happy_scaled` | `level_b_same_source_public_graphics` | 0.21912431716918945 | 26.817 | 2.345 | 2 | `cell-mbr-fast-scalar` | `cell-mbr-exact-witness` |
| `thai_asian_scaled` | `level_b_same_source_public_graphics` | 0.28763842582702637 | 19.281 | 2.437 | 2 | `cell-mbr-fast-scalar` | `cell-mbr-exact-witness` |

All graphics RTDL routes match same-POD author reruns.  All author reruns match
the paper-branch author-log scalar within tolerance.  The inputs are still
Level-B same-source public graphics candidates, not exact paper input bytes.

### Bounded Geo Rows

The two bounded geo rows come from Goal5422:

| Case | Identity Level | Author HDResult | RTDL HDResult | Abs Diff | Tolerance | Author AvgTime ms | RTDL route s | RTDL total s |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `county_zcta_bounded` | `level_b_bounded_geo_fixture` | 65.44752502441406 | 65.44751976280666 | 5.2616073986655465e-06 | 1e-5 | 6.506 | 0.639 | 3.675 |
| `water_bg_bounded` | `level_b_bounded_geo_fixture` | 72.38665008544922 | 72.38664516014835 | 4.925300871150284e-06 | 1e-5 | 4.423 | 0.536 | 2.089 |

Both geo rows use:

```text
route = directed_max_of_nearest_distance_2d_partner_columns
partner = triton
triton_strategy = dense_point_nearest_tiled
per_source_witness_exact = true
```

These are bounded ArcGIS fixtures and generic partner-route evidence.  They are
not exact geo paper inputs and not geo Figure 5 reproduction.

## Claim Boundary

Authorized:

```text
level_b_same_pod_scalar_matrix_claimed = true
```

Not authorized:

```text
figure5_reproduction_claimed = false
full_figure5_matrix_claimed = false
exact_paper_dataset_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
performance_ratio_claimed = false
author_rt_core_algorithm_equivalence_claimed = false
explicit_lb_reopened = false
route_micro_optimization_goal_authorized = false
```

## Stop-Loss Gate G-1

Goal5423 mentions explicit `-lb` only as a stopped line.  It does not authorize
row identity, hash parity, offload-stream parity, namespace reconciliation, or
any app-artifact parity work.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: generic_directed_max_of_nearest_distance_2d / Goal5128 facility-service-radius consumer family
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

G-1 decision:

```text
PASS: this consolidation reports bounded scalar evidence using generic routes and does not start app-artifact parity work.
```

## Remaining Blockers

Goal5423 keeps four blockers visible:

| Blocker | Impact |
|---|---|
| `exact_paper_dataset_files_or_hashes_missing` | prevents exact paper dataset and full Figure 5 reproduction claims |
| `figures_5_to_11_denominators_not_aligned` | prevents author-vs-RTDL performance ratios |
| `explicit_lb_row_identity_fail_closed` | prevents Figure 7 load-balance implementation-artifact parity line |
| `fast_scalar_routes_are_scalar_only_when_per_source_witness_exact_false` | prevents exact per-source witness claims for fast-scalar rows |

## Next Recommendation

Goal5423 recommends a strict review packet or a return to exact dataset
acquisition / denominator work, not another route micro-optimization:

```text
strict_review_packet = true
route_micro_optimization = false
explicit_lb = false
preferred_next_goal = Goal5424_strict_review_packet_for_5419_5423_or_return_to_exact_dataset_acquisition
```

## Validation

Commands:

```text
$env:PYTHONPATH='src'
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5423_level_b_matrix_consolidation_after_geo.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5423_level_b_matrix_consolidation_after_geo.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5421_xhd_bounded_geo_same_pod_packet_plan_2026-07-10.md history/internal_docs/goal5422_xhd_bounded_geo_same_pod_packet_execution_2026-07-10.md
py -m unittest tests.goal5423_level_b_matrix_consolidation_after_geo_test tests.goal5422_bounded_geo_same_pod_packet_execution_test tests.goal5421_bounded_geo_same_pod_packet_plan_test tests.goal5420_figure5_level_b_matrix_consolidation_decision_test
```

Result:

```text
Stop-loss checker: PASS
Ran 19 tests OK
```

The known Windows Python prefix warning appeared and is not a failure.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5423_level_b_matrix_consolidation_after_geo.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5423_level_b_matrix_consolidation_after_geo.json
tests/goal5423_level_b_matrix_consolidation_after_geo_test.py
history/internal_docs/goal5423_xhd_level_b_matrix_consolidation_after_geo_2026-07-10.md
history/internal_docs/call_for_review_goal5423_xhd_level_b_matrix_consolidation_after_geo_2026-07-10.md
```

## Summary

Current Level-B scalar evidence is now:

```text
3 graphics cases, same-POD author/RTDL scalar matches
2 bounded geo cases, same-POD author/RTDL scalar matches
```

This is strong Level-B evidence and useful system validation.  It is still not
full X-HD paper reproduction because exact paper datasets and denominator
alignment remain unresolved.
