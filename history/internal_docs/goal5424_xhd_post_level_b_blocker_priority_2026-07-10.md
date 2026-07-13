# Goal5424 - X-HD Post-Level-B Blocker Priority

## Verdict

```text
completed_post_level_b_next_branch_selected__full_public_water_bg_feasibility_first__no_route_tuning
```

Goal5424 decides the next technical branch after the Goal5423 Level-B
same-POD matrix consolidation.

It does not run author code, RTDL code, POD commands, or new route
optimizations.  It ranks the remaining blockers and selects the next
full-reproduction-oriented action.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5424_post_level_b_blocker_priority.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.goal5424.post_level_b_blocker_priority.v1
status = post_level_b_next_branch_selected__full_public_water_bg_feasibility_first__no_route_tuning
matched = true
```

## Decision

Goal5424 selects:

```text
recommended_next_goal = Goal5425_full_public_waterbodies_blockgroups_wkt_generation_feasibility
technical_branch = full_public_waterbodies_blockgroups_before_more_route_work
route_micro_optimization = false
explicit_lb = false
county_zcta_full_public_now = false
brats_now = false
osm_now = false
strict_review_packet_available = true
```

Reason:

```text
Goal5423 already provides a Level-B same-POD matrix.
The next full-reproduction blocker is dataset identity / full-public coverage,
not another route timing column.
```

## Candidate Ranking

### Rank 1 - Full-Public WaterBodies -> BlockGroups

```text
candidate = full_public_waterbodies_blockgroups
action = feasibility_and_generation_plan_first
claim_if_executed = Level-B full-public geo candidate only
```

Evidence from Goal5309:

| Service | Paper Points | Observed Public Points | Delta | Relative Delta | Max MBR Delta |
|---|---:|---:|---:|---:|---:|
| `USADetailedWaterBodies.wkt` | 22,818,694 | 22,824,823 | +6,129 | 0.0268596% | 2.908e-06 |
| `USACensusBlockGroupBoundaries.wkt` | 52,271,340 | 52,271,467 | +127 | 0.000243% | 3.710e-06 |

This is the strongest current full-public geo candidate by point-count and MBR
proximity.  It is still not exact paper input recovery because file/hash
provenance is absent.

### Rank 2 - County Source / Simplification Investigation

```text
candidate = alternate_county_source_or_simplification_search
action = investigate_before_full_public_execution
```

Reason:

```text
ZCTA is close, but County has +3,039,134 points (+32.2%) relative to the paper
log.  County-ZCTA should not be the next full-public execution branch without
an alternate County source or simplification match.
```

### Rank 3 - BraTS 2020

```text
candidate = brats_2020
action = requires_access_or_license_before_execution
```

BraTS remains blocked by registration/license and author image-list provenance.

### Rank 4 - OSM Lakes / Parks / AllNodes

```text
candidate = osm_lakes_parks_allnodes
action = requires_snapshot_filter_conversion_plan_before_execution
```

OSM remains blocked by snapshot, filter, and conversion provenance.

## Goal5425 Requirements

Goal5425 must be feasibility and generation planning, not an execution goal.

Required:

```text
must_not_run_author_or_rtdl_yet = true
must_estimate_or_bound_wkt_size_and_disk = true
must_define_resume_checkpoint_plan = true
must_define_author_loader_semantics = true
must_define_pod_upload_or_generation_location = true
must_keep_claim_level = Level-B full-public candidate, not exact paper input
```

Kill conditions:

```text
generated point counts diverge materially from Goal5309 probe
disk or runtime requirements exceed available POD resources
ArcGIS service export cannot be made deterministic/reproducible
```

## Claim Boundary

Authorized:

```text
level_b_same_pod_matrix_claimed = true
next_branch_decision_claimed = true
```

Not authorized:

```text
full_public_water_bg_execution_claimed = false
exact_paper_dataset_reproduction_claimed = false
figure5_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
performance_ratio_claimed = false
explicit_lb_reopened = false
route_micro_optimization_goal_authorized = false
```

## Stop-Loss Gate G-1

Goal5424 mentions explicit `-lb` only to keep it closed.  It does not start
row identity, hash parity, offload-stream parity, or other app-artifact parity
work.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: dataset_provenance_and_full_public_candidate_selection / no app-artifact parity work
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

G-1 decision:

```text
PASS: this is a dataset/provenance branch decision, not an app-artifact parity line.
```

## Validation

Commands:

```text
$env:PYTHONPATH='src'
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5424_post_level_b_blocker_priority.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5424_post_level_b_blocker_priority.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5423_xhd_level_b_matrix_consolidation_after_geo_2026-07-10.md
py -m unittest tests.goal5424_post_level_b_blocker_priority_test tests.goal5423_level_b_matrix_consolidation_after_geo_test tests.goal5422_bounded_geo_same_pod_packet_execution_test
```

Result:

```text
Stop-loss checker: PASS
Ran 15 tests OK
```

The known Windows Python prefix warning appeared and is not a failure.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5424_post_level_b_blocker_priority.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5424_post_level_b_blocker_priority.json
tests/goal5424_post_level_b_blocker_priority_test.py
history/internal_docs/goal5424_xhd_post_level_b_blocker_priority_2026-07-10.md
history/internal_docs/call_for_review_goal5424_xhd_post_level_b_blocker_priority_2026-07-10.md
```

## Summary

The next productive branch is not more RTDL route tuning.  It is a
full-public WaterBodies->BlockGroups feasibility plan, because that pair is
the strongest currently available bridge from bounded Level-B evidence toward
the paper's geo workload scale.
