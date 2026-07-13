# Goal5422 - X-HD Bounded Geo Same-POD Packet Execution

## Verdict

```text
completed_bounded_geo_same_pod_packet_execution__level_b_only_no_ratio
```

Goal5422 executes the Goal5421 bounded-geo packet on the current POD.  Both
bounded geo rows match the same-POD author rerun scalar within tolerance.

This is Level-B bounded geo scalar evidence only.  It is not exact paper input
recovery, not geo Figure 5 reproduction, not author X-HD RT-core equivalence,
and not a performance-ratio denominator.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5422_bounded_geo_same_pod_packet_execution.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.goal5422.bounded_geo_same_pod_packet_execution.v1
status = bounded_geo_same_pod_packet_executed__level_b_only_no_ratio
matched = true
row_count = 2
```

POD:

```text
host = 213.173.108.24
port = 13502
wrapper_required = true
naked_ssh_allowed = false
```

POD access used the project wrapper.  No naked SSH was used for Goal5422.

## Matrix

| Case | Paper Pair | Point Counts | Author HDResult | RTDL HDResult | Abs Diff | Tolerance | Author AvgTime ms | Author remote wall s | RTDL route s | RTDL total s | RTDL remote wall s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `county_zcta_bounded` | `dtl_cnty.wkt -> uszipcode.wkt` | 38034 / 50272 | 65.44752502441406 | 65.44751976280666 | 5.2616073986655465e-06 | 1e-5 | 6.506 | 1.263 | 0.639 | 3.675 | 4.974 |
| `water_bg_bounded` | `USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt` | 124 / 894 | 72.38665008544922 | 72.38664516014835 | 4.925300871150284e-06 | 1e-5 | 4.423 | 1.107 | 0.536 | 2.089 | 3.329 |

Both rows use comparison reference:

```text
directed_input1_to_input2
```

Both rows matched:

```text
abs_diff <= 1e-5
```

## RTDL Route Contract

Both rows use the same generic RTDL partner route:

```text
route = directed_max_of_nearest_distance_2d_partner_columns
partner = triton
triton_strategy = dense_point_nearest_tiled
partner_reference_contract = generic_directed_max_of_nearest_distance_2d
native_engine_row_contract = not_called_partner_reference_only
per_source_witness_exact = true
```

This route is a generic directed max-nearest partner route.  It is not the
author X-HD RT-core algorithm and does not add a geo/X-HD-specific primitive to
RTDL core.

## Raw Evidence

Downloaded raw outputs:

```text
Paper-reproduction-apps/x-hd-paper/results/goal5422_raw/county_zcta_bounded_author.json
Paper-reproduction-apps/x-hd-paper/results/goal5422_raw/county_zcta_bounded_rtdl_summary.json
Paper-reproduction-apps/x-hd-paper/results/goal5422_raw/water_bg_bounded_author.json
Paper-reproduction-apps/x-hd-paper/results/goal5422_raw/water_bg_bounded_rtdl_summary.json
```

Source packet:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5421_bounded_geo_same_pod_packet_plan.json
```

## Denominator Policy

Goal5422 records several timing columns but does not form a ratio:

```text
author Running.AvgTime
author remote process wall
RTDL route phase
RTDL total phase
RTDL remote process wall
```

These are different denominators:

- author `Running.AvgTime` is an internal author algorithm timer;
- author remote process wall includes author process overhead;
- RTDL route phase is the generic partner route phase;
- RTDL total includes app-owned WKT loading and partner-column upload;
- RTDL remote process wall includes Python process and wrapper command overhead.

Therefore:

```text
performance_ratio_claimed = false
```

## Claim Boundary

Authorized:

```text
bounded_geo_execution_claimed = true
level_b bounded geo scalar correctness for the two packet rows
```

## Stop-Loss Gate G-1

This goal mentions the stopped explicit `-lb` line only as a forbidden restart.
It does not attempt row identity, hash parity, offload-stream parity, or any
other author internal artifact parity.  The execution uses the existing generic
directed max-nearest partner route on bounded geo fixtures.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: generic_directed_max_of_nearest_distance_2d / Goal5128 facility-service-radius consumer family
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

G-1 decision:

```text
PASS: this is bounded scalar execution through a generic route, not an app-artifact parity line.
```

Not authorized:

```text
exact_paper_dataset_reproduction_claimed = false
geo_figure5_reproduction_claimed = false
figure5_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
performance_ratio_claimed = false
author_rt_core_algorithm_equivalence_claimed = false
explicit_lb_reopened = false
route_micro_optimization_goal_authorized = false
```

## Interpretation

Goal5422 extends the Level-B same-POD evidence envelope from graphics-only to
graphics plus bounded geo fixtures:

```text
Goal5419: 3 graphics rows, same-POD author/RTDL scalar matches.
Goal5422: 2 bounded geo rows, same-POD author/RTDL scalar matches.
```

This is a useful correctness and ingestion milestone, but it still does not
solve the exact paper input blocker.  The geo fixtures are bounded ArcGIS
samples:

- County-ZCTA uses bounded County / ZCTA rows, not the full exact paper input;
- WaterBodies-BG uses five-feature bounded ArcGIS rows, not the full exact
  paper input.

## Validation

Commands:

```text
$env:PYTHONPATH='src'
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5422_bounded_geo_same_pod_packet_execution.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5422_bounded_geo_same_pod_packet_execution.json
py -m unittest tests.goal5422_bounded_geo_same_pod_packet_execution_test tests.goal5421_bounded_geo_same_pod_packet_plan_test tests.goal5420_figure5_level_b_matrix_consolidation_decision_test tests.goal5419_figure5_level_b_same_pod_graphics_matrix_test tests.goal5418_figure5_level_b_same_pod_matrix_readiness_test
```

Result:

```text
Ran 25 tests OK
```

The known Windows Python prefix warning appeared and is not a failure.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5422_bounded_geo_same_pod_packet_execution.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5422_bounded_geo_same_pod_packet_execution.json
Paper-reproduction-apps/x-hd-paper/results/goal5422_raw/
tests/goal5422_bounded_geo_same_pod_packet_execution_test.py
history/internal_docs/goal5422_xhd_bounded_geo_same_pod_packet_execution_2026-07-10.md
history/internal_docs/call_for_review_goal5422_xhd_bounded_geo_same_pod_packet_execution_2026-07-10.md
```

## Next Recommended Goal

```text
Goal5423_level_b_matrix_consolidation_after_geo
```

Goal5423 should consolidate:

- Goal5419 graphics same-POD matrix;
- Goal5422 bounded geo same-POD matrix;
- remaining blockers for exact paper datasets and Figures 5-11.

It should not start route micro-optimization or reopen explicit `-lb`.
