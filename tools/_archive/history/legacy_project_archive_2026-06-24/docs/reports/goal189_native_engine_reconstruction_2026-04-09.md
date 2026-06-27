# Goal 189 Native Engine Reconstruction

Date: 2026-04-09

## Summary

Goal 189 starts the final `v0.3` engineering cleanup line: reconstructing the
native backend engines out of their current single-file monolith shape.

All four bounded reconstruction slices are now complete for:

- the native oracle
- the native Embree backend
- the native OptiX backend
- the native Vulkan backend

## Current Native Inventory

- `src/native/rtdl_oracle.cpp`
- `src/native/rtdl_embree.cpp`
- `src/native/rtdl_optix.cpp`
- `src/native/rtdl_vulkan.cpp`

Line counts at the start of this goal:

- oracle: `1461`
- embree: `1758`
- optix: `3348`
- vulkan: `3494`

## First Slice Completed

The native oracle was reconstructed into a modular layout under:

- `src/native/oracle/rtdl_oracle_abi.h`
- `src/native/oracle/rtdl_oracle_internal.h`
- `src/native/oracle/rtdl_oracle_geometry.cpp`
- `src/native/oracle/rtdl_oracle_polygon.cpp`
- `src/native/oracle/rtdl_oracle_api.cpp`

Compatibility-preserving top-level entry point remains:

- `src/native/rtdl_oracle.cpp`

That top-level file is now only the stable native entry path that pulls the
split oracle modules together.

## Why This First Slice Matters

This gives the project a concrete reconstruction pattern that preserves:

- the public C ABI
- the current Python runtime build/load surface
- existing workload behavior

without leaving the oracle logic trapped in one large file.

## Verification

Bounded oracle-facing tests passed after the split:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal40_native_oracle_test
Ran 3 tests in 2.402s
OK
```

```text
PYTHONPATH=src:. python3 -m unittest tests.goal138_polygon_pair_overlap_area_rows_test tests.goal146_jaccard_backend_surface_test
Ran 8 tests in 2.405s
OK
```

## Second Slice Completed

The native Embree backend was reconstructed into a modular layout under:

- `src/native/embree/rtdl_embree_prelude.h`
- `src/native/embree/rtdl_embree_geometry.cpp`
- `src/native/embree/rtdl_embree_scene.cpp`
- `src/native/embree/rtdl_embree_api.cpp`

Compatibility-preserving top-level entry point remains:

- `src/native/rtdl_embree.cpp`

That top-level file now only provides the stable runtime/build entry path and
pulls the split Embree modules together.

This slice also surfaced and fixed a real shared ABI problem:

- native `RtdlRay2D` records were packed in the C ABI
- the shared Python `ctypes` definition in `src/rtdsl/embree_runtime.py` was not

That mismatch is now corrected, which keeps the reconstructed Embree path
behavior-equivalent and also aligns the shared Python-side ABI used by the
other native backends.

## Verification

Bounded Embree-facing tests passed after the split:

```text
PYTHONPATH=src:. python3 -m unittest tests.rtdsl_embree_test
Ran 9 tests in 0.023s
OK
```

```text
PYTHONPATH=src:. python3 -m unittest tests.rtdsl_vulkan_test
Ran 3 tests in 0.003s
OK (skipped=1)
```

```text
PYTHONPATH=src:. python3 -m unittest tests.goal162_visual_demo_test tests.goal146_jaccard_backend_surface_test
Ran 5 tests in 0.438s
OK
```

## Third Slice Completed

The native OptiX backend was reconstructed into a modular layout under:

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`

Compatibility-preserving top-level entry point remains:

- `src/native/rtdl_optix.cpp`

That top-level file now only provides the stable runtime/build entry path and
pulls the split OptiX modules together.

This slice keeps the embedded CUDA kernel strings and the host-side workload
launchers separated from the exported C API, which is a meaningful structural
improvement even though OptiX remains a large backend internally.

## Verification

Bounded checks passed after the split:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal43_optix_validation_test
Ran 2 tests in 0.001s
OK
```

```text
PYTHONPATH=src:. python3 -m unittest tests.rtdsl_embree_test tests.rtdsl_vulkan_test
Ran 12 tests in 0.026s
OK (skipped=1)
```

```text
python3 -m compileall src/native/rtdl_optix.cpp src/native/optix src/rtdsl/embree_runtime.py
Listing 'src/native/optix'...
```

On this host, that bounded verification is structural rather than a full live
GPU runtime execution pass. The split preserves the current runtime/build
surface, and the stronger OptiX runtime checks should still be exercised on a
machine with the CUDA/OptiX toolchain available.

## Final Slice Completed

The native Vulkan backend was reconstructed into a modular layout under:

- `src/native/vulkan/rtdl_vulkan_prelude.h`
- `src/native/vulkan/rtdl_vulkan_core.cpp`
- `src/native/vulkan/rtdl_vulkan_api.cpp`

Compatibility-preserving top-level entry point remains:

- `src/native/rtdl_vulkan.cpp`

That top-level file now only provides the stable runtime/build entry path and
pulls the split Vulkan modules together.

## Verification

Bounded Vulkan-facing checks passed after the split:

```text
python3 -m compileall src/native/rtdl_vulkan.cpp src/native/vulkan
Listing 'src/native/vulkan'...
```

```text
PYTHONPATH=src:. python3 -m unittest tests.rtdsl_vulkan_test tests.goal169_vulkan_orbit_demo_test
Ran 5 tests in 0.024s
OK (skipped=3)
```

```text
PYTHONPATH=src:. python3 -m unittest tests.rtdsl_embree_test tests.goal43_optix_validation_test
Ran 11 tests in 0.037s
OK
```

## Current Closure State

Goal 189 has now completed the full planned reconstruction order:

1. native oracle
2. Embree
3. OptiX
4. Vulkan

The native engines are no longer maintained as four single-file monoliths.
Each backend still preserves the same stable top-level source path expected by
the current Python runtime/build surface, but the real implementation now lives
in backend-specific module directories under `src/native/`.
