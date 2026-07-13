# Goal5425 - X-HD Full-Public WaterBodies->BlockGroups WKT Generation Feasibility

## Verdict

```text
completed_full_public_water_bg_wkt_generation_feasible_with_checkpoint_gate__no_execution
```

Goal5425 turns the Goal5424 next-branch decision into a concrete feasibility
plan for generating full-public WKT inputs for:

```text
USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
```

It does not generate WKT, does not run author `hd_exec`, does not run RTDL, and
does not claim Figure 5 reproduction.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5425_full_public_water_bg_wkt_generation_feasibility.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.goal5425.full_public_water_bg_wkt_generation_feasibility.v1
status = full_public_water_bg_wkt_generation_feasible_with_checkpoint_gate__no_execution
matched = true
selected_candidate = full_public_waterbodies_blockgroups
```

## Resource Estimate

The estimate uses:

- full-public point counts from Goal5309;
- bounded WKT byte/point ratios from Goal5306.

| Service | Full-Public Author-Loader Points | Bounded Bytes/Point | Estimated WKT MiB | Estimated WKT GiB |
|---|---:|---:|---:|---:|
| `USADetailedWaterBodies.wkt` | 22,824,823 | 30.177 | 656.9 | 0.641 |
| `USACensusBlockGroupBoundaries.wkt` | 52,271,467 | 29.846 | 1487.8 | 1.453 |

Combined estimate:

```text
estimated_total_wkt_bytes = 2,248,869,515
estimated_total_wkt_mib = 2144.69
estimated_total_wkt_gib = 2.094
recommended_free_disk_gib = 6.283
safety_factor = 3.0
```

Probe time floor from Goal5309:

```text
WaterBodies probe elapsed = 640.52s
BlockGroups probe elapsed = 929.21s
combined floor = 1569.74s
```

This is only a floor because WKT generation also formats and writes geometries.

## Generation Plan

Preferred generation location:

```text
POD /tmp/xhd_goal5426/full_public_water_bg
```

Reason:

```text
Full WKT artifacts are large and the next author/RTDL gates run on POD.  Avoid
local disk churn and upload costs if POD disk is sufficient.
```

Required resource preflight:

```text
POD wrapper preflight
df -BG /tmp
verify ArcGIS service reachability
write permission for /tmp/xhd_goal5426/full_public_water_bg
```

Checkpoint files:

```text
USADetailedWaterBodies_full_public.checkpoint.json
USACensusBlockGroupBoundaries_full_public.checkpoint.json
```

Output files:

```text
USADetailedWaterBodies_full_public.wkt
USACensusBlockGroupBoundaries_full_public.wkt
manifest.json
```

Author-loader semantics:

```text
input_type = wkt
n_dims = 2
normalize = false
one_geometry_per_line = true
polygon_outer_ring_only_for_author_point_count = true
close_polygon_outer_rings_if_needed = true
ignore_holes = true
```

## Kill Conditions

Goal5426 must stop before execution if any of these fail:

```text
free disk below 6.283 GiB on /tmp or selected output volume;
generated WaterBodies point count differs from 22,824,823;
generated BlockGroups point count differs from 52,271,467;
ArcGIS export becomes non-deterministic or service schema changes;
generation cannot checkpoint/resume after interruption.
```

## Claim Boundary

Authorized:

```text
feasibility_plan_claimed = true
```

Not authorized:

```text
full_public_wkt_generated = false
author_rtdl_correctness_claimed = false
exact_paper_dataset_reproduction_claimed = false
figure5_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
performance_ratio_claimed = false
route_micro_optimization_goal_authorized = false
explicit_lb_reopened = false
```

## Stop-Loss Gate G-1

This goal does not start app-artifact parity work.  It plans dataset generation
for a full-public candidate and keeps the claim level below exact paper input.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: dataset_generation_feasibility / no app-artifact parity work
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

G-1 decision:

```text
PASS: this is feasibility planning, not row/hash/internal-stream parity.
```

## Validation

Commands:

```text
$env:PYTHONPATH='src'
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5425_full_public_water_bg_wkt_generation_feasibility.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5425_full_public_water_bg_wkt_generation_feasibility.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5424_xhd_post_level_b_blocker_priority_2026-07-10.md
py -m unittest tests.goal5425_full_public_water_bg_wkt_generation_feasibility_test tests.goal5424_post_level_b_blocker_priority_test tests.goal5423_level_b_matrix_consolidation_after_geo_test
```

Result:

```text
Stop-loss checker: PASS
Ran 16 tests OK
```

The known Windows Python prefix warning appeared and is not a failure.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5425_full_public_water_bg_wkt_generation_feasibility.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5425_full_public_water_bg_wkt_generation_feasibility.json
tests/goal5425_full_public_water_bg_wkt_generation_feasibility_test.py
history/internal_docs/goal5425_xhd_full_public_water_bg_wkt_generation_feasibility_2026-07-10.md
history/internal_docs/call_for_review_goal5425_xhd_full_public_water_bg_wkt_generation_feasibility_2026-07-10.md
```

## Next Recommended Goal

```text
Goal5426_full_public_water_bg_wkt_generation_dry_run_or_execute_if_resources_pass
```

Goal5426 may run POD preflight and resource checks.  It may generate WKT only
if disk, checkpoint, service reachability, and deterministic export conditions
pass.  It must not run author `hd_exec` or RTDL comparison yet.
