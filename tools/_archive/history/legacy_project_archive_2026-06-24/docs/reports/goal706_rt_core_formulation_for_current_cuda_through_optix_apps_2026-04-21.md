# Goal706: RT-Core Formulation For Current CUDA-Through-OptiX Apps

Date: 2026-04-21

Status: design report pending external AI review

## Why This Goal Exists

Goal705 conservatively excluded Hausdorff, ANN/KNN, and Barnes-Hut from RTX
RT-core app claims today. That exclusion is not a fundamental statement that
these workloads cannot use ray tracing. It only says the current RTDL
implementations do not yet lower their dominant work to OptiX ray traversal in
a way we can honestly benchmark as RT-core acceleration.

The project direction remains: RTDL should grow the language/runtime by
building real apps and progressively replacing CUDA-through-OptiX or host-side
paths with explicit RT formulations when the formulation is technically sound.

## Paper Evidence Read For This Goal

Local paper inputs:

- `/Users/rl2025/Downloads/2026-xhd (1).pdf`
- `/Users/rl2025/Downloads/2303.09655v1.pdf`
- `/Users/rl2025/Downloads/3650200.3656601.pdf`
- `/Users/rl2025/Downloads/3710848.3710885 (1).pdf`

Relevant conclusions:

- X-HD shows Hausdorff distance can be accelerated with RT cores by reducing
  nearest-neighbor subproblems to ray/AABB traversal, but it also shows that
  naive one-point-per-AABB RT KNN is not enough. High performance requires
  grid grouping, HD estimators, early break, and load-balance-aware fallback
  to CUDA kernels.
- RT-DBSCAN shows fixed-radius neighbor discovery can be reduced to ray
  tracing by expanding spheres/AABBs around data points and launching
  point-rays from query points. This validates RTDL's current fixed-radius
  `rt_count_threshold` and `rt_core_flags` direction, but full DBSCAN still
  needs explicit separation between RT core-flag discovery and cluster
  expansion.
- Arkade shows KNN/ANN-like workloads can be extended beyond Euclidean
  distance by using filter-refine or monotone transformation reductions. RTDL
  should expose this as bounded candidate generation plus exact/refined
  distance ranking, not as a generic "RT cores solve all ANN" claim.
- RT-BarnesHut shows Barnes-Hut can be reformulated for ray tracing by building
  the Barnes-Hut tree separately, representing tree nodes as RT scene objects,
  launching rays whose intervals encode the opening criterion, and using
  intersection results plus autoropes to emulate tree traversal decisions.
  This is a real RT formulation, but it is a new algorithmic path, not the same
  as RTDL's current CUDA-through-OptiX Barnes-Hut app.

## What "CUDA-Through-OptiX" Means In RTDL Today

The current apps may use files, build systems, or dispatch code under the OptiX
backend, but their dominant work is not necessarily `optixTrace` traversal over
an RT scene.

That distinction matters because:

- NVIDIA RT-core claims require the key operation to be BVH traversal /
  intersection work, not merely CUDA kernels compiled next to OptiX code.
- A CUDA-through-OptiX app can still be useful GPU acceleration.
- A CUDA-through-OptiX app must be benchmarked as GPU compute unless and until
  its dominant operation is reimplemented as a real traversal/intersection
  primitive.

## Target Workload Designs

### Hausdorff Distance

Current status: excluded from RT-core app claims today because the current app
uses KNN-style GPU compute through the OptiX backend rather than a validated
X-HD-style RT formulation.

Target RTDL design:

- Build a uniform grid over target points.
- Represent non-empty cells as AABBs expanded by the current search radius.
- Launch query rays/point-rays to find candidate cells through RT traversal.
- Refine candidate cells with exact point distances.
- Maintain nearest-neighbor distance per query.
- Apply Hausdorff-specific pruning:
  - lower/upper HD estimators;
  - early break when a query point cannot improve the current max;
  - selective CUDA fallback for high-load cells.

First implementable RTDL slice:

- `rt.hausdorff_candidates(...)`: returns bounded candidate cells/points for
  each query point using RT traversal.
- Python/app layer computes exact nearest distances and final max distance.
- Correctness oracle compares against CPU exact Hausdorff.

Performance claim boundary:

- Before the full X-HD-style algorithm exists, we may claim only
  RT-assisted candidate generation, not full Hausdorff speedup.

### ANN / KNN Candidate Search

