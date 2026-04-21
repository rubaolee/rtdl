# Goal 674: HIPRT Prepared 2D Any-Hit Optimization

Date: 2026-04-20

## Goal

Continue the post-v0.9.5 cross-engine optimization round by implementing the HIPRT item from the Goal 670 roadmap:

- add a prepared HIPRT path for bounded 2D `ray_triangle_any_hit`;
- reuse the HIPRT scene/kernel across repeated ray batches;
- keep the claim bounded to Ray2D/Triangle2D any-hit until 3D prepared any-hit is separately implemented;
- verify correctness against the CPU oracle and existing direct HIPRT dispatch on the Linux HIPRT host.

## Implementation

Native HIPRT additions:

- `rtdl_hiprt_prepare_ray_anyhit_2d`
- `rtdl_hiprt_run_prepared_ray_anyhit_2d`
- `rtdl_hiprt_destroy_prepared_ray_anyhit_2d`

The prepared handle stores:

- HIPRT runtime/context;
- encoded 2D triangle device buffer;
- encoded triangle AABB device buffer;
- HIPRT AABB geometry;
- HIPRT function table for `intersectRtdlTriangle2D`;
- JIT-compiled `RtdlRayAnyhit2DKernel`.

Python additions:

- `PreparedHiprtRayTriangleAnyHit2D`
- `prepare_hiprt_ray_triangle_any_hit_2d(...)`
- `rt.prepare_hiprt(...)` dispatch for Ray2D/Triangle2D `ray_triangle_any_hit`

The generic prepared dispatcher now explicitly rejects prepared 3D any-hit rather than implying support. Existing prepared 3D hit-count remains unchanged.

## Correctness Evidence

Local macOS portable validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal674_hiprt_prepared_anyhit_2d_test \
  tests.goal639_hiprt_native_any_hit_test \
  tests.goal543_hiprt_dispatch_test -v

Ran 13 tests in 0.002s
OK (skipped=8)
```

Linux native HIPRT validation on `lestat@192.168.1.20` from `/tmp/rtdl_goal674`:

```text
make build-hiprt
RTDL_HIPRT_LIB=/tmp/rtdl_goal674/build/librtdl_hiprt.so \
PYTHONPATH=src:. python3 -m unittest \
  tests.goal674_hiprt_prepared_anyhit_2d_test \
  tests.goal639_hiprt_native_any_hit_test \
  tests.goal543_hiprt_dispatch_test -v

Ran 13 tests in 5.064s
OK
```

Coverage includes:

- direct prepared 2D any-hit matches CPU;
- generic `rt.prepare_hiprt(...)` prepared 2D any-hit matches CPU;
- prepared handle can be reused for multiple ray batches;
- existing direct HIPRT 2D/3D any-hit still matches CPU;
- existing HIPRT prepared 3D hit-count dispatch still matches CPU;
- prepared 3D any-hit is explicitly rejected as not implemented;
- empty prepared scene and closed-handle behavior are tested.

## Performance Evidence

Linux repeated-query sanity case:

- 4096 rays
- 1024 triangles
- all 4096 rays hit
- direct path and prepared path both returned the same hit count

Measured wall times:

```text
direct_median_s: 0.580084853
prepared_query_median_s: 0.007464495
direct_samples_s:
  [0.580084853, 0.578349963, 0.588148660]
prepared_query_samples_s:
  [0.007579984, 0.007468706, 0.007460285,
   0.007497140, 0.007445179, 0.007422181]
```

Interpretation:

- This is a real repeated-query win from reusing HIPRT setup work: runtime/context, AABB geometry, function table, and JIT kernel.
- This is not yet a scalar count-only or prepacked-ray optimization. The prepared path still encodes/uploads rays and materializes output rows per query.
- The claim should therefore be limited to repeated Ray2D/Triangle2D any-hit workloads where build-side geometry is reused.

## Boundaries

Accepted claim:

- HIPRT now has a prepared 2D any-hit path that avoids rebuilding the HIPRT scene/kernel for repeated query batches and is much faster than the direct unprepared path on the Linux HIPRT host for the measured case.

Not claimed:

- no prepared 3D any-hit support yet;
- no count-only HIPRT any-hit API yet;
- no prepacked HIPRT ray-buffer API yet;
- no AMD GPU hardware validation, because the current HIPRT host uses HIPRT through the CUDA/Orochi path on NVIDIA hardware.

## Verdict

Codex verdict: ACCEPT.

Goal 674 satisfies the HIPRT prepared 2D any-hit optimization slice and is ready for external AI review.
