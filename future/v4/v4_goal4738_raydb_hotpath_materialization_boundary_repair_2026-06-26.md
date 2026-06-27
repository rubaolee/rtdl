# V4 Goal4738 RayDB Hot-Path Materialization Boundary Repair

Date: 2026-06-26

Status: `focused_pod_complete_pending_external_review_debt`

Decision:
`raydb_v3_regression_cleared_by_device_output_hot_path_boundary_repair`

## Purpose

Goal4737 identified RayDB as the highest-priority remaining blocker:

- Goal4732 repaired the V4 route binding and cleared V2.14 no-regression.
- But the focused result was still V4/V3.0.2 hot `0.954x`.

Goal4738 investigated and fixed that regression without changing the generic
OptiX kernel.

## Root Cause

The V4 native traversal was not slower than V3.0.2. In the Goal4732 raw rows:

- V3 traversal: about `0.005033s`;
- V4 direct device-output traversal: about `0.005006s`;
- V4 app wall was slower because each measured iteration converted device
  output columns back into Python rows for presentation.

That contradicted the V4 metadata boundary: the route claimed no group-row host
materialization in the hot path while the app benchmark included a Python-row
presentation step in the measured window.

## Repair

For `--summary-only-iterations`, the V4 RayDB device-output route now:

1. measures the device-output execution window;
2. keeps Python row materialization out of the measured hot path;
3. materializes rows once after timing for correctness;
4. records explicit metadata:
   - `host_materialization_in_hot_path: false`;
   - `group_rows_downloaded_to_host_in_hot_path: false`;
   - `result_rows_materialized_after_hot_path: true`;
   - `result_materialization_after_hot_path_sec`.

This is not an app-specific native kernel. It is a benchmark/app-frontdoor
measurement-boundary correction for the generic V4 device-output surface.

## Focused POD Rerun

Evidence:

- `future/v4/evidence/v4_goal4738_raydb_hotpath_20260626/summary.json`
- `future/v4/evidence/v4_goal4738_raydb_hotpath_20260626/summary.md`
- raw rows under `future/v4/evidence/v4_goal4738_raydb_hotpath_20260626/raw/`

Scale:

- generated rows: `131072`
- generated groups: `1024`
- repeat/warmup: `7/2`
- V4 backend: `paper_rt_v4_cupy_device_grouped_reduction`

Result:

| version | backend | hot sec | parity |
|---|---|---:|---|
| V2.14 | `paper_rt_optix_prepared_grouped_reduction` | 0.0056826211512088776 | true |
| V3.0.2 | `paper_rt_optix_prepared_grouped_reduction` | 0.005691319704055786 | true |
| V4 current | `paper_rt_v4_cupy_device_grouped_reduction` | 0.005151424556970596 | true |

Ratios:

| comparison | hot speedup |
|---|---:|
| V4 / V2.14 | 1.1031164464050043x |
| V4 / V3.0.2 | 1.1048050187116953x |

V4 hot-path metadata:

- row presentation in measured timing: `0.0`
- result materialization after hot path: `0.0008434988558292389s`
- host materialization in hot path: false
- group rows downloaded to host in hot path: false
- route metadata pass: true

## Interpretation

Goal4738 clears the RayDB V3 regression. It converts RayDB from:

`v2_no_regression_repair_v3_regression_open`

to:

`modest_device_output_hot_path_win_not_formal_bar`

This row is now clean enough for the next matrix as a no-regression/modest-win
row. It is not a formal high-performance row because V4/V2.14 is about `1.10x`,
below the `1.20x` material-speed bar used for app candidate wins.

## Claim Boundary

Goal4738 supports this bounded internal statement:

RayDB, on the focused serious generated workload, now uses the V4 generic
device-output grouped-i64 surface with correctness parity, V4/V2.14 hot
`1.103x`, and V4/V3.0.2 hot `1.105x`.

Goal4738 does not authorize:

- final V4 tag;
- public all-benchmark speedup claim;
- RayDB high-performance claim;
- geomean headline;
- app-specific native kernel;
- automatic partner selection;
- true-zero-copy wording.

## Goal-Level Decision Audit

1. Was I being foolish?
   No. The repair targeted an actual timing-boundary contradiction rather than
   tuning the OptiX kernel without evidence.

2. If yes, what action made the decision foolish?
   The earlier weak action was allowing V4 metadata to say "no hot host
   materialization" while the benchmark converted device columns to Python rows
   inside the measured window.

3. Was there another path?
   Yes. Keep RayDB as a regression/no-go. That would leave a false measurement
   boundary uncorrected.

4. Can I now try a different path that actually solves the problem?
   Yes. Update the next matrix to remove RayDB as a V3-regression blocker, while
   keeping it below the formal high-performance bar.

## Non-Authorization

Goal4738 authorizes no final V4 tag, no public speed claim, no all-benchmark
speedup claim, no app-specific native kernel, no arbitrary callback support, and
no true-zero-copy wording.
