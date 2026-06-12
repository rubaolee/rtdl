# Goal4346: Fresh Pod CPU-Only OptiX vs Embree Comparison

Date: 2026-06-11

Status: internal engineering evidence; not public speedup authorization.

## Toolchain Fix

- Solved: the Numba/PTX failure was caused by missing old working CUDA env in the fresh runner.
- Fix: put `/usr/local/cuda-12.8/bin` first on `PATH`, set `NUMBA_CUDA_PREFIX=/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc`, and set `CUDA_HOME`/`CUDA_PATH` to that Numba CUDA prefix.
- Verification: Numba CUDA smoke passed; corrected OptiX scale `all_pass` is `True` across all 10 rows.

## Hardware Boundary

- GPU: `NVIDIA RTX 4000 Ada Generation, 550.127.05, 20475 MiB`.
- CPU: `AMD EPYC 7702 64-Core Processor`, 128 logical CPUs visible.
- Boundary: this is Embree CPU evidence on the pod CPU, not Intel-specific Embree evidence.

## OptiX Scale Status

- Corrected full scale `all_pass`: `True`.
- Failed-env attempt is preserved as `optix_scale_summary.json`; fixed run is `optix_scale_summary_fixed_env.json`.

## Measured Rows

| App | Bucket | Metric | OptiX | Embree 8t | Embree 64t | Selected Embree / OptiX | Faster |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `librts_spatial_index` | `clean_same_scale_query_phase` | `query_median_sec` (sec) | 0.000623803 | 0.062685329 | 0.09514946 | 100.49x | `optix` |
| `hausdorff_xhd` | `clean_internal_query_ratio` | `max_directed_query_fixed_radius_threshold_reached_count_sec` (sec) | 0.003853494 | 0.009748009 | 0.014270252 | 2.53x | `optix` |
| `contact_manifold` | `clean_internal_query_ratio` | `native_collect_elapsed_sec` (sec) | 0.000443441 | 0.000376444 | 0.000368218 | 0.83x | `embree` |
| `triangle_counting` | `clean_internal_query_ratio` | `query_median_ms` (ms) | 0.155335292 | 12.108332 | 13.454486 | 77.95x | `optix` |
| `robot_collision` | `boundary_limited_phase_ratio` | `traversal_phase_median_sec` (sec) | 0.000040496 | 0.001181259 | 0.001186779 | 29.17x | `optix` |
| `raydb_style` | `boundary_limited_phase_ratio` | `native_rt_traversal_sec` (sec) | 0.000209818 | 0.013930317 | 0.007873165 | 37.52x | `optix` |

For `Selected Embree / OptiX`, values above 1 mean OptiX is faster for the metric; values below 1 mean Embree is faster. Selected Embree is the faster observed Embree profile between the planned 8-thread run and the 64-thread pod-CPU sensitivity run, and is internal evidence only.

## Remaining Contract Work

| App | Why No Serious Ratio Yet |
| --- | --- |
| `spatial_rayjoin` | toolchain is fixed and current mixed route runs; serious Embree-vs-OptiX ratio still needs a chosen common contract: PIP count, LSI scalar count, or overlay active-count |
| `rt_dbscan` | toolchain is fixed and current OptiX+Numba grouped signature runs; serious Embree-vs-OptiX ratio still needs fixed-radius rows or grouped-signature contract on both sides |
| `barnes_hut` | toolchain is fixed and current Numba exact-force partner-only row runs; serious Embree-vs-OptiX ratio still needs exact-force configured route or node-coverage route on both sides |
| `rtnn` | OptiX row is 3-D ranked summary; Embree registry row is 2-D ANN candidate quality; choose one contract before ratio reporting |

## Claim Boundary

Internal CPU-only NVIDIA OptiX RT-core versus Embree CPU engineering packet. It does not authorize release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, paper reproduction wording, true-zero-copy wording, automatic partner selection, or Intel-CPU-specific claims.
