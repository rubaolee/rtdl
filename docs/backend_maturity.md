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
| Apple Metal/MPS RT | Implemented for bounded native slices | Correct with v0.9.2 overhead reductions; still not a broad speedup claim and Embree remains faster on current hit-count/segment fixtures |
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

The v0.9.1 Apple RT slice was correctness-first. Current v0.9.2 candidate work
adds prepared closest-hit reuse and masked chunked traversal for hit-count and
segment-intersection to reduce repeated setup overhead. Local Apple M4
measurements against Embree after Goal598 show:

| Workload | Embree median | Apple RT median | Apple RT vs Embree |
| --- | ---: | ---: | ---: |
| 3D `ray_triangle_closest_hit` | 0.002708896 s | 0.001413271 s | about 0.52x Apple/Embree, but unstable |
| 3D `ray_triangle_hit_count` | 0.002438146 s | 0.114898792 s | about 47.13x slower |
| 2D `segment_intersection` | 0.007503292 s | 0.031314438 s | about 4.17x slower |

Evidence artifact:

```text
/Users/rl2025/rtdl_python_only/docs/reports/goal598_post_masked_segment_intersection_perf_macos_2026-04-19.json
```

The segment-intersection path improved from the latest pre-Goal598 local
artifact:

| Artifact | Apple RT segment median | Apple RT vs Embree |
| --- | ---: | ---: |
| Goal597 post-hitcount artifact | 0.092515083 s | about 11.87x slower |
| Goal598 post-segment artifact | 0.031314438 s | about 4.17x slower |

The main reason for the remaining gap is still implementation maturity and
dense-output enumeration cost. Goal597 and Goal598 reduce repeated
acceleration-structure setup with masked chunked nearest-hit traversal, but they
do not make the Apple backend broadly mature or generally faster than Embree.
Therefore the correct claim is:

> Apple Metal/MPS RT is implemented and correctness-validated for bounded native
> slices. Current v0.9.2 work reduces Apple RT overhead for prepared closest-hit,
> hit-count, and segment-intersection, but Apple RT is still a bounded backend
> and not yet a broad performance-leading or mature-backend claim.

## Adaptive Native Engine

The adaptive native engine is paused work-in-progress. Earlier bounded pieces
exist, but unfinished Goal589 work is not release evidence. Do not use adaptive
engine files to support release claims unless that line is explicitly resumed,
tested, reviewed, and committed.
