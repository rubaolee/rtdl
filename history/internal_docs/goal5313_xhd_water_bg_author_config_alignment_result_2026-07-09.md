# Goal5313 - X-HD WaterBodies/BG Author Config Alignment Result

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

Goal5313 resolves the apparent Goal5311/Goal5312 WaterBodies -> BlockGroups
scalar mismatch. The mismatch was not caused by a bad WKT file name, an RTDL
witness metadata bug, or a failure to ingest the full-public candidate. It was
caused by comparing against an author rerun with the wrong `n_points_cell`
setting.

The paper-branch logs for this pair use:

```text
num_points_per_cell = 8
```

Goal5311's first author rerun used the author binary default:

```text
num_points_per_cell = 15
```

Re-running the author binary on the same Goal5310 full-public WKT files with
`-n_points_cell=8` exactly reproduces the paper-branch log HDResult.

## Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_author_water_bg_full_public_n_points_cell_8.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_water_source_13579843.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_bg_target_22441127.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_water_bg_witness_distance_probe.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5313_water_bg_n_points_cell_alignment_summary.json
Paper-reproduction-apps/x-hd-paper/results/goal5313_raw/author_npc8_stdout.txt
Paper-reproduction-apps/x-hd-paper/results/goal5313_raw/author_npc8_stderr.txt
Paper-reproduction-apps/x-hd-paper/scripts/inspect_xhd_wkt_point_by_index.py
tests/goal5313_xhd_water_bg_n_points_cell_alignment_test.py
```

## Author Config Alignment

Paper-branch log value:

```text
HDResult = 0.8964367508888245
num_points_per_cell = 8
```

Goal5311 default author rerun:

```text
HDResult = 0.8970130085945129
NumPointsPerCell = 15
abs diff vs paper log = 0.0005762577056884766
```

Goal5313 author rerun with paper-log config:

```text
Command includes: -n_points_cell=8
HDResult = 0.8964367508888245
NumPointsPerCell = 8
abs diff vs paper log = 0.0
Running.AvgTime = 110.167 ms
GridResolution = [2557, 1196]
Iterations = 14
```

This means the earlier Goal5311 "same-public author mismatch" was a
configuration mismatch:

```text
default author rerun (15 points/cell) != paper-log author run (8 points/cell)
```

## RTDL Witness Probe

Goal5312's exact-witness RTDL route reported:

```text
HDResult = 0.8964380566690101
source_id = 13,579,843
target_id = 22,441,127
per_source_witness_exact = true
```

Goal5313 added a streaming WKT point-index inspector and extracted those two
coordinates from the same full-public WKT files:

```text
source = [-81.9999084473, 44.5000190735]
target = [-82.7264814704, 43.974954476]
```

Distance checks:

```text
float64 distance = 0.8964380566690101
float32 distance = 0.8964367508888245
```

Interpretation:

```text
float64 distance == RTDL Goal5312 HDResult
float32 distance == author/paper-log HDResult
```

So the RTDL witness is self-consistent, and the remaining `1.305780185645311e-06`
difference is the expected float64-vs-float32 numeric boundary for this
full-public candidate, not a large semantic mismatch.

## POD Command

Author rerun command:

```text
/tmp/xhd-goal5112/build-gcc11-optix77-fast/bin/hd_exec \
  -input1 /tmp/xhd_goal5311/data/USADetailedWaterBodies.wkt.full_public_arcgis_candidate.wkt \
  -input2 /tmp/xhd_goal5311/data/USACensusBlockGroupBoundaries.wkt.full_public_arcgis_candidate.wkt \
  -input_type wkt \
  -n_dims 2 \
  -variant rt \
  -execution gpu \
  -json /tmp/xhd_goal5313/author_water_bg_full_public_n_points_cell_8.json \
  -overwrite=true \
  -check=false \
  -normalize=false \
  -n_points_cell=8
```

The POD stderr confirms the same point counts:

```text
Points A: 22824823 Points B: 52271467
Avg Running Time 110.167 ms
HausdorffDistance: distance is 0.896437
```

## Validation

Commands run locally:

```text
py -m unittest tests.goal5313_xhd_water_bg_n_points_cell_alignment_test
py -m unittest \
  tests.goal5310_xhd_water_bg_full_public_wkt_candidate_test \
  tests.goal5311_xhd_water_bg_full_public_author_ingestion_test \
  tests.goal5312_xhd_water_bg_full_public_rtdl_summary_test \
  tests.goal5313_xhd_water_bg_n_points_cell_alignment_test
```

Results:

```text
Ran 3 tests OK
Ran 15 tests OK
```

## Claim Boundary

Allowed summary:

```text
On the full-public WaterBodies/BG candidate, the author binary reproduces the
paper-branch HDResult exactly when rerun with the paper-log
num_points_cell=8 configuration. RTDL's exact-witness route reports the same
witness in float64, and that witness's float32 distance equals the author/paper
value.
```

Forbidden summaries:

```text
Exact paper WKT files are recovered.
Figure 5 is fully reproduced.
RTDL performance parity is established.
RTDL and author use identical numeric precision internally.
The previous Goal5311 default author rerun was the correct paper-log denominator.
```

## Next Recommended Goal

Continue the WaterBodies/BG line by making the paper-log configuration explicit
in the author gate and RTDL comparison summary:

```text
Goal5314: replace or supersede the Goal5311/5312 WaterBodies-BG comparison with
an author-paper-config denominator (`n_points_cell=8`) and record the RTDL
float64-vs-author-float32 tolerance boundary.
```

This should update the public route summary without erasing the Goal5311 default
rerun evidence. Goal5311 remains useful as proof that the author result changes
with `n_points_cell`.
