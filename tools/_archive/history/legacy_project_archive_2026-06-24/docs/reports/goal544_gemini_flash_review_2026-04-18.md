ACCEPT for bounded post-`v0.8.0` development use, pending external AI review.

Goal 544 successfully integrates the experimental HIPRT preview into the public-facing documentation and examples. The HIPRT feature is clearly identified as a post-`v0.8.0` experimental backend, explicitly not part of the released `v0.8.0` support matrix.

Key reasons for ACCEPT:
- **Clear Scoping:** Documentation (README.md, quick_tutorial.md, release_facing_examples.md, current_architecture.md, capability_boundaries.md) consistently describes HIPRT as an experimental Linux HIPRT-SDK preview for a single RTDL shape: Ray3D probes, Triangle3D build geometry, and `ray_triangle_hit_count`. It explicitly states that there is no AMD GPU validation, no CPU fallback, and no general support for other RTDL workloads.
- **Runnable Example:** The `examples/rtdl_hiprt_ray_triangle_hitcount.py` demonstrates the feature effectively. It correctly implements CPU Python reference first, gracefully handles HIPRT unavailability, and performs parity checks when HIPRT is present.
- **Tested Implementation:** The `tests/goal544_hiprt_docs_examples_test.py` validates the example's behavior, including scenarios where HIPRT is both available and unavailable, ensuring robustness.
- **Honest Communication:** The public documentation manages user expectations well, avoiding overstatement of release support or general backend capabilities.

This approach makes the new HIPRT surface visible to users without overclaiming it as a released general backend.