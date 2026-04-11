# Goal 216 Report

## Summary

Goal 216 adds a first OptiX backend path for `fixed_radius_neighbors`.

The implementation is correctness-first and follows the existing OptiX helper
pattern used by `point_nearest_segment`: GPU-parallel helper execution rather
than a new BVH traversal surface.

## Files Changed

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `tests/goal216_fixed_radius_neighbors_optix_test.py`

## Important Mid-Goal Finding

While validating the new workload on Linux, the OptiX run failed with:

- `CUDA driver error: initialization error`

That failure was not specific to the new `fixed_radius_neighbors` path.

The pre-existing OptiX `point_nearest_segment` helper failed with the same
error on the same Linux host. The actual bug was that the CUDA-helper workloads
were not forcing entry through the initialized OptiX/CUDA context before
`cuModuleLoadData` and `cuLaunchKernel`.

That shared helper bug was fixed by making both:

- `run_point_nearest_segment_cuda(...)`
- `run_fixed_radius_neighbors_cuda(...)`

enter `get_optix_context()` before module load / launch.

## Verification

Local targeted regression:

- `PYTHONPATH=src:. python3 -m unittest tests.goal199_fixed_radius_neighbors_cpu_oracle_test tests.goal200_fixed_radius_neighbors_embree_test tests.goal216_fixed_radius_neighbors_optix_test`
- result:
  - `Ran 16 tests`
  - `OK`
  - local OptiX-specific cases skipped on macOS due unavailable local OptiX runtime

Linux validation host:

- host:
  - `lestat@192.168.1.20`
- `make build-optix`
  - `OK`
- direct smoke after context fix:
  - existing OptiX `point_nearest_segment` path runs again
- `PYTHONPATH=src:. python3 -m unittest tests.goal216_fixed_radius_neighbors_optix_test`
  - `Ran 5 tests`
  - `OK`

## Current Honest State

The Goal 216 implementation is running on the Linux OptiX host and preserves
the bounded `fixed_radius_neighbors` contract at the test slice exercised here.

Review closure is still pending until the external review files are read back
and any real findings are addressed.
