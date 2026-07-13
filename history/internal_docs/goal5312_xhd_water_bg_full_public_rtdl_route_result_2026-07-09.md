# Goal5312 X-HD WaterBodies -> BlockGroups Full-Public RTDL Route Result

Date: 2026-07-09

Status: `implemented_review_pending`

## Scope

Run RTDL on the same full-public WaterBodies -> BlockGroups WKT candidate that
Goal5311 ran through author `hd_exec`.

This goal is a Level-B full-public execution gate. It is not exact Figure-5
paper reproduction because Goal5311 already showed the public candidate's
author HDResult differs from the paper-branch log.

## What Changed

### 1. Generic 2-D -> 3-D zero-z lift for cell-MBR routes

The scalable cell-MBR route is currently a 3-D route. To allow 2-D WKT inputs
to use it without adding an X-HD-specific primitive, this goal adds an explicit
fail-closed lift:

```text
(x, y) -> (x, y, 0)
```

Files:

```text
Paper-reproduction-apps/x-hd-paper/scripts/xhd_input_loader.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
tests/goal5312_xhd_2d_zero_z_cell_mbr_route_test.py
tests/goal5312_xhd_2d_zero_z_cell_mbr_pod_artifact_test.py
tests/goal5312_xhd_water_bg_full_public_rtdl_summary_test.py
```

The lift is explicit:

```text
--lift-2d-to-3d-zero-z
```

Without that flag, a 2-D cell-MBR route fails closed and the default 2-D route
remains `public-columnar`.

### 2. Streaming WKT matrix front door

`load_wkt_point_matrix()` now fills a NumPy matrix in two streaming passes
instead of building one global Python tuple list before conversion. This is
required for multi-GB WKT inputs.

The parser semantics remain the same as the existing app-owned WKT contract:

```text
POINT / LINESTRING / MULTILINESTRING supported
POLYGON / MULTIPOLYGON use outer rings only
```

## Local Validation

```text
py -m unittest tests.goal5312_xhd_2d_zero_z_cell_mbr_route_test
Ran 5 tests OK

py -m unittest \
  tests.goal5312_xhd_2d_zero_z_cell_mbr_route_test \
  tests.goal5312_xhd_2d_zero_z_cell_mbr_pod_artifact_test \
  tests.goal5312_xhd_water_bg_full_public_rtdl_summary_test
Ran 8 tests OK

py -m unittest \
  tests.goal5310_xhd_water_bg_full_public_wkt_candidate_test \
  tests.goal5311_xhd_water_bg_full_public_author_ingestion_test \
  tests.goal5309_xhd_full_public_arcgis_probe_result_test
Ran 14 tests OK

py -m unittest \
  tests.goal5310_xhd_water_bg_full_public_wkt_candidate_test \
  tests.goal5311_xhd_water_bg_full_public_author_ingestion_test \
  tests.goal5255_xhd_rtdl_hd_exec_entrypoint_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test
Ran 17 tests OK
```

The Windows `py` launcher printed the known noisy
`Could not find platform independent libraries <prefix>` message; tests passed.

## POD Validation

POD:

```text
host = 213.173.108.24
port = 13502
hostname = 45c502cfccb5
gpu = NVIDIA RTX 4000 Ada Generation, driver 550.127.05
```

POD tests:

```text
cd /tmp/rtdl_goal5305
python -m unittest tests.goal5312_xhd_2d_zero_z_cell_mbr_route_test
Ran 5 tests OK
```

Small OptiX smoke:

```text
input_n_dims = 2
execution_n_dims = 3
lift_2d_to_3d_zero_z = true
route_label = cell-mbr-fast-scalar
route = rtdl_cell_mbr_frontier_optix_3d
HDResult = 9.0
claim flags = false
```

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5312_2d_zero_z_cell_mbr_pod_smoke.json
```

## Full-Public RTDL Runs

Pair:

```text
USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
```

Point counts:

```text
WaterBodies = 22,824,823
BlockGroups = 52,271,467
```

Author same-public result from Goal5311:

```text
author HDResult = 0.8970130085945129
paper-log HDResult = 0.8964367508888245
author abs delta vs paper log = 0.0005762577056884766
author Running.AvgTime = 103.564 ms
```

### Fast scalar route

Command shape:

```text
run_xhd_rtdl_hd_exec.py
  -n_dims 2
  -input_type wkt
  -variant rt
  -execution gpu
  --rtdl-route cell-mbr-fast-scalar
  --lift-2d-to-3d-zero-z
  --grid-shape 256,128,1
  --max-inline-points 512
