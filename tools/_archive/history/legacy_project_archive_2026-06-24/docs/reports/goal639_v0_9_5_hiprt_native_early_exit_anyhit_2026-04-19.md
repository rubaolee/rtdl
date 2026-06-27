# Goal 639: v0.9.5 HIPRT Native Early-Exit Any-Hit

Date: 2026-04-19

## Goal

Upgrade HIPRT `ray_triangle_any_hit` from the Goal636 compatibility path
(`ray_triangle_hit_count` followed by `hit_count > 0`) to a HIPRT-native
any-hit path that stops the HIPRT traversal loop after the first accepted
triangle hit.

This follows the engine priority policy recorded in `/Users/rl2025/refresh.md`:
OptiX first, then Embree/HIPRT, then Vulkan, then Apple Metal/MPS RT.

## Implementation

Changed files:

- `/Users/rl2025/rtdl_python_only/src/native/hiprt/rtdl_hiprt_prelude.h`
- `/Users/rl2025/rtdl_python_only/src/native/hiprt/rtdl_hiprt_core.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/hiprt/rtdl_hiprt_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/hiprt_runtime.py`
- `/Users/rl2025/rtdl_python_only/tests/goal639_hiprt_native_any_hit_test.py`
- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/features/ray_tri_anyhit/README.md`
- `/Users/rl2025/rtdl_python_only/docs/features/visibility_rows/README.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/visibility_runtime.py`

Native ABI added:

- `rtdl_hiprt_run_ray_anyhit_2d`
- `rtdl_hiprt_run_ray_anyhit_3d`

Python dispatch added:

- `_RtdlRayAnyHitRow`
- `ray_triangle_any_hit_2d_hiprt(...)`
- `ray_triangle_any_hit_3d_hiprt(...)`
- `ray_triangle_any_hit_hiprt(...)` now prefers the native symbols when loaded
- stale-library fallback still projects hit-count rows to any-hit rows when the
  native symbols are absent

The native implementation reuses the existing HIPRT geometry and intersection
setup for 2D and 3D ray/triangle traversal, but specializes the kernel row type
and traversal body:

```cpp
if (hit.hasHit()) {
    any_hit = 1u;
    break;
}
```

## Boundary

This is a genuine HIPRT backend implementation because it goes through the
HIPRT geometry, HIPRT traversal, Orochi launch, and HIPRT row return path.

The performance claim is intentionally bounded:

- It is native early-exit at the RTDL HIPRT kernel loop level.
- On the current Linux validation machine it runs through HIPRT/Orochi on an
  NVIDIA GTX 1070 path, not an AMD GPU path.
- The whole-call timing still includes HIPRT setup, geometry build, and kernel
  compilation, so Goal639 does not claim a measured end-to-end speedup.
- Vulkan and Apple RT remain compatibility paths for this predicate.

## Validation

Local macOS focused test:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal639_hiprt_native_any_hit_test \
  tests.goal636_backend_any_hit_dispatch_test \
  tests.goal637_optix_native_any_hit_test \
  tests.goal638_embree_native_any_hit_test

Ran 14 tests in 0.028s
OK (skipped=8)
```

HIPRT is unavailable on the Mac, so the HIPRT-specific tests skipped locally.
The same run confirmed Embree/Apple compatibility did not regress.

Linux validation host:

```text
ssh lestat-lx1
cd /tmp/rtdl_goal639_hiprt_anyhit
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
```

Build result:

```text
build/librtdl_hiprt.so built successfully
```

Linux focused test:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal639_hiprt_native_any_hit_test \
  tests.goal636_backend_any_hit_dispatch_test

Ran 10 tests in 2.824s
OK (skipped=4)
```

The Linux test verifies:

- HIPRT exports `rtdl_hiprt_run_ray_anyhit_2d`.
- HIPRT exports `rtdl_hiprt_run_ray_anyhit_3d`.
- 2D HIPRT native any-hit matches the CPU oracle through `run_hiprt`.
- 2D HIPRT native any-hit matches the CPU oracle through the direct Python
  helper.
- 3D HIPRT native any-hit matches the CPU oracle through `run_hiprt`.
- 3D HIPRT native any-hit matches the CPU oracle through the direct Python
  helper.

Dense-hit sanity timing on Linux:

```text
1500 rays, 150 triangles
HIPRT any-hit median whole-call time: 0.614094397998997 s
HIPRT hit-count median whole-call time: 0.6094138070038753 s
hit-count / any-hit ratio: 0.9923780594475813
```

Interpretation: the native any-hit path is correct and structurally early-exit,
but whole-call timing is dominated by setup/JIT/build overhead in this unprepared
path. No speedup claim is made from this measurement.

## Documentation Updates

Public docs now state:

- OptiX, Embree, and HIPRT have native any-hit paths.
- Vulkan and Apple RT remain bounded compatibility paths for any-hit.
- HIPRT native any-hit is validated on the current Linux NVIDIA/Orochi path and
  should not be overclaimed as AMD-GPU performance evidence.

## Codex Verdict

ACCEPT for the Goal639 HIPRT native any-hit implementation.

## 3-AI Consensus

Codex verdict: ACCEPT.

Claude review:

- File: `/Users/rl2025/rtdl_python_only/docs/reports/goal639_claude_review_2026-04-19.md`
- Verdict: ACCEPT.
- Main finding: the `any_hit = 1u; break;` substitution lands inside the HIPRT
  traversal loop, the 2D/3D native ABI symbols are exported, Python prefers
  native symbols with stale-library fallback, and the docs avoid performance
  overclaiming.

Gemini Flash review:

- File: `/Users/rl2025/rtdl_python_only/docs/reports/goal639_gemini_flash_review_2026-04-19.md`
- Verdict: ACCEPT.
- Note: an earlier broad Gemini prompt declined review due scope/domain limits;
  the narrower file-specific review produced the recorded ACCEPT verdict.

Remaining future work:

- A prepared HIPRT any-hit path would be needed before making meaningful
  whole-call performance claims.
- Vulkan native early-exit any-hit remains a later lower-priority backend goal.
- Apple RT remains constrained by Metal/MPS RT API shape and should not be
  forced into a fake hardware-backed claim.
