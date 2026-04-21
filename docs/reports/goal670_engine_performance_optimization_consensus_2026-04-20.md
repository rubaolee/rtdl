# Goal670: Engine Performance Optimization Consensus

Date: 2026-04-20

Status: accepted as roadmap with notes by Codex, Claude, and Gemini 3 preview

## Purpose

Apply the Goal669 cross-engine optimization playbook to the three GPU RT
backends requested for this goal:

- OptiX: reviewed by Codex
- HIPRT: reviewed by Claude
- Vulkan: reviewed by Gemini 3 preview

Then cross-review each engine report with all three AIs and record consensus.

## Inputs

Playbook:

`/Users/rl2025/rtdl_python_only/docs/reports/goal669_cross_engine_performance_optimization_lessons_2026-04-20.md`

Primary engine reports:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal670_codex_optix_performance_optimization_review_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal670_claude_hiprt_performance_optimization_review_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal670_gemini3_vulkan_performance_optimization_review_2026-04-20.md`

Cross-consensus reviews:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal670_codex_engine_optimization_consensus_review_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal670_claude_engine_optimization_consensus_review_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal670_gemini_engine_optimization_consensus_review_2026-04-20.md`

Handoff files:

- `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL670_HIPRT_PERFORMANCE_OPTIMIZATION_REVIEW_REQUEST_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL670_VULKAN_PERFORMANCE_OPTIMIZATION_REVIEW_REQUEST_2026-04-20.md`
- `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL670_ENGINE_OPTIMIZATION_CONSENSUS_REVIEW_REQUEST_2026-04-20.md`

Note: `gemini-3-pro` was not available through the local Gemini CLI and returned
`ModelNotFoundError`. The review was completed with `gemini-3-pro-preview`.

## Per-Engine Consensus

### OptiX

Consensus verdict: ACCEPT WITH NOTES.

Agreed optimization priority:

1. Add prepared/prepacked ray-triangle any-hit for visibility and collision.
2. Add native scalar `any` / `count` output to avoid row materialization when
   the app only needs a summary.
3. Add phase-level profiling: prepare, pack, launch, wait, download, reduction,
   Python materialization.
4. Add reduced nearest-neighbor outputs for app contracts such as Hausdorff,
   outlier detection, and DBSCAN-style density.
5. Audit graph workloads before any OptiX graph performance claim.

Required claim boundaries:

- OptiX RT traversal, CUDA compute, and host-indexed C++ paths must be labeled
  separately.
- Current graph BFS and triangle-probe paths are host-indexed native C++ support,
  not OptiX RT traversal.
- GTX 1070 evidence is not RT-core evidence.
- Scalar-count speedups must not be compared against full emitted-row outputs
  without explicit output-contract disclosure.

### HIPRT

Consensus verdict: ACCEPT WITH NOTES.

Agreed optimization priority:

1. Add prepared 2D ray-triangle hit-count and any-hit.
2. Add prepared 3D any-hit so Goal639's early-exit kernel can show benefit
   without one-shot setup/JIT dominating timing.
3. Add prepared 2D nearest-neighbor.
4. Fix or gate the `k_max > 64` nearest-neighbor behavior.
5. Profile large-scale memory growth for prepared graph and DB contexts.
6. Consider shared HIPRT runtime/context pooling only after a safe lifetime
   design exists.

Required claim boundaries:

- Current HIPRT performance evidence is NVIDIA/Orochi CUDA evidence, not AMD GPU
  validation.
- GTX 1070 evidence is not RT-core evidence.
- Large-scale HIPRT claims are blocked until memory/OOM behavior is profiled.
- Broad kNN claims are blocked until the `k_max > 64` silent zero-result behavior
  is fixed or rejected at the API boundary.
- Device `float` precision versus host `double` precision must be disclosed for
  geospatial and precision-sensitive workloads.

### Vulkan

Consensus verdict: ACCEPT WITH NOTES.

Agreed optimization priority:

1. Add persistent BLAS/TLAS caching for static build-side geometry.
2. Add descriptor, staging-buffer, and output-buffer reuse.
3. Replace catastrophic `O(N*M)` output allocation with sparse/two-pass
   materialization or a bounded atomic-counter strategy.
4. Extend native early-exit to other boolean/any-hit predicates where the app
   contract allows it.
5. Separate Vulkan KHR ray tracing, Vulkan compute, CPU exact refinement, and
   Python materialization in every performance report.

Required claim boundaries:

- Large-scale Vulkan performance claims are blocked by the current worst-case
  output allocation until sparse/two-pass materialization exists.
- Jaccard CPU-oracle fallback must not be claimed as Vulkan acceleration.
- Driver and vendor variability must be reported.
- Future prepared/BVH-cached Vulkan benchmarks must report first-query,
  repeated-query, and break-even costs separately.

## Cross-Engine Consensus

All three AIs agree that Goal669 generalizes correctly:

- Prepared build-side state is mandatory for serious repeated-query performance.
- Prepacked probe-side buffers are needed when probe sets repeat.
- Reduced-output contracts are the next high-value optimization when apps need
  `any`, `count`, `min`, `max`, `sum`, or grouped summaries rather than full rows.
- Full row-output APIs remain the semantic source of truth for correctness.
- First-query and repeated-query timings must be separated.
- Backend mechanism honesty is mandatory: RT traversal, GPU compute, CPU
  fallback/refinement, and Python materialization must be identified separately.

## Roadmap Status

Accepted as optimization roadmap:

- OptiX prepared/prepacked scalar visibility.
- HIPRT prepared 2D ray/any-hit and kNN boundary fix.
- Vulkan acceleration-structure caching and sparse/two-pass output.

Blocked as release-facing claims until fixed or measured:

- HIPRT broad kNN support for `k_max > 64`.
- HIPRT AMD GPU performance.
- HIPRT large-scale graph/DB memory scaling.
- Vulkan large-scale LSI/PIP/overlay scaling under current `O(N*M)` allocation.
- Vulkan Jaccard acceleration while using CPU oracle fallback.
- OptiX graph acceleration while graph paths remain host-indexed C++.

## Final Verdict

ACCEPT WITH NOTES.

The Goal670 reports are valid as engineering roadmaps. They are not release
performance claims. The next implementation work should start with the highest
value and lowest ambiguity items:

1. OptiX prepared/prepacked ray-triangle scalar any/count.
2. HIPRT `k_max > 64` correctness gate plus prepared 2D any-hit.
3. Vulkan sparse/two-pass output allocation and acceleration-structure caching.
