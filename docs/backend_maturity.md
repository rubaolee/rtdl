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

For the released v0.9.5 any-hit layer, this means:

- OptiX, Embree, HIPRT, and current-main Vulkan have native early-exit any-hit
  implementations when the loaded backend libraries export them.
- Apple RT 3D on current `main` can use MPS RT nearest-intersection any-hit.
  Apple RT 2D on current `main` can use MPS prism traversal with per-ray mask
  early-exit plus exact 2D acceptance when `librtdl_apple_rt` is rebuilt.
- `reduce_rows` is a Python standard-library helper over emitted rows, not a
  backend-native reduction.

## Linux GPU Performance Notes

The current Linux GPU evidence has two layers:

- Goal560 is the canonical release smoke matrix: 18 workloads, 72
  backend/workload parity checks across Embree, OptiX, Vulkan, and HIPRT, all
  matching the CPU Python reference. It is not a throughput benchmark.
- Later external large-scale testing reported OptiX/Vulkan near-parity on the
  tested NVIDIA host, with HIPRT slower on database scans and failing one large
  graph BFS case with `std::bad_alloc`.

The large-scale result strengthens the existing maturity boundary rather than
changing it. Vulkan should be treated as a serious open GPU performance path on
that NVIDIA host. OptiX remains useful as the NVIDIA-specific RT backend.
HIPRT remains a real backend integration, but current evidence supports
correctness and API coverage, not broad performance leadership or memory-scaling
claims.

Do not describe HIPRT-on-NVIDIA/CUDA/Orochi measurements as AMD GPU results.
AMD GPU behavior remains unproven until tested on AMD hardware. Do not claim
large graph scalability for HIPRT until the graph representation and prepared
execution path have been memory-profiled and retested.

## Apple Metal/MPS RT

The Apple Metal/MPS backend is real Apple RT work, not a CPU fallback, for the
current native slices:

- 3D `ray_triangle_closest_hit`
- 3D `ray_triangle_hit_count`
- 2D `segment_intersection`

The v0.9.1 Apple RT slice was correctness-first. Released v0.9.4 work
adds prepared closest-hit reuse, masked chunked traversal for hit-count and
segment-intersection, expanded MPS RT geometry/nearest-neighbor slices, and
Metal compute/native-assisted DB and graph slices. Local Apple M4
measurements against Embree after Goal598 show:

Do not read "Apple RT backend" as "every Apple workload uses Apple
ray-tracing hardware." The DB and graph rows in the current Apple surface are
Apple GPU Metal-compute/native-assisted paths, not MPS ray-tracing traversal
paths.

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
> and native-assisted slices. Internal v0.9.2/v0.9.3 work reduces Apple RT
> overhead for prepared closest-hit, hit-count, and segment-intersection, and
> released v0.9.4 work extends DB/graph coverage through Metal compute, but Apple
> RT is still a bounded backend and not yet a broad performance-leading or
> mature-backend claim.

## Adaptive Native Engine

The adaptive native engine is paused work-in-progress. Earlier bounded pieces
exist, but unfinished Goal589 work is not release evidence. Do not use adaptive
engine files to support release claims unless that line is explicitly resumed,
tested, reviewed, and committed.
