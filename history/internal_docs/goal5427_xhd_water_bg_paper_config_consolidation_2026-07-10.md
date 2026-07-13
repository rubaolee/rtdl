# Goal5427 - X-HD WaterBodies->BlockGroups Paper-Config Consolidation

## Verdict

```text
existing_goal5314_evidence_sufficient__no_rerun
```

Goal5427 consolidates the current full-public WaterBodies->BlockGroups evidence
after Goal5426.

It does **not** run author `hd_exec` and does **not** run RTDL.  It records that
the correct denominator for this full-public candidate is Goal5314's
paper-config author run (`n_points_cell=8`), not Goal5311's default author run
(`n_points_cell=15`).

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5427_water_bg_paper_config_consolidation.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.goal5427.water_bg_paper_config_consolidation.v1
matched = true
status = existing_goal5314_evidence_sufficient__no_rerun
```

## Why No Rerun

Goal5426 verifies that the current POD has hash-matching full-public WKT
artifacts:

```text
/tmp/xhd_goal5426/full_public_water_bg/USADetailedWaterBodies_full_public.wkt
/tmp/xhd_goal5426/full_public_water_bg/USACensusBlockGroupBoundaries_full_public.wkt
```

These symlink to the existing Goal5311 files, whose hashes match the local
Goal5310 manifest:

```text
WaterBodies sha256 = 0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39
BlockGroups sha256 = 8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e
```

Goal5314 already ran RTDL exact-witness on the same Goal5310 full-public WKT
hashes.  Rerunning the 873s-class exact route would not change the claim
boundary.

## Correct Denominator

Goal5311 default author run:

```text
n_points_cell = 15
HDResult = 0.8970130085945129
paper value matched = false
```

Goal5314 paper-config author run:

```text
n_points_cell = 8
HDResult = 0.8964367508888245
matches paper log = true
AvgTime = 110.167 ms
GridResolution = [2557, 1196]
Iterations = 14
```

Therefore, the paper-log comparison denominator is:

```text
goal5314_paper_config_n_points_cell_8
```

Goal5311 remains useful only as config-sensitivity evidence.

## RTDL Evidence

Goal5314 RTDL exact-witness route:

```text
RTDL HDResult float64 = 0.8964380566690101
abs diff vs author paper-config float32 = 1.305780185645311e-06
declared tolerance = 2e-6
matched_with_declared_tolerance = true
per_source_witness_exact = true
route_sec = 61.562113016843796
entrypoint_total_sec = 873.2409668043256
```

Goal5314 numeric probe:

```text
same_witness_float32_distance = 0.8964367508888245
distance_float32_matches_paper_log = true
```

## Decision

```text
full_public_water_bg_level_b_scalar_match_confirmed = true
rerun_required_now = false
exact_paper_dataset_reproduction_claimed = false
figure5_reproduction_claimed = false
performance_ratio_claimed = false
```

## Claim Boundary

Authorized:

```text
full_public_level_b_scalar_match_claimed = true
existing_evidence_consolidation_only = true
```

Not authorized:

```text
new_execution_claimed = false
exact_paper_dataset_reproduction_claimed = false
geo_figure5_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
performance_ratio_claimed = false
author_rt_core_equivalence_claimed = false
route_micro_optimization_goal_authorized = false
explicit_lb_reopened = false
```

## Validation

Commands:

```text
$env:PYTHONPATH='src'
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5427_water_bg_paper_config_consolidation.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5427_water_bg_paper_config_consolidation.py
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5427_water_bg_paper_config_consolidation.json
py -m unittest tests.goal5427_water_bg_paper_config_consolidation_test tests.goal5426_full_public_water_bg_wkt_resource_gate_test tests.goal5314_xhd_water_bg_corrected_comparison_summary_test
```

The known Windows Python prefix warning appeared and is not a failure.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5427_water_bg_paper_config_consolidation.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5427_water_bg_paper_config_consolidation.json
tests/goal5427_water_bg_paper_config_consolidation_test.py
history/internal_docs/goal5427_xhd_water_bg_paper_config_consolidation_2026-07-10.md
history/internal_docs/call_for_review_goal5427_xhd_water_bg_paper_config_consolidation_2026-07-10.md
```

## Next Recommended Goal

```text
Goal5428_update_level_b_matrix_with_goal5427_water_bg_paper_config_row
```

Goal5428 should fold this row into the current Level-B matrix as the strongest
full-public geo row:

```text
geo_water_bg_full_public_paper_config
```

It must still keep this below exact paper dataset and Figure 5 reproduction.