```

Result:

```text
RTDL HDResult = 0.8964380566690101
abs diff vs author same-public = 0.0005749519255028313
abs diff vs paper log = 0.000001305780185645311
load_input_sec = 799.0501907840371
rtdl_route_sec = 74.4317325502634
entrypoint_total_sec = 878.4006162211299
frontier_row_count = 162,583
candidate_distance_evaluations = 1,768,448,183
global_bound_early_break = true
global_bound_early_break_count = 22,696,892
per_source_witness_exact = false
```

Interpretation:

```text
This route executes the full-public candidate, but it is not a correctness
gate for author same-public HDResult. It uses global-bound early break and
does not keep exact per-source witnesses. Its close match to the paper log is
not a valid Figure-5 claim because the same public input differs from the
author rerun.
```

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5312_water_bg_full_public_rtdl_cell_mbr.json
```

### Exact-witness label route

Command shape:

```text
run_xhd_rtdl_hd_exec.py
  -n_dims 2
  -input_type wkt
  -variant rt
  -execution gpu
  --rtdl-route cell-mbr-exact-witness
  --lift-2d-to-3d-zero-z
  --grid-shape 256,128,1
  --max-inline-points 512
```

Result:

```text
RTDL HDResult = 0.8964380566690101
abs diff vs author same-public = 0.0005749519255028313
abs diff vs paper log = 0.000001305780185645311
load_input_sec = 806.7858745679259
rtdl_route_sec = 61.562113016843796
entrypoint_total_sec = 873.2409668043256
frontier_row_count = 0
candidate_distance_evaluations = 0
initial_candidate_distance_evaluations = 402,228,670,641
initial_grid_cell_probes = 271,349,174
initial_scanned_cell_count = 28,805,280
exact_seed_frontier_skipped = true
initial_seed_quality = exact_nearest_witness_under_grid_cell_branch_bound
per_source_witness_exact = true
source_id = 13,579,843
target_id = 22,441,127
```

Interpretation:

```text
This route also executes the full-public candidate, but it still does not
match the author same-public HDResult. Despite the route label and metadata,
it cannot be promoted to author correctness for this 2-D lifted WKT case until
the semantic gap is explained.
```

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5312_water_bg_full_public_rtdl_exact_witness.json
```

## Consolidated Summary

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5312_water_bg_full_public_rtdl_summary.json
```

Decision fields:

```text
full_public_rtdl_execution_passed = true
author_same_public_scalar_match_passed = false
fast_scalar_is_not_correctness_gate = true
exact_paper_dataset_reproduction_blocked = true
performance_ratio_claimed = false
```

## Claim Boundary

Allowed:

```text
RTDL can now execute the full-public WaterBodies-BlockGroups WKT candidate
through an explicit 2-D -> 3-D zero-z cell-MBR path.
```

Not allowed:

```text
claiming Figure-5 reproduction;
claiming exact paper dataset recovery;
claiming author same-public scalar match;
claiming performance ratio or parity;
claiming author RT-core algorithm equivalence;
claiming the fast scalar route is a correctness gate for this pair.
```

## Next Required Work

Goal5313 should investigate the semantic mismatch:

```text
author same-public HDResult = 0.8970130085945129
RTDL lifted cell-MBR HDResult = 0.8964380566690101
paper-log HDResult = 0.8964367508888245
```

Likely hypotheses:

```text
H1. RTDL zero-z lifted cell-MBR route is returning a grid/seed approximate
    value despite metadata suggesting exactness.
H2. RTDL WKT parsing / coordinate contract differs from author WKT semantics
    in a way not captured by point counts.
H3. Author same-public run and RTDL route differ in numeric precision or
    preprocessing contract.
H4. The public WKT candidate has a source pair whose exact witness differs
    from the route's reported witness; source/target witness extraction must
    be audited.
```

Do not proceed to a performance matrix until this scalar mismatch is resolved
or explicitly classified.
