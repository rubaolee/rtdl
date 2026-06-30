# Goal 675: Vulkan Prepared 2D Any-Hit With Packed Rays

Date: 2026-04-20

## Goal

Continue the Goal 670 cross-engine optimization roadmap for Vulkan by reducing repeated-query overhead for bounded 2D `ray_triangle_any_hit`.

## Implementation

Native Vulkan additions:

- `rtdl_vulkan_prepare_ray_anyhit_2d`
- `rtdl_vulkan_run_prepared_ray_anyhit_2d`
- `rtdl_vulkan_destroy_prepared_ray_anyhit_2d`

The prepared native handle stores:

- encoded build-side Triangle2D GPU buffer;
- Vulkan AABB BLAS;
- Vulkan TLAS;
- the existing native any-hit ray tracing pipeline using `terminateRayEXT`.

Python additions:

- `PreparedVulkanRayTriangleAnyHit2D`
- `prepare_vulkan_ray_triangle_any_hit_2d(...)`
- prepared `.run(...)` accepts either tuple Ray2D inputs or existing `PackedRays`.

The packed-ray input matters. Prepared Vulkan scene reuse without packed rays was not a win because Python ray packing dominated. The useful app contract is therefore:

```python
packed_rays = rt.pack_rays(rays)
with rt.prepare_vulkan_ray_triangle_any_hit_2d(triangles) as prepared:
    rows = prepared.run(packed_rays)
```

## Correctness Evidence

Local macOS portable validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal675_vulkan_prepared_anyhit_2d_test \
  tests.goal674_hiprt_prepared_anyhit_2d_test \
  tests.goal671_optix_prepared_anyhit_count_test -v

Ran 19 tests in 0.002s
OK (skipped=7)
```

Linux native Vulkan validation on `lestat@192.168.1.20` from `/tmp/rtdl_goal675`:

```text
make build-vulkan
RTDL_VULKAN_LIB=/tmp/rtdl_goal675/build/librtdl_vulkan.so \
PYTHONPATH=src:. python3 -m unittest \
  tests.goal675_vulkan_prepared_anyhit_2d_test \
  tests.goal636_backend_any_hit_dispatch_test -v

Ran 14 tests in 0.769s
OK (skipped=4)
```

Coverage includes:

- prepared 2D any-hit matches CPU;
- prepared 2D any-hit matches direct Vulkan;
- prepared scene can be reused across ray batches;
- packed 2D rays are accepted;
- empty scene, closed handle, and 3D ray rejection are tested;
- existing Vulkan 2D/3D any-hit dispatch still passes.

## Performance Evidence

Linux repeated-query sanity cases using prepared scene plus prepacked rays:

```text
4096 rays / 1024 triangles:
  direct_median_s: 0.008035034
  prepared_packed_query_median_s: 0.004496957

8192 rays / 8192 triangles:
  direct_median_s: 0.011363139
  prepared_packed_query_median_s: 0.006903602

32768 rays / 8192 triangles:
  direct_median_s: 0.028801230
  prepared_packed_query_median_s: 0.021956306
```

Interpretation:

- Vulkan now has a real repeated-query improvement when both build-side geometry and ray packing are reused.
- This is a moderate win, not an OptiX-style order-of-magnitude win.
- The optimization does not change direct `rt.run_vulkan(...)` behavior.
- Prepared Vulkan without packed rays was measured and found slower on these cases; do not claim the prepared scene handle alone is sufficient for a speedup.

## Boundaries

Accepted claim:

- Vulkan Ray2D/Triangle2D any-hit can now reuse BLAS/TLAS and the build-side triangle buffer across repeated ray batches.
- With prepacked rays, repeated-query wall time improves on the tested Linux NVIDIA/Vulkan host.

Not claimed:

- no prepared Vulkan 3D any-hit yet;
- no Vulkan scalar count-only any-hit API yet;
- no universal speedup for tuple-ray prepared calls;
- no change to DB/graph output allocation behavior in this goal.

## Verdict

Codex verdict: ACCEPT.

Goal 675 satisfies the Vulkan prepared 2D any-hit plus packed-ray optimization slice and is ready for external AI review.
