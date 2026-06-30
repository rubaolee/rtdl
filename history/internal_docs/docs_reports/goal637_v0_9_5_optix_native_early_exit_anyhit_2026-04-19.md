# Goal 637: v0.9.5 OptiX Native Early-Exit Any-Hit

Date: 2026-04-19

## Goal

Convert `ray_triangle_any_hit` on the OptiX backend from compatibility projection
(`ray_triangle_hit_count` followed by `hit_count > 0`) into a native OptiX
any-hit traversal that terminates the ray after the first accepted intersection.

## Reason

Goal 636 intentionally closed backend compatibility by projecting existing
hit-count rows. The user correctly challenged that this was not a native
early-exit implementation. Under the engine implementation priority policy,
OptiX is the first backend where new performance-sensitive RT features should
be implemented directly.

## Scope

- Add OptiX C ABI symbols:
  - `rtdl_optix_run_ray_anyhit`
  - `rtdl_optix_run_ray_anyhit_3d`
- Add 2-D and 3-D OptiX pipelines whose any-hit programs set payload `any_hit=1`
  and call `optixTerminateRay()`.
- Route Python `run_optix` / `prepare_optix` for `ray_triangle_any_hit` to the
  native any-hit symbols when available.
- Keep a stale-library fallback to hit-count projection only for dictionary
  mode; raw mode requires the new native symbols.

## Non-Scope

- No claim that Embree, HIPRT, Vulkan, or Apple RT now have native early-exit
  any-hit. They remain compatibility paths until separate goals implement native
  early-exit for those engines.
- No speedup claim until Linux measurements are recorded.

## Acceptance Bar

- Local Python tests for Goals 632, 633, and 636 must still pass.
- Linux OptiX build must succeed.
- Linux OptiX any-hit tests must prove parity with CPU/oracle for 2-D and 3-D
  fixtures.
- Any performance statement must distinguish native early-exit implementation
  from measured speedup.

## Implementation

- Added `RtdlRayAnyHitRow` and two OptiX C ABI entry points:
  - `rtdl_optix_run_ray_anyhit`
  - `rtdl_optix_run_ray_anyhit_3d`
- Added separate 2-D and 3-D OptiX pipelines derived from the existing
  ray-triangle hit-count kernels but with the any-hit shader changed to:
  - set payload `any_hit=1`
  - call `optixTerminateRay()`
- Updated Python OptiX dispatch so `ray_triangle_any_hit` uses the native
  any-hit ABI when present.
- Kept dictionary-mode fallback to hit-count projection for stale libraries.
- Raw OptiX row-view mode for `ray_triangle_any_hit` now requires the native
  symbols and returns `("ray_id", "any_hit")`.

## Validation

Local macOS focused tests:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal632_ray_triangle_any_hit_test \
  tests.goal633_visibility_rows_test \
  tests.goal636_backend_any_hit_dispatch_test \
  tests.goal637_optix_native_any_hit_test -v

Ran 18 tests in 0.035s
OK (skipped=5)
```

Linux OptiX build:

```text
ssh lestat-lx1
cd /tmp/rtdl_goal637_optix_anyhit
make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc

build/librtdl_optix.so built successfully
```

Linux focused OptiX/backend tests:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal637_optix_native_any_hit_test \
  tests.goal636_backend_any_hit_dispatch_test -v

Ran 9 tests in 5.485s
OK (skipped=4)
```

## Bounded Performance Observation

This is a bounded micro-result on `lestat-lx1`, not a broad release speedup
claim. Fixture: 5,000 2-D rays, 200 triangles, hit-dense geometry. Median of
three warmed runs:

| Path | Median seconds |
| --- | ---: |
| OptiX native any-hit | 0.0032699169969419017 |
| OptiX hit-count path | 0.02033192099770531 |

Observed ratio on this fixture: hit-count path / native any-hit path =
`6.217870672778597`.

This supports the design expectation that native early-exit helps dense-hit
cases. It does not prove broad speedup for sparse-hit cases, all devices, or all
backend implementations.

## Verdict

Codex verdict: ACCEPT for the OptiX-native early-exit slice.

External consensus:

- Gemini Flash review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal637_gemini_flash_review_2026-04-19.md`
  - Verdict: ACCEPT
- Claude review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal637_claude_review_2026-04-19.md`
  - Verdict: ACCEPT

Goal637 closure status: ACCEPTED with 3-AI consensus.
