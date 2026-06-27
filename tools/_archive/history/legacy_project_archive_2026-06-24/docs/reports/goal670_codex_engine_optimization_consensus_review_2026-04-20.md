# Goal670: Codex Engine Optimization Consensus Review

Date: 2026-04-20

Reviewer: Codex

Reports reviewed:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal670_codex_optix_performance_optimization_review_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal670_claude_hiprt_performance_optimization_review_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal670_gemini3_vulkan_performance_optimization_review_2026-04-20.md`

## Overall Verdict

ACCEPT WITH NOTES.

The three reports are suitable as performance-optimization roadmaps, not as
release performance claims. Each report correctly applies the Goal669 playbook:
separate setup from repeated query, separate full rows from reduced outputs,
and separate actual backend mechanism from public API support.

## OptiX Report Verdict

ACCEPT WITH NOTES.

The OptiX roadmap is technically valid. The strongest near-term target is
prepared/prepacked ray-triangle any-hit with scalar count/any output, because
OptiX already has true programmable any-hit with `optixTerminateRay()` and a
measured dense-hit micro-speedup.

Accepted priorities:

- prepared triangle GAS reuse plus prepacked rays;
- scalar `count`/`any` output to avoid row materialization;
- reduced nearest-neighbor outputs for app contracts such as Hausdorff,
  outlier detection, and DBSCAN-style density tests;
- DB grouped-reduction profiling before implementing GPU grouping;
- graph mechanism audit before any OptiX graph acceleration claim.

Required notes:

- CUDA compute under the OptiX backend is not the same as OptiX RT traversal.
- Current graph paths are host-indexed support, not OptiX RT acceleration.
- Reduced-output speedups must not be compared against full emitted rows
  without output-contract disclosure.

## HIPRT Report Verdict

ACCEPT WITH NOTES.

Claude's HIPRT report is technically grounded and more detailed than a simple
roadmap. It correctly identifies that prepared contexts are the key HIPRT
performance mechanism, and it keeps the NVIDIA/Orochi boundary explicit.

Accepted priorities:

- prepared 2D ray/triangle hit-count and any-hit;
- prepared 3D any-hit to expose Goal639's early-exit benefit;
- prepared 2D nearest-neighbor;
- device-side grouped DB aggregation only after profiling;
- shared HIPRT runtime/context pooling after correctness-safe lifetime design.

Required notes:

- No AMD GPU validation exists; all current performance evidence is
  NVIDIA/Orochi CUDA.
- GTX 1070 results are not RT-core evidence.
- HIPRT float-device precision must be disclosed for geometry-sensitive cases.
- OOM behavior at large scale remains unquantified.
- The `k_max > 64` silent zero-result behavior in HIPRT NN kernels is a
  correctness blocker for broad kNN claims until fixed or rejected at the API
  boundary.

## Vulkan Report Verdict

ACCEPT WITH NOTES.

Gemini 3 preview's Vulkan report identifies the right bottlenecks: repeated
BLAS/TLAS rebuild, transient descriptor/buffer allocation, catastrophic
worst-case output allocation, and limited early-exit coverage.

Accepted priorities:

- persistent acceleration-structure caching for static build-side geometry;
- descriptor set, pipeline, staging, and output buffer reuse;
- sparse/two-pass output materialization to avoid `O(P * Q)` memory blowups;
- extend native early-exit to other boolean/any-hit workloads;
- classify Jaccard and complex geometry work honestly before performance
  claims.

Required notes:

- Vulkan driver variability requires hardware-specific validation.
- Any large-scale Vulkan claim is blocked until worst-case output memory
  allocation is fixed or bounded by a disclosed contract.
- Native Vulkan RT, Vulkan compute, and host exact refinement must be reported
  separately.

## Shared Consensus Direction

The next implementation wave should not try to optimize every workload at once.
The common high-value pattern is:

1. Pick one workload with a stable build side and repeated probes.
2. Add prepared build-side backend state.
3. Add prepacked probe buffers.
4. Add reduced output only when the app contract needs a scalar or grouped
   result.
5. Add phase-level profiling.
6. Compare first-query, repeated-query, and break-even behavior.
7. Keep full row output as the correctness source of truth.

Best first candidates by engine:

- OptiX: prepared/prepacked ray-triangle scalar any/count.
- HIPRT: prepared 2D ray-triangle any-hit, then fix `k_max > 64`.
- Vulkan: acceleration-structure caching and sparse/two-pass output before
  new performance claims.

## Final Codex Consensus

ACCEPT WITH NOTES.

No report is blocked as a roadmap. Several claims are blocked until specific
evidence or fixes exist, especially HIPRT broad kNN claims, HIPRT AMD GPU
claims, and Vulkan large-scale scaling claims.
