# RTDL Backend Maturity

This page separates three different claims that are easy to confuse:

- implemented: the backend exists and can be called through RTDL
- correctness-validated: bounded tests show parity with the reference/oracle for supported workloads
- optimized: the backend is mature enough for performance-facing claims

RTDL should not describe every implemented backend as optimized.

## Current Summary

| Backend | Current status | Honest performance claim |
| --- | --- | --- |
| Embree | Mature RTDL CPU backend | Optimized enough for current RTDL performance-facing claims |
| OptiX | Implemented for supported Linux/NVIDIA workloads | Real RT backend; performance is workload-dependent and not a broad speedup claim |
| Vulkan | Implemented for supported workloads | Real backend and portability path; not consistently optimized |
| HIPRT | Implemented for the accepted HIPRT matrix, including the current CUDA/NVIDIA compatibility path | Correctness-focused HIPRT integration; not a broad speedup claim |
| Apple Metal/MPS RT | Implemented for bounded native slices | Correct but currently unoptimized; local Apple M4 data shows Embree faster |
| CPU/Python reference | Correctness oracle and fallback | Not a performance backend |
| Adaptive native engine | Paused work-in-progress | Not release evidence and not an optimized backend claim |

## Optimized Today

Embree is the only backend RTDL should currently describe as optimized or mature
by release-document standards. It is the strongest practical backend in the
current tree for broad local CPU execution and has the deepest workload coverage
and regression evidence.

This does not mean Embree wins every possible future workload. It means current
RTDL evidence supports Embree as the one backend that can be advertised as a
mature optimized engine.

## Implemented But Bounded

OptiX, Vulkan, HIPRT, and Apple Metal/MPS RT are real backend integrations. They
should be described as implemented and correctness-validated only where the
release reports provide evidence.

They should not be described as generally optimized or performance-leading.
Their correct public framing is:

- real backend path
- bounded workload support
- reference/oracle parity where tested
- measured performance varies by workload, host, and implementation maturity

## Apple Metal/MPS RT

The Apple Metal/MPS backend is real Apple RT work, not a CPU fallback, for the
current native slices:

- 3D `ray_triangle_closest_hit`
- 3D `ray_triangle_hit_count`
- 2D `segment_intersection`

However, it is currently unoptimized. Local Apple M4 measurements against Embree
show:

| Workload | Embree median | Apple RT median | Apple RT vs Embree |
| --- | ---: | ---: | ---: |
| 3D `ray_triangle_closest_hit` | 0.000204 s | 0.001802 s | about 8.8x slower |
| 3D `ray_triangle_hit_count` | 0.000203 s | 0.338369 s | about 1664x slower |
| 2D `segment_intersection` | 0.010139 s | 0.095927 s | about 9.5x slower |

Evidence artifact:

```text
/Users/rl2025/rtdl_python_only/docs/reports/apple_rt_vs_embree_perf_macos_2026-04-19.json
```

The main reason is implementation structure: the current Apple hit-count and
segment-intersection paths rebuild small MPS acceleration structures repeatedly,
so setup and dispatch overhead dominate. Therefore the correct claim is:

> Apple Metal/MPS RT is implemented and correctness-validated for bounded native
> slices, but currently unoptimized and not performance-competitive with Embree
> on the local Apple M4 measurements.

## Adaptive Native Engine

The adaptive native engine is paused work-in-progress. Earlier bounded pieces
exist, but unfinished Goal589 work is not release evidence. Do not use adaptive
engine files to support release claims unless that line is explicitly resumed,
tested, reviewed, and committed.

