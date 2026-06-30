# Goal2121 X-HD-Inspired Point-Group OptiX Hausdorff Enhancement

Date: 2026-05-16

## Purpose

Goal2120 proved that the current clean A5000 pod can build and execute RTDL/OptiX, but the exact Hausdorff RT path is algorithmically weak: it builds one OptiX custom primitive per target point and asks each query to find an in-radius nearest witness. That matches the naive RT nearest-neighbor direction that the X-HD paper warns against, and the measured RT path stayed slower than the pure CUDA/CuPy continuation even after the pod environment was fixed.

This goal begins the X-HD-guided correction without violating the RTDL app-agnostic engine rule.

## What Changed

Added a generic OptiX primitive:

- `rtdl_optix_prepare_point_group_nearest_witness_2d`
- `rtdl_optix_count_prepared_point_group_threshold_reached_2d`
- `rtdl_optix_run_prepared_point_group_nearest_witness_2d`
- `rtdl_optix_destroy_prepared_point_group_nearest_witness_2d`

The primitive accepts:

- a contiguous 2-D point array;
- generic point-group MBR records (`RtdlPointGroupBounds2D`) with `point_offset` and `point_count` spans;
- a reusable `max_radius` build bound.

OptiX builds a BVH over group MBRs, not individual point AABBs. The intersection program rejects groups whose point-to-MBR lower bound exceeds the active radius. The any-hit program then scans only points inside the accepted group span to either:

- count threshold coverage; or
- carry one nearest in-radius witness per query point.

The v2 Hausdorff example now has `rtdl_rt_grouped_nearest_witness`, which builds uniform point groups in Python and calls the generic primitive. The native engine never receives a Hausdorff-specific ABI name or reducer.

The example also has `rtdl_rt_grouped_adaptive_nearest_witness`, an app-level worklist loop inspired by X-HD. It starts with a small radius, accepts query points as soon as their nearest witness is found, and reruns only the active no-witness subset at larger radii. This keeps the adaptive policy in Python app code while the engine continues to expose only the generic point-group primitive.

## Mapping To X-HD

Implemented now:

- X-HD uniform-grid grouping over the target point set, performed in Python app code.
- BVH over grouped MBRs instead of one primitive per point.
- Point-to-MBR lower-bound pruning in the OptiX intersection shader.
- Exact nearest witness extraction for every query point, followed by exact Python reduction to directed and undirected Hausdorff distance.
- App-level active-query worklist shrink, so not every query point must run at the final Hausdorff radius.

Still pending:

- X-HD adaptive grid-size cost model.
- X-HD estimator-driven global lower/upper bound initialization beyond the conservative dataset bounding-box bound.
- X-HD device-side adaptive radius growth/refit loop.
- X-HD heavy-cell staging to CUDA thread blocks for high-skew cells.
- Same-dataset performance against the X-HD paper datasets.

## Boundary

This is not a release speedup claim. It is the first app-agnostic primitive needed to make RTDL/OptiX follow the X-HD algorithmic shape.

Verdict at this checkpoint:

- Generic engine boundary: `accept`
- X-HD parity: `accept-with-boundary`
- Outperform pure CUDA on X-HD datasets: `needs-more-evidence`

Before making the requested performance claim, we still need a pod run on the X-HD-style datasets or faithful same-shape subsets, comparing:

- `rtdl_rt_grouped_nearest_witness`
- `rtdl_v2_user_cuda`
- standalone CUDA C++ tiled exact HD
- CuPy RawKernel exact HD

## Files

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/rtdsl/optix_runtime.py`
- `examples/rtdl_hausdorff_v2_function.py`
- `examples/rtdl_hausdorff_v2_language_lab.py`
- `tests/goal2121_xhd_point_group_hausdorff_optix_enhancement_test.py`

## Validation

Local Windows static/unit validation:

- `$env:PYTHONPATH='src;.'; py -3 -m py_compile src/rtdsl/optix_runtime.py examples/rtdl_hausdorff_v2_function.py examples/rtdl_hausdorff_v2_language_lab.py tests/goal2121_xhd_point_group_hausdorff_optix_enhancement_test.py`
- `$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2121_xhd_point_group_hausdorff_optix_enhancement_test`

Local Linux build/runtime validation on `192.168.1.20`, detached worktree `/home/lestat/work/rtdl_goal2121_build_20260516`, OptiX prefix `/home/lestat/vendor/optix-dev`:

- `PYTHONPATH=src:. python3 -m py_compile src/rtdsl/optix_runtime.py examples/rtdl_hausdorff_v2_function.py examples/rtdl_hausdorff_v2_language_lab.py tests/goal2121_xhd_point_group_hausdorff_optix_enhancement_test.py`
- `PYTHONPATH=src:. python3 -m unittest tests.goal2121_xhd_point_group_hausdorff_optix_enhancement_test`
- `make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev`
- `RTDL_OPTIX_LIB=build/librtdl_optix.so PYTHONPATH=src:. python3 -m unittest tests.goal637_optix_native_any_hit_test tests.goal162_optix_visual_demo_parity_test`
- A direct `hausdorff_distance_2d_rt_grouped_nearest_witness` smoke on two 2-point sets returned exact distance `2.0` and forced runtime compilation of the new grouped threshold and nearest-witness OptiX kernels.
