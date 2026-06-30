# Goal 708: v1.0 Embree Baseline And NVIDIA RT-Core App Plan

Date: 2026-04-21
Status: accepted after Claude/Gemini/Codex consensus and required-plan fixes

## Consensus We Already Have

The v1.0 direction has two technical stages:

1. First, make Embree the mature local CPU RT baseline.
2. Then, move selected public apps to genuine NVIDIA RT-core execution through
   RTDL OptiX traversal and run cloud RTX validation only after local homework
   is ready.

This is the correct order. Embree lets RTDL prove the app/runtime contract on
machines we control, including the user's Windows 32-thread machine, before we
pay for cloud RTX time.

Release staging before v1.0:

- `v0.9.8`: development milestone. Finish the Embree multi-core baseline work,
  selected OptiX RT-core app implementation work, and full correctness/testing,
  including cloud RTX tests for targets that pass local readiness gates.
- `v0.9.9`: internal pre-release boosting milestone. Use all v0.9.8 evidence to
  optimize bottlenecks, tighten app interfaces, remove avoidable Python/native
  overhead, rerun full tests, and prepare release docs/audits.
- `v1.0`: public claim milestone. Publish only the app claims that survive
  v0.9.8 development/testing and v0.9.9 internal boosting without honesty
  boundary violations.

## Plan Review Consensus

- Codex: ACCEPT after applying required-plan fixes.
- Gemini Flash: ACCEPT. Gemini recommended ray-based Embree kernels first
  because they align directly with the later OptiX flagship path.
- Claude: ACCEPT with required changes. Claude recommended fixed-radius/KNN
  first because it solves variable-length row merging and covers more apps.

Resolution:

- Fixed-radius/KNN point queries go first for the Embree stage.
- Ray hit-count / closest-hit / any-hit go second.
- Rationale: fixed-radius/KNN is the harder and broader Embree dispatch
  contract because it requires deterministic variable-length per-query row
  merging. Once that is correct, scalar ray-query merging is simpler and can
  reuse the same thread-partitioning structure.

## Stage 1: Embree v1.0 Pre-Goal

### Goal

RTDL should fully use Embree's CPU RT capabilities for every eligible app core,
and the Embree engine should automatically dispatch independent RTDL probes
across multiple CPU cores by default, with user-configurable thread limits.

### Important Correction

Embree itself does not automatically make every RTDL app multi-threaded.
Embree provides CPU BVH/ray/point-query primitives and thread-safe traversal
patterns, but RTDL's current Embree backend often loops over probes, rays,
query points, graph frontiers, or DB predicates in RTDL C++ code.

Therefore the implementation target is:

> RTDL-controlled Embree parallel dispatch over independent query/probe/ray
> units, while preserving deterministic output and CPU-oracle parity.

### Required User-Facing Contract

- Default thread mode: `auto`.
- Environment override: `RTDL_EMBREE_THREADS=<N|auto|1>`.
- Optional Python API: `rt.configure_embree(threads=...)` or an equivalent
  scoped runtime setting if the existing runtime config pattern supports it.
- CLI apps should not require users to write threading code.
- Every report must record effective Embree thread count and whether execution
  used single-thread or multi-thread dispatch.

### Required Engineering Contract

- Parallelize independent query loops inside native Embree backend code.
- Partition query units into contiguous index ranges, one range per worker
  thread. Do not use work-stealing for the first v1.0 Embree implementation.
- Keep per-query scratch state thread-local or per-task.
- Accumulate results into thread-local output vectors.
- Merge per-thread row vectors deterministically after traversal by
  concatenating them in ascending worker/range order.
- Treat committed Embree scenes as read-only during dispatch. Any RTDL-owned
  mutable state must be thread-local or per-task before a kernel is declared
  parallel-safe.
- Preserve row ordering and exact parity against CPU reference.
- Keep prepared-scene reuse intact.
- Avoid parallelizing code paths that call non-thread-safe external state unless
  protected or isolated.
- Add phase timing for build, dispatch/traversal, materialization, and Python
  postprocess in benchmark scripts.

### Eligible App Groups

The Embree v1.0 pre-goal covers:

- Unified DB analytics.
- Unified graph analytics.
- Spatial radius/KNN apps.
- Segment/polygon apps.
- Hausdorff, ANN, outlier, DBSCAN, robot collision, and Barnes-Hut app cores
  where their RTDL core is currently expressed as KNN, fixed-radius, ray, or
  candidate generation.

Apps not yet eligible for a full Embree claim must be explicit:

- CPU-only polygon overlap/Jaccard apps need an Embree eligibility decision.
- Apple-specific and HIPRT-specific demos are not Embree app targets.

## Stage 2: NVIDIA RT-Core v1.0 Goal

### Goal

For selected public apps, the RTDL-owned acceleration core must genuinely use
NVIDIA RT cores through OptiX traversal on RTX-class hardware. Whole-app
performance should be optimized as far as practical without hiding
Python/interface/postprocess costs.

### Claim Rule

An app can enter NVIDIA RT-core claim review only when:

- the measured path uses OptiX traversal, such as `optixTrace`, over an OptiX
  acceleration structure;
- the benchmark ran on RTX-class NVIDIA hardware;
- the report splits native traversal from Python packing, copy-back,
  materialization, validation, and app postprocess;
