# Goal 640: v0.9.5 Any-Hit / Visibility Backend Support Audit

Date: 2026-04-19

## Purpose

After adding native any-hit paths for OptiX, Embree, and HIPRT, audit whether
the full public backend set supports the v0.9.5 any-hit / visibility surface
honestly enough for the release line:

- CPU / Python oracle
- Embree
- OptiX
- Vulkan
- HIPRT
- Apple RT

## Support Matrix

| Backend | `ray_triangle_any_hit` support | `visibility_rows(..., backend=...)` support | Current claim |
| --- | --- | --- | --- |
| CPU / Python oracle | Native reference implementation | Native standard-library helper | Correctness oracle |
| Embree | Native early-exit via `rtcOccluded1` | Uses native any-hit dispatch | Native early-exit |
| OptiX | Native early-exit via `optixTerminateRay()` | Uses native any-hit dispatch | Native early-exit |
| HIPRT | Native HIPRT traversal-loop early exit | Uses native any-hit dispatch when symbols are present | Native early-exit at RTDL HIPRT kernel-loop level |
| Vulkan | Backend compatibility by projecting hit-count rows | Uses backend compatibility dispatch | Correct backend execution, no native early-exit claim |
| Apple RT | Backend compatibility by projecting hit-count rows | Uses Apple RT compatibility dispatch | Correct backend execution, no native early-exit claim |

## Why Vulkan Does Not Block v0.9.5

Vulkan is the third-priority engine under `/Users/rl2025/refresh.md`.

Current Vulkan any-hit correctness is present: `run_vulkan` executes the
Vulkan ray-triangle hit-count path and projects `hit_count > 0` to `any_hit`.
The focused Linux test confirms this matches the CPU oracle. Raw mode remains
intentionally rejected for Vulkan any-hit because the current native row view is
still a hit-count view.

This is acceptable for v0.9.5 because:

- the release goal is to expose and validate bounded any-hit / visibility
  semantics across public engines;
- Vulkan correctly executes the backend traversal path;
- docs explicitly avoid native early-exit performance claims for Vulkan;
- OptiX, Embree, and HIPRT already cover the high-priority native early-exit
  implementations.

Native Vulkan early-exit can be a future optimization goal, but it should not
block this version unless the release definition changes.

## Why Apple RT Does Not Block v0.9.5

Apple RT is the fourth-priority engine under `/Users/rl2025/refresh.md`.

The Apple RT path supports the any-hit and visibility row contracts through its
existing Apple RT compatibility dispatch. It is tested locally on Apple M4 and
matches CPU. The docs avoid saying this is a specialized Apple hardware
early-exit shader.

This is acceptable for v0.9.5 because:

- Apple RT correctness is present for the public row contract;
- the release does not claim Apple native early-exit performance;
- the project policy explicitly allows API/hardware-constrained Apple features
  to remain correct compatibility paths instead of fake hardware-backed claims.

## Validation Evidence

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

Relevant local coverage:

- Embree any-hit matches CPU.
- Apple RT any-hit with `native_only=True` matches CPU.
- `visibility_rows(..., backend="embree")` matches CPU.
- `visibility_rows(..., backend="apple_rt", native_only=True)` matches CPU.
- HIPRT/OptiX/Vulkan skipped locally because their libraries are not built on
  this Mac checkout.

Linux host `/tmp/rtdl_goal639_hiprt_anyhit` backend probes:

```text
embree OK (4, 3, 0)
optix OK (9, 0, 0)
vulkan OK (0, 1, 0)
hiprt OK {'version': (2, 2, 15109972), 'api_version': 2002,
          'device_type': 1, 'device_name': 'NVIDIA GeForce GTX 1070'}
```

Linux focused test after rebuilding OptiX, Vulkan, and HIPRT:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal636_backend_any_hit_dispatch_test \
  tests.goal637_optix_native_any_hit_test \
  tests.goal638_embree_native_any_hit_test \
  tests.goal639_hiprt_native_any_hit_test

Ran 14 tests in 3.758s
OK (skipped=2)
```

Relevant Linux coverage:

- Embree any-hit matches CPU.
- OptiX any-hit matches CPU.
- Vulkan any-hit matches CPU through compatibility dispatch.
- HIPRT any-hit matches CPU through native 2D/3D symbols.
- OptiX native raw any-hit rows expose `("ray_id", "any_hit")`.
- Embree native raw any-hit rows expose `("ray_id", "any_hit")`.
- HIPRT native 2D/3D any-hit symbols are exported.
- Apple RT skips on Linux as expected.

## Documentation Check

Public documentation now states:

- OptiX, Embree, and HIPRT have native any-hit paths.
- Vulkan and Apple RT are compatibility paths for this predicate.
- Compatibility paths are real backend execution, not native early-exit
  performance evidence.

Files checked:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/features/ray_tri_anyhit/README.md`
- `/Users/rl2025/rtdl_python_only/docs/features/visibility_rows/README.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/visibility_runtime.py`

## Codex Verdict

ACCEPT.

The v0.9.5 any-hit / visibility row surface is supported across the public
backend set under honest backend-specific claims. Vulkan and Apple RT should
remain compatibility paths for this release unless a later explicit goal adds
native early-exit implementations and validation.

## 2-AI Consensus

Codex verdict: ACCEPT.

Claude external review:

- File: `/Users/rl2025/rtdl_python_only/docs/reports/goal640_external_review_2026-04-19.md`
- Verdict: ACCEPT.
- Main finding: the backend support matrix is honest, Vulkan/Apple RT
  compatibility paths are correctly scoped, and deferring native early-exit for
  those lower-priority engines should not block v0.9.5.