Current status: excluded from RT-core app claims today because the current path
is CUDA-through-OptiX KNN rows.

Target RTDL design:

- Treat RT as the bounded candidate generator.
- Use Euclidean fixed-radius shells for L2 candidates.
- For non-L2 distances, use Arkade-style reductions:
  - filter-refine for distances with bounded geometric objects;
  - monotone transformation for distances where transformed Euclidean order
    preserves the desired metric order.
- Keep exact ranking/refinement explicit and separate.

First implementable RTDL slice:

- `rt.knn_candidate_filter(...)`: returns bounded candidates from RT traversal.
- `rt.refine_knn(...)` remains CPU/Python or CUDA until a native reducer exists.
- Metrics supported first: L2 and L1/Chebyshev-style filter-refine; cosine or
  angular only after a documented monotone transform.

Performance claim boundary:

- Claim RT-assisted candidate filtering only until exact top-k ranking is
  native and phase-separated.

### Barnes-Hut

Current status: excluded from RT-core app claims today because the current app
uses CUDA-through-OptiX plus Python tree/opening-rule/reduction work.

Target RTDL design:

- Build the Barnes-Hut tree explicitly in RTDL/Python host code.
- Bucketize leaves to control tree depth and memory use.
- Encode tree nodes as RT scene objects, likely triangles or custom AABBs.
- Use rays/ray intervals to test the opening condition.
- Use autoropes or equivalent jump metadata to emulate depth-first traversal.
- Accumulate approximate and exact force contributions in a native kernel.

First implementable RTDL slice:

- `rt.barnes_hut_opening_candidates(...)`: given bodies, tree nodes, and theta,
  returns which nodes are accepted/expanded per query body.
- Python/app layer computes force contributions first.
- Native accumulation follows only after correctness and memory behavior are
  understood.

Performance claim boundary:

- Until opening-rule traversal and force accumulation are native and measured,
  claim design feasibility only, not RT-core Barnes-Hut speedup.

## Language/Runtime Implications

These apps need minimal ITRE-compatible extensions, not a new database or
general analytics system:

- `input`: structured point sets, grid/cell metadata, tree-node metadata.
- `traverse`: RT candidate generation, any-hit/count-threshold traversal,
  node-opening traversal, or bounded cell hits.
- `refine`: exact distance checks, top-k ranking, HD pruning, force
  contribution calculation.
- `emit`: compact summaries such as candidate IDs, per-query nearest distance,
  core flags, accepted Barnes-Hut nodes, hit counts, or scalar app summaries.

The important runtime rule is that Python may orchestrate and validate, but
Python must not own the heavy inner loop for any performance claim.

## Revised Interpretation Of Goal705

Goal705 remains correct: these apps are excluded from RTX RT-core app claims
today.

Goal706 clarifies the reason:

- Excluded today does not mean impossible.
- Excluded today means "do not benchmark or market the current implementation
  as RT-core acceleration."
- The next valid work is to implement the workload-specific RT reductions
  above and then update the readiness matrix after correctness and phase-clean
  performance evidence exists.

## Proposed Follow-Up Goals

Goal707: fixed-radius and DBSCAN phase cleanup.

- Finish phase-clean timings for `rt_count_threshold` and `rt_core_flags`.
- This is the nearest already-implemented RT-core candidate.

Goal708: Hausdorff RT candidate-generation prototype.

- Implement bounded RT candidate generation over grid-expanded AABBs.
- Keep final Hausdorff exact/refine in Python first.
- Compare against CPU exact and current CUDA-through-OptiX path.

Goal709: ANN/KNN RT filter-refine prototype.

- Implement bounded RT candidate filtering and explicit exact ranking.
- Start with L2; add one non-L2 filter-refine metric only if the geometry is
  clear and testable.

Goal710: Barnes-Hut RT opening-candidate prototype.

- Implement tree-node scene encoding and opening-rule candidate emission.
- Keep force accumulation outside native RT until the opening traversal is
  correct.

Goal711: app support/readiness refresh.

- Update app matrix statuses only after Goal708-Goal710 provide correctness
  and phase-clean evidence.

## Non-Goals

- Do not claim full X-HD, Arkade, or RT-BarnesHut reproduction before those
  algorithmic optimizations exist in RTDL.
- Do not claim RT-core speedup from CUDA-through-OptiX kernels.
- Do not implement a full data system.
- Do not use cloud RTX benchmarking as a substitute for local correctness and
  phase-isolated profiling.
