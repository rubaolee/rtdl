# Goal2408 Codex RT-DBSCAN Next-Fight Plan

Date: 2026-05-19

Status: Codex proposal for external review before the next implementation fight

## Current Position

Goal2405 is the current positive result:

- RTDL now has a generic true OptiX RT 3-D fixed-radius count-threshold device
  column primitive.
- It writes threshold-capped counts and core flags into partner CUDA columns.
- It stays app-agnostic: no DBSCAN-native ABI.
- On the RTX A5000 pod, it beats the old OptiX-backend uniform-cell summary
  bridge and wins on dense `clustered3d` at 131k points.

Goal2407 is the current negative result:

- A generic OptiX any-hit core-graph union prototype compiled and matched
  signatures.
- It did not beat Goal2405's RT-count plus CuPy-grid continuation.
- Conclusion: raw any-hit atomic union is not the continuation primitive we want.

So the problem is now sharper:

```text
RTDL can use RT cores to classify fixed-radius core points, but the full DBSCAN
composition still pays for a separate radius-graph component continuation.
```

## Design Boundary

The next work must remain generic. Allowed vocabulary:

- fixed-radius graph
- core flags
- threshold-capped counts
- component labels
- cell index
- compact edge stream
- grouped/union continuation

Disallowed native direction:

- `dbscan` native ABI
- DBSCAN cluster expansion hard-coded into OptiX
- app-specific neighborhood semantics
- broad RT-core speedup claims before pod evidence

## Candidate Strategies

### Candidate A: Prepared CuPy Grid Continuation

Build a reusable partner-side prepared grid object for fixed-radius component
continuation:

```text
prepare_radius_graph_components_3d_cupy_grid(point_columns, radius)
run(core_flags, neighbor_counts)
```

It would cache:

- point columns cast to stable dtypes,
- cell ids,
- sorted order,
- unique cells,
- starts/counts,
- output buffers where safe.

Why it may help:

- current `radius_graph_components_3d_cupy_grid_partner_columns` rebuilds the
  grid every call;
- the DBSCAN benchmark uses fixed points and radius per run;
- both pure CuPy and RTDL+OptiX can share the same prepared continuation, so the
  comparison stays fair.

Why it may not be enough:

- on dense 131k, the continuation cost may be dominated by per-point/per-neighbor
  union work, not sorting/unique/allocation.

Verdict: useful baseline hardening, but probably not the whole win.

### Candidate B: Generic Cell-Graph All-Core Continuation

When all points are core, the component problem can be reduced from point-level
neighbor union to a smaller cell-level graph:

1. Build a fixed-radius grid.
2. For each neighboring cell pair, test whether any point pair across the cells
   is within radius.
3. Union cells, not every point pair.
4. Label each point by its cell component.
5. Fall back to the existing CuPy grid continuation when non-core points exist.

Why it may help:

- Goal2407 showed that point-level atomic union inside RT any-hit is too noisy.
- Dense clustered rows have all or almost all points core.
- Cell count is often much smaller than point count.
- This is still generic fixed-radius graph continuation, not DBSCAN-native logic.

Main correctness risk:

- cell adjacency alone is not enough; we must prove or test an actual in-radius
  cross-cell point pair before unioning cells.

Verdict: best next fight. It attacks the measured bottleneck and preserves the
app-agnostic boundary.

### Candidate C: Compact RT Edge Stream Consumed By Partner Union

Have RT traversal emit a compact stream of core-core edges, then run a partner
union kernel over that compact stream.

Why it may help:

- moves hit discovery to RT traversal;
- keeps union in a partner kernel instead of doing atomics inside OptiX any-hit;
- creates a reusable stream continuation shape.

Why it is risky now:

- dense rows can produce enormous edge streams;
- bounded capacity and overflow policy become central;
- row/edge materialization could recreate the problem Goal2405 avoided.

Verdict: important v2.x primitive idea, but after Candidate B unless cell-graph
cannot preserve correctness or scale.

### Candidate D: Exact RT Radius Graph With Device-Resident Union Scheduling

A deeper native runtime primitive could combine RT traversal with a scheduled
device-resident union/reduction pipeline.

Why it may help:

- closest to the paper-style direction;
- could avoid both duplicate CuPy traversal and raw any-hit atomic contention.

Why it is too large for the immediate fight:

- needs a stronger generic scheduling contract;
- risks accidentally becoming DBSCAN-shaped;
- needs more design review before coding.

Verdict: hold for after Candidate B/C evidence.

## Recommended Next Implementation

Implement Candidate B as Goal2409:

```text
generic fixed-radius cell-graph component continuation for all-core 3-D point
sets, with fallback to the existing CuPy grid continuation when non-core points
exist
```

Concrete API shape:

```python
radius_graph_components_3d_cupy_cell_graph_partner_columns(
    point_columns,
    radius=...,
    min_neighbors=...,
    core_flags=...,
    neighbor_counts=...,
    return_metadata=True,
)
```

The initial version can live in the partner adapter as a CuPy RawKernel
continuation. It should not touch native OptiX unless the partner-only cell
graph result proves useful.

Execution plan:

1. Add static tests that enforce generic names and fallback behavior.
2. Implement cell-pair existence and cell-union kernels in CuPy.
3. Use it in the RT-DBSCAN benchmark as a new mode:

```text
optix_rt_core_flags_cupy_cell_graph_components_3d
```

4. Compare against:

```text
partner_cupy_grid_components_3d
optix_rt_core_flags_cupy_grid_components_3d
```

5. Pod test at:

```text
4096, 32768, 65536, 131072
clustered3d and road3d
repeat_count >= 3
```

6. Accept only if signatures match and at least one of these is true:

- dense clustered 131k improves over Goal2405 materially, or
- sparse road rows do not regress while dense stays competitive, or
- profiling clearly identifies a next smaller fix.

## What Would Make Me Change My Mind

I would abandon Candidate B quickly if:

- cell-pair exactness requires scanning almost the same number of point pairs as
  point-level union;
- cell-level labeling breaks non-convex/sparse connectivity correctness;
- it only wins on the synthetic clustered row by exploiting "all points core" in
  a way that does not generalize to fixed-radius graph workloads.

If that happens, the next target should be Candidate A for disciplined prepared
continuation measurement, then Candidate C for compact edge stream design.

## Claim Boundary

This plan does not authorize a release claim, RT-DBSCAN paper reproduction
claim, broad RT-core speedup claim, or v2.x closure.

It is a plan for the next benchmark-driven RTDL runtime improvement. The engine
must remain app-agnostic throughout.
