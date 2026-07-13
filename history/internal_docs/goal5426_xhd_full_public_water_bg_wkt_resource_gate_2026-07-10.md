# Goal5426 - X-HD Full-Public WaterBodies->BlockGroups WKT Resource Gate

## Verdict

```text
resource_gate_complete__existing_goal5311_artifacts_reused__regeneration_not_safe_on_current_tmp
```

Goal5426 runs the POD resource gate requested by Goal5425 for the full-public
WaterBodies->BlockGroups WKT candidate.

It does **not** regenerate WKT, does **not** run author `hd_exec`, does **not**
run RTDL, and does **not** claim Figure 5 reproduction.  It verifies that the
current POD cannot safely regenerate the full WKT under the Goal5425 3x disk
safety threshold, but can safely reuse already-present Goal5311 WKT artifacts
whose hashes match the local Goal5310 manifest.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5426_full_public_water_bg_wkt_resource_gate.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.goal5426.full_public_water_bg_wkt_resource_gate.v1
matched = true
selected_action = reuse_existing_goal5311_full_public_wkt_candidate__no_regeneration
```

## POD Resource Gate

POD wrapper preflight passed:

```text
POD_OK
hostname = 45c502cfccb5
GPU = NVIDIA RTX 4000 Ada Generation, 550.127.05
```

Disk result:

```text
/tmp free GiB = 3.9125747680664062
Goal5425 recommended free GiB = 6.283268840052187
generation_safety_gate_passed = false
```

Interpretation:

```text
The current POD /tmp volume is below the Goal5425 3x free-disk safety line.
Do not regenerate the multi-GiB WKT files on this POD under this condition.
```

## Existing Artifact Reuse Gate

Goal5426 found complete Goal5311 full-public WKT files on the POD:

```text
/tmp/xhd_goal5311/data/USADetailedWaterBodies.wkt.full_public_arcgis_candidate.wkt
/tmp/xhd_goal5311/data/USACensusBlockGroupBoundaries.wkt.full_public_arcgis_candidate.wkt
```

The files match the local Goal5310 manifest:

```text
WaterBodies bytes = 741925630
WaterBodies sha256 = 0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39

BlockGroups bytes = 1560257609
BlockGroups sha256 = 8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e

all_files_exist = true
all_sizes_match = true
all_hashes_match = true
existing_artifact_reuse_gate_passed = true
```

Goal5426 created symlinks instead of copying multi-GiB files:

```text
/tmp/xhd_goal5426/full_public_water_bg/USADetailedWaterBodies_full_public.wkt
  -> /tmp/xhd_goal5311/data/USADetailedWaterBodies.wkt.full_public_arcgis_candidate.wkt

/tmp/xhd_goal5426/full_public_water_bg/USACensusBlockGroupBoundaries_full_public.wkt
  -> /tmp/xhd_goal5311/data/USACensusBlockGroupBoundaries.wkt.full_public_arcgis_candidate.wkt
```

Remote manifest:

```text
/tmp/xhd_goal5426/full_public_water_bg/manifest.json
```

## Prior Author Evidence Kept Visible

Goal5311 already proved the same full-public WKT candidate is ingestible by
author `hd_exec`:

```text
Goal5311 author HDResult = 0.8970130085945129
Goal5311 author ingestion passed = true
Goal5311 paper value matched = false
```

This remains a full-public Level-B candidate, not exact paper input.

Goal5314 supersedes the Goal5311 default-author denominator for paper-log
comparison:

```text
Goal5311 default author n_points_cell=15 HDResult = 0.8970130085945129
Goal5311 paper value matched = false

Goal5314 paper-config author n_points_cell=8 HDResult = 0.8964367508888245
Goal5314 paper-config author matches paper log = true
Goal5314 RTDL exact-witness float64 HDResult = 0.8964380566690101
Goal5314 RTDL exact-witness matches author float32 with declared 2e-6 tolerance = true
```

Therefore the next comparison must use the Goal5314 paper-config denominator,
not the Goal5311 default-author denominator.

## Claim Boundary

Authorized:

```text
resource_gate_claimed = true
existing_goal5311_wkt_reused = true
```

Not authorized:

```text
full_public_wkt_generated_by_goal5426 = false
author_rtdl_correctness_claimed = false
exact_paper_dataset_reproduction_claimed = false
figure5_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
performance_ratio_claimed = false
route_micro_optimization_goal_authorized = false
explicit_lb_reopened = false
```

## Stop-Loss Gate G-1

This is a resource / dataset-availability gate, not an app-artifact parity
direction.

```text
gate_generic_capability_produced: true
gate_non_app_consumer: dataset resource gate / existing artifact reuse, no app-artifact parity
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

Decision:

```text
PASS: resource gate, not row/hash/internal-stream parity.
```

## Validation

Commands:

```text
$env:PYTHONPATH='src'
py Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5426_full_public_water_bg_wkt_resource_gate.py --host 213.173.108.24 --port 13502 --timeout 300
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5426_full_public_water_bg_wkt_resource_gate.json
py scripts/xhd_stop_loss_gate_check.py history/internal_docs/goal5425_xhd_full_public_water_bg_wkt_generation_feasibility_2026-07-10.md history/internal_docs/goal5426_xhd_full_public_water_bg_wkt_resource_gate_2026-07-10.md
py -m unittest tests.goal5426_full_public_water_bg_wkt_resource_gate_test tests.goal5425_full_public_water_bg_wkt_generation_feasibility_test tests.goal5424_post_level_b_blocker_priority_test
```

The known Windows Python prefix warning appeared and is not a failure.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5426_full_public_water_bg_wkt_resource_gate.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5426_full_public_water_bg_wkt_resource_gate.json
tests/goal5426_full_public_water_bg_wkt_resource_gate_test.py
history/internal_docs/goal5426_xhd_full_public_water_bg_wkt_resource_gate_2026-07-10.md
history/internal_docs/call_for_review_goal5426_xhd_full_public_water_bg_wkt_resource_gate_2026-07-10.md
```

## Next Recommended Goal

```text
Goal5427_refresh_or_consolidate_existing_full_public_water_bg_rtdl_against_goal5314_paper_config
```

Goal5427 may use:

```text
/tmp/xhd_goal5426/full_public_water_bg/USADetailedWaterBodies_full_public.wkt
/tmp/xhd_goal5426/full_public_water_bg/USACensusBlockGroupBoundaries_full_public.wkt
```

Goal5427 must compare against the Goal5314 paper-config author denominator:

```text
paper-config author HDResult = 0.8964367508888245
RTDL exact-witness float64 HDResult = 0.8964380566690101
declared tolerance = 2e-6
```

It must keep the paper-log mismatch visible and must not claim exact paper
dataset recovery, Figure 5 reproduction, full paper reproduction, or a
performance ratio.
