# Goal 548 External Review

Date: 2026-04-18
Reviewer: Claude (external AI review)
Verdict: **ACCEPT**

## Summary

Goal 548 delivers a real HIPRT traversal path for `fixed_radius_neighbors` over `Point3DLayout` inputs. No blockers found.

## Reviewed Artifacts

- `src/native/rtdl_hiprt.cpp` — C++ native backend
- `src/rtdsl/hiprt_runtime.py` — Python ctypes dispatch
- `tests/goal548_hiprt_fixed_radius_3d_test.py` — test suite
- `docs/reports/goal548_hiprt_correctness_matrix_linux_2026-04-18.json` — Linux run results

## Positive Findings

**Traversal approach is sound.** AABB geometry built from search points inflated by radius, with a custom intersection function that performs exact Euclidean distance check. The `hiprtGeomCustomTraversalAnyHit` while-loop exhausts all candidate hits, which is correct for all-in-radius collection.

**Correctness matrix passes.** Linux run shows `fixed_radius_neighbors_3d` PASS with `parity=true`, `hiprt_row_count=5` matching `cpu_reference_row_count=5`. Zero failures across all 17 workloads.

**Input validation is complete.** `k_max == 0`, `k_max > 64`, `radius < 0`, null pointer with nonzero count, and output capacity overflow are all caught before GPU execution, both in C++ and Python.

**Resource cleanup is correct.** `func_table` and `geometry` are destroyed in both the success path and exception path. `DeviceAllocation` RAII handles GPU memory.

**ctypes layout matches C structs.** `_RtdlPoint3D` and its C counterpart both use default alignment (uint32_t + padding + 3 doubles = 32 bytes). `_RtdlFixedRadiusNeighborRow` (two uint32_t + double = 16 bytes) matches the C struct.

**Empty input short-circuit is correct.** Query or search count of zero returns an empty result without touching the GPU.

**Insertion sort in kernel is bounded.** O(k_max) per hit, with k_max capped at 64 — acceptable for this batch size.

## Acknowledged Limitations (non-blocking)

- Coordinates are downcast from double to float for GPU traversal. Documented in the honesty boundary; consistent with the `float_approx` precision tag on the kernel.
- Validation covers only NVIDIA GTX 1070 (CUDA/Orochi path). AMD GPU behavior is not proven. Documented and explicitly out of scope for v0.9.
- `prepare_hiprt` does not yet support `fixed_radius_neighbors` (only `ray_triangle_hit_count`). Correct to leave as `NotImplementedError` given the v0.9 goal ladder.

## No Blockers

Implementation is correct, resource-safe, and bounded to the declared scope. Correctness evidence matches CPU reference on real hardware.
