# Goal2640 Call For Design: Generic RT-Core Aggregate-Frontier Acceleration

Date: 2026-05-27

Audience: Claude external design reviewer

## Context

RTDL has a Barnes-Hut benchmark app, but the project principle is that native
engines must remain app-agnostic. The engine must not contain Barnes-Hut,
mass, force, inverse-square, contact, DBSCAN, graph, or database semantics.

Goal2638 introduced `AGGREGATE_FRONTIER_COLLECT_2D` as a generic CPU-reference
and partner-column primitive. It emits source-offset plus row-major `int64`
frontier rows:

```text
source_id, frontier_kind_code, item_id, owner_aggregate_id, dfs_index, resume_index, metadata_flags
```

Goal2639 added app-name-free Embree and OptiX native symbols with same-contract
parity and fail-closed overflow evidence. However, the current OptiX symbol is
host-side generic traversal packaged inside the OptiX backend library. It does
not materially use RT cores. Larger pod timing showed only about 1.00x-1.04x
OptiX/Embree, which is expected for host-side traversal.

The next design target is a true RT-core-backed generic primitive/lowering that
can accelerate the aggregate-frontier row-collection workload without polluting
the engine with app logic.

## Design Problem

Design a generic RTDL primitive or primitive composition that lets OptiX RT
cores accelerate aggregate-frontier-style row collection while preserving the
engine boundary.

The design must answer:

1. What is the generic primitive name and contract?
2. What inputs and outputs does it own?
3. What exact work do RT cores perform?
4. How does the design preserve exact fail-closed overflow semantics?
5. How does the app use the generic primitive to recover the
   `AGGREGATE_FRONTIER_COLLECT_2D` row contract?
6. How does the design avoid app-specific native-engine logic?
7. What should be implemented first as a minimal but real RT-core slice?
8. What tests prove correctness, parity, and boundary cleanliness?
9. What performance evidence is required before claiming RT acceleration?
10. What risks or reasons might make this design unsuitable?

## Non-Negotiable Boundaries

- Do not put Barnes-Hut, mass, force, inverse-square, N-body, or paper-specific
  vocabulary into native engine code.
- Do not put force-vector summation or app scoring into native engine code.
- Do not silently truncate rows. Overflow must be fail-closed:
  `overflowed == true`, emitted count is zero, and no partial rows are surfaced.
- Do not claim RT-core speedup until an OptiX implementation demonstrably uses
  OptiX traversal and beats the Embree same-contract path on suitable workloads.
- App Python may build an aggregate tree and decide how to interpret generic
  rows, but native primitives must stay generic.

## Candidate Direction To Evaluate

A plausible direction is a generic expanded-AABB point-membership primitive:

```text
EXPANDED_AABB_POINT_MEMBERSHIP_2D
```

Inputs:

- source points: `source_id, x, y`
- indexed boxes: `box_id, min_x, min_y, max_x, max_y`
- per-box expansion or radius
- bounded output capacity

Output:

- row-major `int64` rows like `(source_id, box_id)` or
  `(source_id, box_id, metadata_flags)`
- source row offsets
- overflow diagnostics

RT-core role:

- Build OptiX custom-primitive AABBs for expanded boxes.
- For each source point, trace a short probe ray or equivalent query that
  reports boxes containing/intersecting the point.
- Emit generic “near/exclusion” rows.

Potential use for aggregate frontier:

- The app/lowering can treat “source is inside expanded node box” as
  “node may be too near to accept under the opening predicate,” then combine
  this generic exclusion set with tree topology to decide accept/descend.
- The engine only knows points, boxes, expansions, rows, offsets, and overflow.

Claude should critique this candidate and may propose a better generic design.

## Expected Output

Write a detailed design review with:

- Recommended primitive contract.
- Minimal implementation plan for OptiX and Embree parity.
- How it composes with `AGGREGATE_FRONTIER_COLLECT_2D`.
- Boundary audit: what must stay outside engine.
- Tests and performance evidence requirements.
- Verdict: accept, reject, or accept with changes.
