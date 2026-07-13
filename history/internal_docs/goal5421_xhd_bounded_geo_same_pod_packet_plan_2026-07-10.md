# Goal5421 - X-HD Bounded Geo Same-POD Packet Plan

## Verdict

```text
completed_bounded_geo_same_pod_packet_plan__no_execution
```

Goal5421 defines the bounded-geo same-POD command packet authorized by
Goal5420.  It does not execute POD commands and does not claim new bounded geo
results.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5421_bounded_geo_same_pod_packet_plan.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.goal5421.bounded_geo_same_pod_packet_plan.v1
status = bounded_geo_same_pod_packet_planned__no_execution
matched = true
row_count = 2
case_ids = ["county_zcta_bounded", "water_bg_bounded"]
```

## Purpose

Goal5419 executed the same-POD graphics matrix.  Goal5420 then decided that the
next work should not be route micro-optimization, but a separate bounded-geo
packet plan.

Goal5421 implements that decision:

- keep bounded geo separate from the graphics `hd_exec`-compatible packet;
- define author and RTDL command payloads for the two known bounded geo cases;
- preserve denominator separation;
- preserve the no-ratio, no-exact-dataset, no-Figure-5 boundary;
- leave actual execution to a later Goal5422.

## Packet Rows

| Case | Paper Pair | Identity Level | Prior Author HDResult | Prior RTDL HDResult | Abs Diff | Tolerance | Prior Match | Route Family |
|---|---|---|---:|---:|---:|---:|---|---|
| `county_zcta_bounded` | `dtl_cnty.wkt -> uszipcode.wkt` | `level_b_bounded_geo_fixture` | 65.44752502441406 | 65.44751976280666 | 5.2616073986655465e-06 | 1e-5 | true | generic partner/Triton |
| `water_bg_bounded` | `USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt` | `level_b_bounded_geo_fixture` | 72.38665008544922 | 72.38664516014835 | 4.925300871150284e-06 | 1e-5 | true | generic partner/Triton |

The prior matches come from Goal5305 and Goal5307.  Goal5421 only packages
those cases for a clean same-POD rerun; it does not execute them.

## Author Command Contract

Both rows use the author `hd_exec` binary with the geo paper flags:

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec
  -input_type wkt
  -n_dims 2
  -variant rt
  -execution gpu
  -normalize=false
  -overwrite=true
  -check=false
```

The exact per-row input and JSON paths are stored in the packet JSON under:

```text
rows[*].author.command
```

## RTDL Command Contract

Both rows use the existing generic partner route:

```text
run_xhd_goal5305_county_zcta_rtdl_numba_gate.py
  --input-type wkt
  --n-dims 2
  --partner triton
  --triton-strategy dense_point_nearest_tiled
  --tolerance 1e-5
```

Route metadata:

```text
route = directed_max_of_nearest_distance_2d_partner_columns
partner_reference_contract = generic_directed_max_of_nearest_distance_2d
native_engine_row_contract = not_called_partner_reference_only
per_source_witness_exact = true
```

This is a generic partner/reference route.  It is not the author X-HD RT-core
algorithm and not a new RTDL geo or X-HD primitive.

## POD Rule

The packet records:

```text
host = 213.173.108.24
port = 13502
wrapper_required = true
naked_ssh_allowed = false
```

Future execution must use:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<remote command>"
```

Goal5421 itself runs no remote commands.

## Denominator Policy

The packet explicitly keeps denominators separate:

```text
author_running_avg_time_ms = record_if_author_json_reports_it
author_process_wall_sec = record_in_goal5422_execution_only
rtdl_route_sec = record_in_goal5422_execution_only
rtdl_total_sec = record_in_goal5422_execution_only
ratio_authorized = false
```

Reason:

```text
Author internal timing, author process wall, RTDL route wall, and RTDL total
are separate denominators.
```

## Claim Boundary

Authorized:

```text
bounded_geo_packet_plan_claimed = true
level_b_bounded_geo_correctness_claimed_from_prior_evidence = true
```

## Stop-Loss Gate G-1

This goal mentions the stopped explicit `-lb` line only as a forbidden restart.
It is not an app-artifact parity implementation goal.  The work uses the
existing generic directed max-nearest partner route and packages bounded geo
consumers of that route.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: generic_directed_max_of_nearest_distance_2d / Goal5128 facility-service-radius consumer family
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

G-1 decision:

```text
PASS: this is a bounded scalar packet around a generic route, not a row/hash/internal-stream parity line.
```

Not authorized:

```text
bounded_geo_execution_claimed = false
figure5_reproduction_claimed = false
geo_figure5_reproduction_claimed = false
exact_paper_dataset_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
performance_ratio_claimed = false
author_rt_core_algorithm_equivalence_claimed = false
explicit_lb_reopened = false
route_micro_optimization_goal_authorized = false
```

## Why This Is The Right Next Step

The graphics matrix is already executed and ready for review.  The bounded geo
rows have prior author/RTDL scalar matches, but they use a different route
family and were deliberately kept out of the graphics packet.

Goal5421 therefore expands the evidence envelope in a disciplined way:

- it packages the geo rows separately;
- it preserves the runner-family boundary;
- it avoids route micro-optimization drift;
- it avoids exact-dataset or Figure-5 overclaims.

## Validation

Commands:

```text
$env:PYTHONPATH='src'
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5421_bounded_geo_same_pod_packet_plan.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5421_bounded_geo_same_pod_packet_plan.json
py -m unittest tests.goal5421_bounded_geo_same_pod_packet_plan_test tests.goal5420_figure5_level_b_matrix_consolidation_decision_test tests.goal5419_figure5_level_b_same_pod_graphics_matrix_test tests.goal5418_figure5_level_b_same_pod_matrix_readiness_test tests.goal5417_figure5_level_b_same_pod_matrix_plan_test
```

Result:

```text
Ran 26 tests OK
```

The known Windows Python prefix warning appeared and is not a failure.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5421_bounded_geo_same_pod_packet_plan.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5421_bounded_geo_same_pod_packet_plan.json
tests/goal5421_bounded_geo_same_pod_packet_plan_test.py
history/internal_docs/goal5421_xhd_bounded_geo_same_pod_packet_plan_2026-07-10.md
history/internal_docs/call_for_review_goal5421_xhd_bounded_geo_same_pod_packet_plan_2026-07-10.md
```

## Next Recommended Goal

```text
Goal5422_bounded_geo_same_pod_packet_execution
```

Goal5422 may execute this packet on the current POD.  It must still keep:

```text
no exact dataset claim
no Figure 5 claim
no author-vs-RTDL performance ratio
no explicit -lb reopening
no route micro-optimization by default
```
