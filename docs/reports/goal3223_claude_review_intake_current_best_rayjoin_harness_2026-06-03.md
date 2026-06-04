# Goal3223: Claude Review Intake for Current-Best RayJoin Harness

Date: 2026-06-03

## Purpose

Goal3223 intakes the independent Claude Goal3221 review of the Goal3220
current-best Spatial RayJoin count/parity harness.

Claude's verdict was `accept-with-boundary`. It found no medium-severity
correctness, ABI, or claim-boundary issues, but identified two low-severity
items before stronger use:

- L1: hardware metadata in the harness was weaker than the Goal3218 public LSI
  probe standard,
- L2: the `overlay_seed` fixture had expected count `0`, making its parity check
  trivially weak.

Goal3223 addresses both and records a fresh pod artifact.

## Actions

- Updated `scripts/goal3220_spatial_rayjoin_current_best_count_harness.py` to
  write harness schema `rtdl.goal3220.spatial_rayjoin_current_best_count_harness.v2`.
- Added stronger pod metadata:
  - `cuda_driver_query`,
  - `nvcc_version`,
  - `rtdl_optix_library`.
- Added a per-workload default dataset policy:
  - `pip`: `tests/fixtures/rayjoin/br_county_subset.cdb`,
  - `lsi`: `tests/fixtures/rayjoin/br_county_subset.cdb`,
  - `overlay_seed`: `derived/authored_overlay_squares_tiled_x64`.
- Corrected the overlay count contract used by the harness: the prepared
  count route returns `overlay_active_pair_dependency_count`, so the CPU
  reference comparison must use `active_seed_count`, not the full
  `pair_dependency_row_count`.
- Added tests that guard the metadata fields, per-workload dataset policy, and
  overlay active-seed count contract.

## Pod Evidence

Artifact:

- `docs/reports/goal3223_spatial_rayjoin_current_best_count_harness_2026-06-03.json`
- `docs/reports/goal3223_spatial_rayjoin_current_best_count_harness_2026-06-03.stdout`

Pod summary:

- Commit: `824dc01950e629f307f03ef83233a58f7e87d4ce`
- GPU: `NVIDIA A40, 570.211.01`
- CUDA driver query: present
- nvcc version: present
- OptiX library: `/root/rtdl_goal3151/build/librtdl_optix.so`
- Status: `pass`
- Warmup: `1`
- Repeat: `5`

| Workload | Dataset | Route | Expected | Observed | Primary Phase Median (ms) |
| --- | --- | --- | ---: | ---: | ---: |
| `pip` | `tests/fixtures/rayjoin/br_county_subset.cdb` | `prepared_optix` | 6 | 6 | `prepared_query_sec`: 0.14010630548000336 |
| `lsi` | `tests/fixtures/rayjoin/br_county_subset.cdb` | `prepared_optix_left_id_dense_count` | 1 | 1 | `left_id_count_device_columns_sec`: 0.12307055294513702 |
| `overlay_seed` | `derived/authored_overlay_squares_tiled_x64` | `prepared_optix` | 64 | 64 | `prepared_query_sec`: 0.367727130651474 |

The first attempted v2 harness pod run usefully exposed the hidden overlay
contract mismatch: CPU full pair-dependency rows were `4096`, while prepared
OptiX count correctly returned the active seed count `64`. Goal3223 keeps the
nonzero fixture and compares the same active-seed count contract.

## Boundary

This intake does not authorize release, public speedup claims, whole-app speedup
claims, broad RT-core claims, true zero-copy claims, `RTDL beats RayJoin`
claims, or RayJoin paper-reproduction claims.

The harness remains count/parity-only. Row overlay continuation is still deferred
Tier B work.
