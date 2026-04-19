# Goal578: v0.9.1 Apple RT Backend Bring-Up

Status: implemented, external AI reviewed, accepted

Date: 2026-04-18 local EDT

## Purpose

Goal578 starts the v0.9.1 Apple-chip RT line with a narrow, honest backend surface: 3D `ray_triangle_closest_hit` through Apple Metal/MPS ray intersection on macOS Apple Silicon.

This is not a full parity claim with Embree, OptiX, Vulkan, or HIPRT. It is the first verified Apple RT backend slice.

## Host And SDK Facts

- Repo: `/Users/rl2025/rtdl_python_only`
- Branch at implementation time: `main`
- Base version: `v0.9.0`
- Host OS: macOS Darwin arm64
- CPU: Apple M4
- Local SDK path: `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk`
- Metal framework exists: `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/System/Library/Frameworks/Metal.framework`
- MetalPerformanceShaders framework exists: `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/System/Library/Frameworks/MetalPerformanceShaders.framework`
- MPSRayIntersector headers exist under `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/System/Library/Frameworks/MetalPerformanceShaders.framework/Versions/A/Frameworks/MPSRayIntersector.framework/Headers`
- Standalone `metal` CLI is not available through Command Line Tools on this host, so this first slice intentionally uses Objective-C++ and MPSRayIntersector without an offline Metal shader build dependency.

## Files Changed

- `/Users/rl2025/rtdl_python_only/Makefile`
- `/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal578_apple_rt_backend_test.py`

## Implementation Summary

- Added `make build-apple-rt`.
- Added native library target: `/Users/rl2025/rtdl_python_only/build/librtdl_apple_rt.dylib`.
- Added Objective-C++ backend using `MPSRayIntersector` and `MPSTriangleAccelerationStructure`.
- Added C ABI:
  - `rtdl_apple_rt_get_version`
  - `rtdl_apple_rt_context_probe`
  - `rtdl_apple_rt_free_rows`
  - `rtdl_apple_rt_run_ray_closest_hit_3d`
- Added Python runtime:
  - `rt.apple_rt_version()`
  - `rt.apple_rt_context_probe()`
  - `rt.ray_triangle_closest_hit_apple_rt(...)`
  - `rt.run_apple_rt(...)`
- `run_apple_rt` currently supports only `ray_triangle_closest_hit` kernels over 3D rays and 3D triangles.

## Correctness Evidence

Build command:

```bash
cd /Users/rl2025/rtdl_python_only
make build-apple-rt
```

Result: pass, produced `/Users/rl2025/rtdl_python_only/build/librtdl_apple_rt.dylib`.

Focused test command:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test -v
```

Result:

```text
Ran 4 tests in 0.010s
OK
```

The test covers:

- version query
- Metal/MPS context probe
- direct Apple RT closest-hit helper parity with `rt.ray_triangle_closest_hit_cpu`
- `rt.run_apple_rt(...)` parity with `rt.run_cpu_python_reference(...)`
- empty-triangle behavior returning no rows

## Important Fix During Bring-Up

The first test run exposed an ABI mismatch: Python packed `RtdlRay3D` and `RtdlTriangle3D` records but the new native Objective-C++ structs used default C++ alignment. This caused MPS to receive malformed ray/triangle data and return no hit. The native structs are now explicitly packed to match the Python ctypes ABI.

The first test run also exposed a dispatch bug: `run_apple_rt` initially looked for `compiled.candidates.predicate`; the RTDL IR stores the predicate at `compiled.refine_op.predicate`. This is fixed.

## Honesty Boundary

- This backend uses Apple Metal/MPS ray-intersection APIs.
- This report does not claim full v0.9.1 release readiness.
- This report does not claim complete workload parity.
- This report does not claim a measured Apple hardware RT-core speedup.
- This first slice is correctness-credible for bounded 3D closest-hit ray/triangle traversal on the local Apple M4 host.

## External Reviews

- Gemini review: `/Users/rl2025/rtdl_python_only/docs/reports/goal578_gemini_flash_review_2026-04-18.md`
- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal578_claude_review_2026-04-18.md`

Both external reviews returned ACCEPT with no blockers.

## Current Verdict

Codex local verdict: ACCEPT for Goal578 as a first Apple RT backend bring-up slice.
