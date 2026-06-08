# Goal3938 Current Benchmark Route Decision Registry

Date: 2026-06-08

## Purpose

Goal3938 adds a machine-readable current route decision registry:

- `rtdsl.current_benchmark_route_decisions()`
- `rtdsl.summarize_current_benchmark_route_decisions()`
- `rtdsl.explain_current_benchmark_route(app)`
- `rtdsl.validate_current_benchmark_route_decisions()`

This is the user-facing answer to: "For this benchmark contract, should I use an RTDL primitive, Numba, CuPy, or a mixed route?"

## Design Rule

The registry encodes the rule we now use across benchmark apps:

1. Prefer a fused generic RTDL primitive when it exactly expresses the answer.
2. Use Numba when custom scalar or row-stream logic wins and the user wants no RawKernel/CUDA-C code.
3. Keep CuPy only where it is honestly the fastest measured partner, while still exposing a Numba no-RawKernel reference where available.
4. Keep the user's partner/route choice explicit.
5. Do not auto-dispatch and do not promote slower candidates.

## Current Decisions

| App | Decision |
| --- | --- |
| `hausdorff_xhd` | Primitive-first RTDL/OptiX nearest-witness route |
| `spatial_rayjoin` | Mixed explicit route: Numba for bounded PIP one-shot; RTDL/OptiX for repeated PIP, LSI, and overlay active count |
| `rt_dbscan` | RTDL/OptiX grouped stream plus Numba continuation; blocked grouped stream remains unpromoted |
| `robot_collision` | Primitive-only prepared any-hit flag route |
| `contact_manifold` | Primitive-only bounded witness collection |
| `raydb_style` | Primitive-first fused grouped reductions |
| `barnes_hut` | RTDL/OptiX membership plus explicit partner force continuation; CuPy fastest measured, Numba no-RawKernel reference available |
| `librts_spatial_index` | Primitive-only prepared AABB index query |
| `rtnn` | Primitive-first prepared ranked-summary aggregate |
| `triangle_counting` | Primitive-first explicit native RT graph summary route |

## Why This Matters

Before Goal3938, a reader had to combine the adequacy registry, scale profile registry, Goal3936 clean pod artifact, and older partner-choice guidance to understand the current route story. That was accurate but too scattered.

Now the route decision is a first-class API and can be queried directly:

```python
import rtdsl as rt

print(rt.explain_current_benchmark_route("spatial_rayjoin")["current_reader_decision"])
```

## Boundary

This goal does not authorize release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, paper-reproduction wording, true-zero-copy wording, automatic partner selection, AMD performance wording, or app-specific native-engine logic.

It is a routing explanation and governance surface. It does not run new performance tests and does not change native engine behavior.
