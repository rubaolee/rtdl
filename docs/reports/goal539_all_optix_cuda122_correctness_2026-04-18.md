# Goal 539: All OptiX-Supported Workload Correctness After CUDA 12.2.2 Upgrade

Date: 2026-04-18

Status: PASS after fixing one broadened-suite correctness blocker

## Question

Did RTDL complete a correctness test for all OptiX-supported workloads after moving the Linux OptiX validation path to the new user-space CUDA 12.2.2 toolkit?

Answer: yes, after expanding beyond Goal 538's focused coverage and fixing a 2D/3D CUDA-function cache collision.

## Environment

- Host: `lx1`
- Kernel: `Linux lx1 6.17.0-20-generic #20~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Thu Mar 19 01:28:37 UTC 2 x86_64`
- GPU: `NVIDIA GeForce GTX 1070`
- Driver: `580.126.09`
- Compute capability: `6.1`
- CUDA toolkit: `/home/lestat/vendor/cuda-12.2.2`
- CUDA compiler: `/home/lestat/vendor/cuda-12.2.2/bin/nvcc`
- CUDA compiler version: `Build cuda_12.2.r12.2/compiler.33191640_0`
- RTDL test checkout: `/tmp/rtdl_optix_cuda122_test`
- RTDL OptiX library: `/tmp/rtdl_optix_cuda122_test/build/librtdl_optix.so`

## Workloads Covered

The broadened suite covers the current OptiX-supported workload families represented by the public and internal OptiX tests:

- 2D geometric ray/triangle hitcount
- 3D ray/triangle hitcount
- point/nearest-segment
- 2D fixed-radius neighbors
- 2D kNN rows
- 3D fixed-radius neighbors
- 3D bounded kNN rows
- 3D kNN rows
- v0.6 graph BFS OptiX path
- v0.6 graph triangle-count OptiX path
- v0.7 DB conjunctive scan
- v0.7 DB grouped count
- v0.7 DB grouped sum
- prepared OptiX DB dataset reuse
- columnar prepared OptiX DB dataset transfer
- OptiX/Embree interop/parity checks
- visual/orbit demo parity checks
- Linux Vulkan/OptiX comparison test coverage
- legacy/cold prepared OptiX test coverage

## Test Command

```bash
cd /tmp/rtdl_optix_cuda122_test
export PYTHONPATH=src:.
export RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so
export RTDL_NVCC=$HOME/vendor/cuda-12.2.2/bin/nvcc
export LD_LIBRARY_PATH=$HOME/vendor/cuda-12.2.2/lib64:${LD_LIBRARY_PATH:-}

python3 -m unittest \
  tests.goal162_optix_visual_demo_parity_test \
  tests.goal169_optix_orbit_demo_test \
  tests.goal216_fixed_radius_neighbors_optix_test \
  tests.goal217_knn_rows_optix_test \
  tests.goal311_v0_5_optix_3d_nn_test \
  tests.goal394_v0_6_rt_graph_bfs_optix_test \
  tests.goal397_v0_6_rt_graph_triangle_optix_test \
  tests.goal427_v0_7_rt_db_optix_backend_test \
  tests.goal427_v0_7_rt_db_optix_perf_test \
  tests.goal435_v0_7_optix_native_prepared_db_dataset_test \
  tests.goal43_optix_validation_test \
  tests.goal441_v0_7_optix_columnar_prepared_db_dataset_transfer_test \
  tests.goal44_optix_benchmark_test \
  tests.goal45_optix_county_zipcode_test \
  tests.goal47_optix_goal41_large_checks_test \
  tests.goal65_vulkan_optix_linux_comparison_test \
  tests.goal99_optix_cold_prepared_run1_win_test \
  tests.optix_embree_interop_test
```

## Initial Failure Found

The first broadened run failed:

```text
Ran 86 tests in 1.920s

FAILED (failures=3)
```

All failures were in `tests.goal311_v0_5_optix_3d_nn_test`:

- 3D fixed-radius neighbors returned zero rows.
- 3D bounded kNN returned zero rows.
- 3D kNN returned zero rows.

The Python reference returned valid rows.

## Root Cause

The native OptiX/CUDA helper layer used shared cached CUDA function objects for both 2D and 3D kernels:

- `g_frn` was used by both `fixed_radius_neighbors` and `fixed_radius_neighbors_3d`.
- `g_knn` was used by both `knn_rows` and `knn_rows_3d`.

When the broader suite initialized the 2D CUDA kernel first, the 3D path reused the wrong cached CUDA function. This is a correctness issue revealed by the broader CUDA 12.2.2 validation order; it is not a language-surface change.

## Fix

Updated:

- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_core.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_workloads.cpp`

Changes:

- Added separate CUDA function caches:
  - `g_frn` for 2D fixed-radius neighbors
  - `g_frn3d` for 3D fixed-radius neighbors
  - `g_knn` for 2D kNN rows
  - `g_knn3d` for 3D kNN rows
- Updated the 3D workload paths to initialize and launch the 3D-specific cached function.

## Final Result

After the fix:

```text
Ran 86 tests in 2.416s

OK
```

## Evidence Files

- `/Users/rl2025/rtdl_python_only/docs/reports/goal539_all_optix_cuda122_correctness_2026-04-18.log`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal539_all_optix_cuda122_correctness_2026-04-18.json`

The JSON evidence records:

- `status: PASS`
- `rtdl_nvcc: /home/lestat/vendor/cuda-12.2.2/bin/nvcc`
- `rtdl_optix_lib: /tmp/rtdl_optix_cuda122_test/build/librtdl_optix.so`
- all 18 test modules listed above

## Honest Boundary

This is an all-current-OptiX-test correctness pass for supported RTDL OptiX workload families after the CUDA 12.2.2 build/runtime upgrade on the Linux NVIDIA host.

It is not:

- a performance claim
- a system CUDA replacement claim
- an RT-core claim, because the GTX 1070 has no RT cores
- a non-NVIDIA backend validation
- a guarantee that every future workload app has an OptiX path unless it is represented by the current OptiX tests

## Verdict

The all-current-OptiX workload correctness gate is now passed under CUDA 12.2.2.
