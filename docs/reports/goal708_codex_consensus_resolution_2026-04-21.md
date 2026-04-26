# Goal 708: Codex Consensus Resolution

Date: 2026-04-21
Status: accepted

## Inputs

- Primary plan:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal708_v1_0_embree_then_nvidia_rt_core_plan_2026-04-21.md`
- Claude review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal708_claude_plan_review_2026-04-21.md`
- Gemini Flash review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal708_gemini_flash_plan_review_2026-04-21.md`

## Consensus

All reviewers agree on the high-level v1.0 direction:

1. Make Embree the mature local CPU RT baseline first.
2. Then move selected public apps to genuine NVIDIA RT-core OptiX traversal
   claims after local correctness, determinism, phase-split, and Embree
   baseline gates.
3. Do not start broad paid RTX cloud benchmarking until the local gates are
   clean.

## Resolved Disagreement

Gemini recommended starting Embree parallelization with ray-based queries
because that aligns directly with the later OptiX flagship app path.

Claude recommended starting with fixed-radius/KNN because that is the harder
and broader Embree problem: it forces deterministic variable-length per-query
row merging and covers service coverage, event hotspot, KNN assignment,
outlier detection, DBSCAN, Hausdorff, ANN, and Barnes-Hut candidate paths.

Codex resolution:

- Start Embree implementation with fixed-radius/KNN point queries.
- Implement ray hit-count / closest-hit / any-hit second.

Reason:

- The Embree pre-goal is about mature CPU RT coverage across apps, not only the
  later OptiX flagship.
- Variable-length output merging is the harder common infrastructure.
- Ray scalar outputs are important but easier once the thread partitioning and
  deterministic merge contract exists.

## Required Plan Fixes Applied

- Added contiguous query-unit range partitioning.
- Added thread-local output vectors.
- Added ascending worker/range-order merge.
- Added read-only committed-scene invariant.
- Reordered Goal710 kernel families to fixed-radius/KNN first, ray queries
  second.
- Added Goal712 entry gate requiring Goal711 robot-collision success on macOS
  and Windows 32-thread machine before OptiX conversion begins.
- Added minimum workload floors for meaningful 32-thread performance
  measurement.

## Decision

Goal708 is accepted. Next implementation goal is Goal709: Embree threading
configuration and deterministic dispatch contract.
