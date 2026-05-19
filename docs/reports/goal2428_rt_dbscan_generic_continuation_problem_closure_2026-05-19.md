# Goal2428 RT-DBSCAN Generic Continuation Problem Closure

Date: 2026-05-19

Status: planning/claim problem closed; runtime continuation problem scoped

## What Is Closed

Goal2424 added the fair prepared-CuPy baseline. Goal2425 measured that baseline
against the prepared OptiX RT-count bridge. Goal2427 then smoked the updated
`planned_rt_dbscan` choices on the RTX A5000 pod.

That closes the planning problem:

```text
RTDL can now choose the measured RT-DBSCAN benchmark path explicitly,
record the reason, execute the selected mode, and keep the claim boundary
visible in the output JSON.
```

It also closes a documentation problem: the learner README now contains only the
Goal2425/Goal2427 policy, not the stale earlier 262k road-crossover language.

## What Is Not Closed

The remaining performance problem is not DBSCAN-specific. It is the generic
continuation after a fixed-radius native phase:

```text
RTDL has a generic prepared fixed-radius count-threshold device-column phase,
but the current component-label continuation still redoes radius-neighborhood
traversal in CuPy.
```

Counts and core flags are useful, but they are not enough to label components.
Exact component labeling needs connectivity information:

- core-core edges determine connected core components;
- border points need at least one adjacent core component;
- threshold-capped neighbor counts cannot reconstruct those edges;
- a hidden DBSCAN-native ABI would violate the app-agnostic engine boundary.

## Required Generic Primitive

The next v2.x runtime primitive should be generic fixed-radius graph
continuation machinery, not a DBSCAN shortcut:

```text
prepared fixed-radius edge/adjacency stream
  -> device-resident grouped union/find continuation
  -> optional border/witness assignment
```

The primitive should expose an explicit plan/explain contract:

- selected native backend and partner;
- whether the native phase writes counts, flags, edge offsets, or edge chunks;
- whether outputs stay device-resident;
- whether a bounded/streaming path was used;
- whether RT-core speedup, whole-app speedup, and paper-reproduction claims are
  authorized.

## Candidate Implementation Order

1. Add a partner-only prepared edge-stream prototype over the existing CuPy
   grid so the row-stream and grouped-union contract can be tested without
   changing the native engine.
2. Add an OptiX prepared fixed-radius edge-stream writer only if the partner
   contract proves useful. The ABI must remain generic, for example
   fixed-radius adjacency offsets plus neighbor indices, not DBSCAN labels.
3. Add a bounded/streaming mode for dense rows so RTDL can avoid materializing
   a huge full edge table.
4. Re-run the RT-DBSCAN benchmark on the same datasets and compare against
   prepared CuPy, prepared RT-count plus CuPy-grid continuation, and the
   negative microcell path.

## Boundary

This is v2.x primitive/runtime work. It is not a v3.0 user-defined shader
injection feature, and it must not introduce app-specific native engine
terminology.
