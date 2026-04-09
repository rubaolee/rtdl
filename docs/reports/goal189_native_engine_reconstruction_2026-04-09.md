# Goal 189 Native Engine Reconstruction

Date: 2026-04-09

## Summary

Goal 189 starts the final `v0.3` engineering cleanup line: reconstructing the
native backend engines out of their current single-file monolith shape.

The first two bounded slices are now complete for:

- the native oracle
- the native Embree backend

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

## Next Slice

The next reconstruction target should now be:

- `src/native/rtdl_optix.cpp`

That is the right third slice because the oracle/Embree compatibility pattern
is now proven and the remaining work is in the larger GPU-native engines.
