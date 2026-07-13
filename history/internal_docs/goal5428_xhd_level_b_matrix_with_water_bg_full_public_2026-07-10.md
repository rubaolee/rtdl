# Goal5428 - X-HD Level-B Matrix With WaterBodies->BlockGroups Full-Public Row

## Verdict

```text
level_b_matrix_updated_with_water_bg_full_public_paper_config__review_node__no_ratio
```

Goal5428 updates the current X-HD Level-B matrix to include the consolidated
WaterBodies->BlockGroups full-public paper-config row from Goal5427.

It performs no author execution, no RTDL execution, and no route optimization.
It is a matrix consolidation / review-node goal.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5428_level_b_matrix_with_water_bg_full_public.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.goal5428.level_b_matrix_with_water_bg_full_public.v1
matched = true
status = level_b_matrix_updated_with_water_bg_full_public_paper_config__review_node__no_ratio
```

## Coverage

```text
graphics_case_count = 3
graphics_route_result_count = 6
bounded_geo_case_count = 2
bounded_geo_route_result_count = 2
full_public_geo_case_count = 1
full_public_geo_route_result_count = 1
total_case_count = 6
total_route_result_count = 9
```

Rows:

```text
graphics:
  dragon_happy
  thai_happy_scaled
  thai_asian_scaled

bounded_geo:
  county_zcta_bounded
  water_bg_bounded

full_public_geo:
  geo_water_bg_full_public_paper_config
```

## Full-Public Geo Row

```text
case_id = geo_water_bg_full_public_paper_config
category = geo_full_public
input_identity_level = level_b_full_public_same_source_geo_not_exact_file_hash
paper_pair = USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
point_counts = [22,824,823, 52,271,467]
```

Author denominator:

```text
author_denominator = goal5314_paper_config_n_points_cell_8
author HDResult = 0.8964367508888245
author Running.AvgTime = 110.167 ms
author matches paper log = true
```

RTDL evidence:

```text
RTDL exact-witness float64 = 0.8964380566690101
abs diff vs author = 1.305780185645311e-06
tolerance = 2e-6
matched_author = true
per_source_witness_exact = true
same witness float32 distance = 0.8964367508888245
distance_float32_matches_paper_log = true
route_sec = 61.562113016843796
total_sec = 873.2409668043256
```

This row is stronger than the bounded `water_bg_bounded` fixture, but it remains
Level-B because exact author WKT file/hash provenance is still absent.

## Claim Boundary

Authorized:

```text
level_b_same_pod_scalar_matrix_claimed = true
full_public_geo_scalar_row_claimed = true
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

## Remaining Blockers

```text
exact_paper_dataset_files_or_hashes_missing
figures_5_to_11_denominators_not_aligned
fast_scalar_routes_are_scalar_only_when_per_source_witness_exact_false
explicit_lb_row_identity_fail_closed
```

The WaterBodies->BlockGroups row improves Level-B coverage but does not remove
the exact-input or figure-denominator blockers.

## Stop-Loss Gate G-1

This goal mentions explicit `-lb` only as a blocked remaining line.  It does not
start row/hash/internal-stream parity work.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: Level-B matrix consolidation / no app-artifact parity work
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

Decision:

```text
PASS: review-node matrix consolidation, not row identity or explicit-lb parity.
```

## Validation

Commands:

```text
$env:PYTHONPATH='src'
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5428_level_b_matrix_with_water_bg_full_public.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5428_level_b_matrix_with_water_bg_full_public.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5428_level_b_matrix_with_water_bg_full_public.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5427_xhd_water_bg_paper_config_consolidation_2026-07-10.md history/internal_docs/goal5428_xhd_level_b_matrix_with_water_bg_full_public_2026-07-10.md
py -m unittest tests.goal5428_level_b_matrix_with_water_bg_full_public_test tests.goal5427_water_bg_paper_config_consolidation_test tests.goal5426_full_public_water_bg_wkt_resource_gate_test tests.goal5423_level_b_matrix_consolidation_after_geo_test
```

The known Windows Python prefix warning appeared and is not a failure.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5428_level_b_matrix_with_water_bg_full_public.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5428_level_b_matrix_with_water_bg_full_public.json
tests/goal5428_level_b_matrix_with_water_bg_full_public_test.py
history/internal_docs/goal5428_xhd_level_b_matrix_with_water_bg_full_public_2026-07-10.md
history/internal_docs/call_for_review_goal5428_xhd_level_b_matrix_with_water_bg_full_public_2026-07-10.md
```

## Next Recommended Goal

```text
strict_review_goals5424_5428_or_exact_dataset_provenance
```

Do not start more route micro-optimization or explicit `-lb` work by default.
The next useful work is strict review of the expanded Level-B matrix or exact
dataset / denominator provenance.
