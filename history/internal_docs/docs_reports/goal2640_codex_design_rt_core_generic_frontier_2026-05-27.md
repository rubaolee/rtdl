# Goal2640 Codex Design: Generic RT-Core Frontier Support Without App Pollution

Date: 2026-05-27

Status: Codex proposal for external review

## Problem Statement

Goal2639 gave `AGGREGATE_FRONTIER_COLLECT_2D` a clean app-name-free native ABI
and same-contract Embree/OptiX row-collection parity. The implementation is not
yet an RT-core implementation: the OptiX symbol performs host-side generic tree
traversal and therefore shows only ~1.00x-1.04x over Embree in row-collection
timing.

The project purpose is to make RTDL help user programs use RT cores. The next
step must therefore introduce a generic RT-core primitive or lowering that does
real OptiX traversal while keeping app semantics out of the engine.

## Design Principle

The engine may own spatial discovery and bounded row materialization. The app
owns interpretation.

Allowed in engine:

- points;
- boxes or expanded boxes;
- tree topology metadata if it is generic;
- row schemas;
- row offsets;
- fail-closed overflow;
- backend execution metadata;
- OptiX/Embree acceleration structures.

Forbidden in engine:

- Barnes-Hut;
- mass;
- force;
- inverse-square math;
- timesteps;
- N-body solver semantics;
- paper-specific shortcuts.

## Proposed Primitive

Name:

```text
EXPANDED_AABB_POINT_MEMBERSHIP_2D
```

Contract:

```text
generic_expanded_aabb_point_membership_2d_v1
```

Purpose:

Given source points and indexed boxes with per-box expansion, emit bounded rows
for point/expanded-box membership.

This is not an aggregate-tree primitive. It is a generic spatial row primitive.

## Inputs

Source points:

```text
source_id:int64
x:float64
y:float64
```

Indexed boxes:

```text
box_id:int64
min_x:float64
min_y:float64
max_x:float64
max_y:float64
expansion:float64
metadata:int64 optional or app-owned side table index
```

Capacity:

```text
max_rows_per_source:uint64_or_UINT64_MAX
row_capacity:uint64
deduplicate_boxes:uint32_bool
```

Backend behavior:

- Embree builds an indexed AABB scene or uses direct CPU reference traversal.
- OptiX builds custom primitive AABBs for expanded boxes and traces one probe
  per source point.

## Outputs

Primary row schema:

```text
source_id, box_id, metadata_flags
```

Additional CSR-style grouping:

```text
source_ids
row_offsets
```

Overflow:

```text
overflowed_out
emitted_count_out
attempted_count_out
```

Failure mode:

- If overflow is false, rows and offsets are valid.
- If overflow is true, emitted count is zero and no rows/offsets may be
  surfaced as complete.

## What RT Cores Actually Do

For OptiX:

1. Expand each box by its per-box expansion.
2. Build a custom-primitive GAS over expanded AABBs.
3. For each source point, launch a short probe ray through the point.
4. The custom intersection/any-hit program reports every expanded box whose
   AABB contains the point.
5. The output is a generic membership row stream.

This gives RT cores a real BVH traversal workload. The result is still generic:
the native code does not know why an app cares about point/box membership.

## Composition With Aggregate Frontier

`AGGREGATE_FRONTIER_COLLECT_2D` can use this primitive as an RT-assisted
subroutine, not as app logic inside the engine.

For an aggregate tree node with center `(cx, cy)`, half-size `h`, and opening
threshold `theta`, the opening test is:

```text
(2 * h) / distance < theta
```

Equivalently, a node is definitely too near to accept if:

```text
distance <= (2 * h) / theta
```

The app/lowering can prepare an expanded box around each node:

```text
expanded_node_box = node_box expanded by (2 * h) / theta
```

Then:

- if a source point is inside a node's expanded box, that node is a generic
  “near/exclusion” candidate;