- CPU/Embree correctness parity is proven for the same workload shape;
- the app output mode avoids unnecessary row materialization when the app only
  needs flags, counts, or summaries.

### Current Candidate Classes

Immediate flagship candidate:

- Robot collision / visibility / ray-triangle any-hit.

Near candidates after local phase-contract work:

- Outlier fixed-radius threshold summary.
- DBSCAN core-flag summary only, not full cluster expansion.

Needs native OptiX traversal design before claim:

- Graph analytics.
- Segment/polygon apps.
- DB analytics aggregation/materialization path.
- Hausdorff, ANN/KNN, and Barnes-Hut paper-derived apps.

Excluded from NVIDIA RT-core claims until redesigned:

- CUDA-through-OptiX row paths.
- Host-indexed fallback paths.
- CPU-only app scripts.
- Apple/HIPRT-specific demos.

## Proposed Goal Sequence

### Goal 708: v1.0 Plan And Consensus

Deliver this plan, get Claude and Gemini consensus, and record blockers.

### Goal 709: Embree Threading Contract

Add user-facing configuration and native runtime plumbing:

- `RTDL_EMBREE_THREADS`
- effective thread-count reporting
- deterministic behavior requirements
- contiguous query-unit range partitioning
- thread-local output vectors
- ascending worker/range-order merge
- read-only committed scene invariant
- tests that default mode is discoverable and invalid values fail clearly

### Goal 710: Embree Parallel Dispatch Implementation

Implement native Embree parallel loops for the highest-impact independent
probe families first:

- fixed-radius and KNN point queries
- ray hit-count / closest-hit / any-hit
- segment/polygon hit-count and any-hit rows

Then expand to:

- graph BFS/triangle probe
- DB conjunctive scan/grouped count/grouped sum

### Goal 711: Embree App Coverage And Performance Gate For v0.9.8

Run correctness and performance across the public app catalog on local macOS and
the Windows 32-thread machine:

- CPU oracle parity
- Embree single-thread vs auto-thread timing
- effective thread count
- phase splits
- deterministic output checks

Minimum workload floors for meaningful 32-thread validation:

- Fixed-radius and KNN: at least 50,000 query points against at least 500,000
  search/geometry primitives.
- Ray kernels: at least 100,000 rays.
- Graph BFS: at least 10,000 frontier nodes per expand step.
- DB scan/aggregation: at least 500,000 candidate rows.

These floors are workload-size requirements for meaningful measurement, not
speedup pass/fail thresholds.

### Goal 712: OptiX RT-Core App Conversion Plan For v0.9.8

Use the Embree baseline to prioritize OptiX traversal conversions:

- robot collision first
- outlier/DBSCAN bounded summaries second
- segment/polygon and graph native traversal next
- DB native aggregation/materialization path after interface bottlenecks are
  reduced

Entry gate:

- Goal 712 may not begin until Goal 711 passes for at least the robot collision
  app on both local macOS and the Windows 32-thread machine, including CPU
  oracle parity, phase-split timing, deterministic output verification, and
  auto-thread Embree execution.

### Goal 713: Cloud RTX Readiness Gate For v0.9.8

Only after Goal711 and targeted Goal712 subgoals pass locally, run cloud RTX
validation. Cloud tests must be narrow, repeatable, phase-split, and tied to a
specific app whose local contract is already clean.

### Goal 714: v0.9.8 Full Development/Test Closure

Close v0.9.8 only after:

- local full tests pass;
- Windows 32-thread Embree tests pass for the agreed workload floors;
- Linux/cloud RTX tests pass for every OptiX app claim included in v0.9.8;
- docs clearly separate Embree CPU RT acceleration, OptiX RT-core acceleration,
  CUDA-through-OptiX GPU compute, and Python app work;
- Claude/Gemini/Codex consensus reports are saved for plan, implementation,
  tests, docs, and audit.

### Goal 715: v0.9.9 Internal Pre-Release Boosting

Use v0.9.8 evidence to improve the whole-app bottlenecks before v1.0:

- reduce Python row materialization where app outputs only need flags, counts,
  or summaries;
- add prepared/prepacked APIs where repeated queries dominate;
- profile and fix native/Python boundary overhead;
- rerun all app benchmarks with phase splits;
- downgrade or exclude any app whose acceleration claim is not clean.

## Immediate Homework Before Cloud

Do not rent or keep an RTX cloud instance for broad app benchmarking yet.

Local homework comes first:

1. Add Embree thread configuration and reporting.
2. Parallelize one high-impact Embree kernel family.
3. Prove deterministic correctness.
4. Measure single-thread vs auto-thread locally.
5. Repeat on the Windows 32-thread machine.
6. Only then select the first OptiX cloud target for v0.9.8.
7. Use v0.9.8 cloud/local data to drive v0.9.9 boosting.

## Consensus Questions For Claude And Gemini

1. Is this v1.0 two-stage direction technically sound?
2. Is RTDL-controlled Embree parallel dispatch the right pre-goal before NVIDIA
   RT-core app work?
3. Are the proposed goals ordered correctly?
4. Which Embree kernel family should be implemented first for highest
   correctness/performance leverage?
5. Are any app groups incorrectly included or excluded?
