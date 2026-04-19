# Goal 544 External Review

Date: 2026-04-18
Reviewer: Claude (external AI review)

## Verdict: ACCEPT

Goal 544 satisfies all four review criteria.

## 1. Publicly documented

HIPRT is now visible in all required public surfaces:

- `README.md`: lists HIPRT under "Backend Names In Plain English" as
  "experimental post-`v0.8.0` backend bring-up surface"; includes a runnable
  preview block with explicit env-var setup; repeats the optional build step
  under "Optional experimental HIPRT backend build step on Linux"
- `docs/quick_tutorial.md`: calls out HIPRT as an experimental post-`v0.8.0`
  path, limited to 3D `ray_triangle_hit_count` on Linux hosts with HIPRT SDK
  runtime libraries, and provides the build/run steps
- `docs/release_facing_examples.md`: has a dedicated "Experimental HIPRT
  Preview" section with build and run commands, parity description, and an
  explicit current boundary table (supported vs. unsupported)
- `docs/current_architecture.md`: includes HIPRT in the backend table and
  correctly describes it as a narrower post-`v0.8.0` preview
- `docs/capability_boundaries.md`: has a "General HIPRT Backend Coverage"
  subsection under "What RTDL Cannot Do Yet" with an accurate and honest
  description of current limits

No doc overstates HIPRT as a released or general backend.

## 2. Runnable example

`examples/rtdl_hiprt_ray_triangle_hitcount.py` is correctly structured:

- always runs the CPU Python reference first (safe on any machine)
- wraps HIPRT in a `try/except (FileNotFoundError, OSError, RuntimeError)`
  block so unavailability is a clean JSON result, not a crash
- prints `hiprt_available: false` with the first error line when HIPRT is not
  present
- validates both `run_hiprt` one-shot and `prepare_hiprt` repeated-query
  parity when HIPRT is available
- the kernel form shown matches the actual RTDL DSL surface
  (`@rt.kernel`, `rt.input`, `rt.traverse`, `rt.refine`, `rt.emit`)

The example is suitable for public users on both HIPRT-equipped and
HIPRT-absent machines.

## 3. Tested on Linux

The internal report records a complete Linux HIPRT validation run:

- `make build-hiprt` produced `build/librtdl_hiprt.so` against
  `hiprtSdk-2.2.0e68f54`
- HIPRT probe returned device name `NVIDIA GeForce GTX 1070` (CUDA path via
  Orochi)
- parity gates all passed: `run_hiprt_first_batch`, `prepare_hiprt_first_batch`,
  `prepare_hiprt_second_batch` all `true`
- the targeted four-test-module bundle (`goal540`, `goal541`, `goal543`,
  `goal544`) ran 10 tests with `OK`

The test `goal544_hiprt_docs_examples_test.py` is a subprocess-level end-to-end
harness that parses JSON output, validates CPU reference values, and gates HIPRT
parity when HIPRT is available. It correctly skips parity assertions when HIPRT
is absent.

## 4. Honestly scoped without overstating release support

Every public surface uses consistent limiting language:

- "experimental post-`v0.8.0`" (not "released", not "v0.8.0")
- "not part of the released `v0.8.0` support matrix"
- "currently exposed only for 3D `ray_triangle_hit_count`"
- "no AMD GPU validation and no CPU fallback is claimed"
- capability_boundaries.md explicitly lists 2D RTDL semantics, DB workloads,
  graph workloads, nearest-neighbor workloads, AMD GPU, and CPU fallback as
  unsupported

No performance claim was added. No broader HIPRT workload coverage was implied.
The boundary between the released `v0.8.0` surface and this post-release preview
is clear and consistently stated across all modified docs.

## Summary

All four criteria are met: documented, runnable (safely degrades without HIPRT),
Linux-validated with a GTX 1070 CUDA/Orochi path, and honestly scoped. No
blocking issue found.