- if a source point is outside a node's expanded box and the node does not
  contain that source, the aggregate node can be accepted;
- child/member traversal remains driven by generic tree topology and the
  near/exclusion row set.

The native primitive only emits `(source_id, box_id)`. It does not decide force
or score.

## Minimal Implementation Slice

Phase 1: CPU/Embree reference

- Add a Python reference function for `EXPANDED_AABB_POINT_MEMBERSHIP_2D`.
- Add row schema and fail-closed overflow tests.
- Add Embree/native or CPU-native parity if cheap.

Phase 2: OptiX real RT-core path

- Add native OptiX symbol:

```text
rtdl_optix_expanded_aabb_point_membership_2d
```

- Use custom primitive AABB GAS.
- Use one ray per source point.
- Emit row-major int64 rows or count-plus-materialize rows with fail-closed
  semantics.
- Record phase telemetry:
  - host pack;
  - upload;
  - GAS build;
  - OptiX launch/traversal;
  - output download;
  - total.

Phase 3: Aggregate-frontier lowering

- Add an experimental `collect_aggregate_frontier_2d_optix_rt_assisted`
  Python path that calls the generic membership primitive.
- It must reconstruct the exact `AGGREGATE_FRONTIER_COLLECT_2D` rows and match
  CPU/Embree bit-for-bit on deterministic fixtures.
- This wrapper may mention aggregate frontier because it is a Python/app-level
  lowering, not native engine code.

## Why Not Put Tree Traversal Directly In OptiX?

A direct OptiX `AGGREGATE_FRONTIER_COLLECT_2D` implementation would be tempting
but risky:

- it couples tree traversal and opening predicate too tightly to one workload;
- it makes it easier for force/scoring logic to creep into the native engine;
- it is less reusable by other apps needing point/expanded-box membership;
- it makes primitive catalog organization less clean.

The generic membership primitive is more reusable and easier to audit.

## Expected Tests

Contract tests:

- row schema is stable;
- metadata flags are documented;
- overflow is fail-closed;
- empty inputs produce empty rows and valid offsets;
- exact capacity succeeds;
- capacity one below exact requirement fails closed.

Parity tests:

- Python reference vs Embree/native;
- Python reference vs OptiX/native;
- aggregate-frontier CPU reference vs RT-assisted lowering.

Boundary tests:

- native files must not contain forbidden tokens:
  `barnes`, `force`, `mass`, `inverse_square`, `nbody`;
- native symbol names must use generic words only;
- primitive catalog must classify this as spatial row emission, not app math.

Performance tests:

- compare Embree membership vs OptiX membership at increasing point/box counts;
- compare CPU/Embree aggregate-frontier collect vs RT-assisted collect;
- record phase telemetry to prove traversal dominates enough to make RT cores
  meaningful.

## Success Criteria

Minimum success:

- OptiX path uses real `optixTrace` over a GAS.
- Rows match Python reference exactly.
- Overflow is fail-closed.
- No app-specific native vocabulary.

Performance success:

- OptiX membership primitive beats Embree on large enough workloads.
- RT-assisted aggregate-frontier lowering beats the current host-side OptiX
  row collector and preferably Embree native row collection.

Promotion success:

- 3-AI consensus accepts the primitive boundary.
- Docs clearly state what is generic and what remains app-owned.

## Main Risk

The expanded-box approximation must be exact for the app's acceptance rule. If
the prepared expanded boxes are too conservative, the app will descend too much
and lose performance. If they are too loose in the other direction, it can
accept nodes incorrectly and break correctness.

For correctness, the initial design should prefer conservative “too near”
classification. A conservative false positive only causes extra descent; a
false negative can cause incorrect aggregate acceptance.

## Codex Verdict

Accept this direction as the next design target, with one caveat: do not
promote it directly as `AGGREGATE_FRONTIER_COLLECT_2D_RT`. First promote the
generic membership primitive, then use it as an app/lowering subroutine.
