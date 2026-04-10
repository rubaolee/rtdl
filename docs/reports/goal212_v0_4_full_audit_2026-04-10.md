# Goal 212 Report: v0.4 Full Audit

Date: 2026-04-10
Status: implementation and local verification complete; external full audit pending

## Summary

Goal 212 is the first whole-line audit report for the active `v0.4`
nearest-neighbor package.

At this point, the `v0.4` line contains:

- two nearest-neighbor workloads:
  - `fixed_radius_neighbors`
  - `knn_rows`
- public contracts for both
- public DSL/lowering for both
- Python truth paths for both
- native CPU/oracle for both
- Embree for both
- optional SciPy / PostGIS external baseline helpers for both
- top-level public examples for both
- one bounded scaling note
- preview release-surface docs
- one workload / research-foundations doc

## Goal Coverage

This audit covers the current `v0.4` goal chain:

- Goal 196: `fixed_radius_neighbors` contract
- Goal 197: `fixed_radius_neighbors` DSL surface
- Goal 198: `fixed_radius_neighbors` truth path
- Goal 199: `fixed_radius_neighbors` CPU/oracle
- Goal 200: `fixed_radius_neighbors` Embree
- Goal 201: `fixed_radius_neighbors` external baselines
- Goal 202: `knn_rows` contract
- Goal 203: `knn_rows` DSL surface
- Goal 204: `knn_rows` truth path
- Goal 205: `knn_rows` CPU/oracle
- Goal 206: `knn_rows` Embree
- Goal 207: `knn_rows` external baselines
- Goal 208: public example chain
- Goal 209: bounded scaling note
- Goal 210: preview release surface
- Goal 211: live-doc consistency audit

## Important Mid-Line Correction

The Goal 209 scaling work exposed a real missed backend bug in the earlier Goal
200 Embree closure:

- `fixed_radius_neighbors` on Embree was missing
  `g_query_kind = QueryKind::kFixedRadiusNeighbors` before `rtcPointQuery(...)`
- this could force the shared callback down the wrong branch and yield zero rows

That bug is now fixed in:

- `/Users/rl2025/rtdl_python_only/src/native/embree/rtdl_embree_api.cpp`

and the affected Goal 200 tests were rerun successfully.

## Consolidated Verification

Ran:

- `PYTHONPATH=src:. python3 -m unittest tests.test_core_quality tests.rtdsl_language_test tests.baseline_contracts_test tests.goal198_fixed_radius_neighbors_truth_path_test tests.goal199_fixed_radius_neighbors_cpu_oracle_test tests.goal200_fixed_radius_neighbors_embree_test tests.goal201_fixed_radius_neighbors_external_baselines_test tests.goal204_knn_rows_truth_path_test tests.goal205_knn_rows_cpu_oracle_test tests.goal206_knn_rows_embree_test tests.goal207_knn_rows_external_baselines_test tests.goal208_nearest_neighbor_examples_test tests.goal209_nearest_neighbor_scaling_note_test`
  - `Ran 170 tests`
  - `OK`

Also previously rerun during the line:

- `python3 -m compileall` on the live `docs/rtdl`, `docs/features`, and
  nearest-neighbor example trees
  - `OK`
- direct CLI smoke for:
  - `examples/rtdl_fixed_radius_neighbors.py`
  - `examples/rtdl_knn_rows.py`
  - `examples/internal/rtdl_v0_4_nearest_neighbor_scaling_note.py`
  - `OK`

## Current Honest Status

What is now true:

- the active `v0.4` nearest-neighbor line is real and runnable
- the live docs now present that line much more honestly than earlier in the
  day
- the current preview package no longer reads like a partially planned shell

What is not yet claimed by this audit report:

- that `v0.4` is released
- that nearest-neighbor GPU backends are closed
- that the current local scaling note is a benchmark-win claim

## Remaining Formal Closure Work

This full-audit report is ready for external review.

The intended next step is:

- one whole-line external audit, ideally Claude after the `4am` availability
  window, covering code, docs, and process history across Goals 196–211
