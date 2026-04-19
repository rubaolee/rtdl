# Goal583 Review: Apple RT Native Ray Hitcount 3D

Verdict: ACCEPT

## Reasons

- **Genuine Native Implementation**: The `rtdl_apple_rt_run_ray_hitcount_3d` function in `src/native/rtdl_apple_rt.mm` utilizes Apple's `MPSRayIntersector` and `MPSTriangleAccelerationStructure`. It correctly employs `MPSIntersectionTypeAny` to perform the intersection test on a per-triangle basis.
- **Honest Documentation**: The report explicitly states the performance trade-off (rebuilding one-triangle acceleration structures in a loop) and clearly distinguishes between native MPS RT coverage (3D closest-hit and 3D hit-count) and CPU-reference compatibility dispatch.
- **Correct Dispatch Logic**: `src/rtdsl/apple_rt_runtime.py` accurately routes 3D ray-triangle hit-count kernels to the native backend while preserving the integrity of the `native_only` flag for other predicates.
- **Verified by Tests**: `tests/goal578_apple_rt_backend_test.py` includes a `native_only=True` test case that forces the execution through the Apple RT native path and validates it against the CPU reference.
