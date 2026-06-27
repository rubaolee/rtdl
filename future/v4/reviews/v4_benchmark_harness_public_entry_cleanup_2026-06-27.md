# V4 Benchmark Harness Public Entry Cleanup

Date: 2026-06-27

Purpose: make the GitHub source view of benchmark apps match the V4 public
documentation promise. New users should see simple current V4 entrypoints first;
the large historical benchmark harnesses remain available only as reproduction
payloads.

## What Changed

| Area | Action |
| --- | --- |
| Benchmark app directories | Kept `v4_app.py` as the current user entrypoint for all 10 benchmark apps. |
| Historical harness bodies | Moved the full legacy benchmark harness implementations to `history/v4_0_benchmark_harness_archive_2026-06-27/`. |
| Compatibility | Recreated the historical harness filenames as small compatibility bridges that load or run the archived payload. |
| V4 public entry helper | Removed direct historical harness paths from `examples/benchmark_apps/_support/v4_public_entry.py`; `--run-harness` now uses the shared compatibility runner. |
| Paper reproduction scripts | Updated `examples/paper_reproduction/rayjoin.py` and `examples/paper_reproduction/rt_barneshut.py` to use the same compatibility runner. |
| Hausdorff helper files | Archived the old helper bodies and left small import-compatible bridge modules. |
| Contact manifold C++ baseline | Kept the C++ baseline next to the current app directory and patched the archived Python harness to find it there. |
| Public gates | Added the compatibility bridges and paper reproduction scripts to the public code scan. |

## Files Moved To History

- `examples/benchmark_apps/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `examples/benchmark_apps/rtnn/rtdl_rtnn_benchmark_app.py`
- `examples/benchmark_apps/triangle_counting/rtdl_triangle_counting_benchmark_app.py`
- `examples/benchmark_apps/robot_collision/rtdl_robot_collision_benchmark_app.py`
- `examples/benchmark_apps/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `examples/benchmark_apps/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
- `examples/benchmark_apps/contact_manifold/rtdl_contact_manifold_benchmark_app.py`
- `examples/benchmark_apps/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/benchmark_apps/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
- `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
- `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
- `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_language_lab.py`
- `examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_v2_user_benchmark.py`

## Current User Path

Users should start from:

- `README.md`
- `tutorials/current/`
- `examples/simple/`
- `examples/benchmark_apps/*/v4_app.py`
- `examples/paper_reproduction/`

The compatibility bridge files exist for old commands and reproducibility, not
as the recommended learning path.

## Verification Target

This cleanup is valid only if:

- `v4_app.py --json` works for every benchmark app.
- `v4_app.py --run-harness -- --help` can reach the archived harness.
- Paper reproduction wrappers can reach their archived reproduction payloads.
- Public docs and public code scans report no stale internal language.
