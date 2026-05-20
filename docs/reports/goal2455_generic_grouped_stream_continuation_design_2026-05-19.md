# Goal2455 Generic Grouped Stream Continuation Design

Date: 2026-05-19

Status: design target, not implemented.

## Why This Exists

The RT-DBSCAN campaign has now ruled out the small continuation knobs:

- prepared chunk offsets helped repeated runs;
- single reused neighbor-index workspace was correct but slower;
- bounded workspace pools were also slower or only parity;
- raising the explicit full-adjacency budget gave the immediate win when the
  full stream fits GPU memory.

The remaining hard case is the one where the full directed adjacency stream is
too large to materialize, but chunking is too launch-heavy. That is not a
DBSCAN-only problem. It is a generic graph/runtime problem:

```text
RT traversal produces grouped hit/edge rows.
Partner continuation needs grouped reductions or union/find over those rows.
Materializing all rows is fast but memory-hungry.
Chunking rows is memory-safe but launch-heavy.
```

Goal2455 defines the next generic primitive/runtime direction.

## Proposed Generic Contract

Name shape:

```text
grouped_stream_continuation
```

Conceptual inputs:

- caller-owned group keys or implicit query ids;
- a traversal-produced item stream, such as directed fixed-radius neighbors;
- optional predicate columns, such as core flags;
- continuation operation descriptor:
  - `grouped_count`
  - `grouped_any`
  - `grouped_min`
  - `grouped_max`
  - `grouped_union_candidate`
  - `grouped_border_candidate`

Conceptual outputs:

- caller-owned partner columns;
- continuation metadata:
  - stream row count estimate;
  - bounded workspace cap;
  - chunk count or tile count;
  - launch count;
  - whether full stream was materialized;
  - whether continuation stayed device-resident;
  - claim-boundary flags.

## First Concrete Target

The first implementation target should be fixed-radius graph/component
continuation, because RT-DBSCAN already supplies the evidence and tests:

```text
generic_fixed_radius_grouped_component_continuation_3d
```

Required behavior:

1. Use generic fixed-radius traversal, not a DBSCAN native ABI.
2. Consume neighbor hits as a stream or bounded tile.
3. Apply a generic predicate such as `is_source_core` / `is_target_core`.
4. Perform union/find or border-candidate capture on device.
5. Emit component labels, core flags, and neighbor counts as partner columns.
6. Avoid host row materialization.
7. Keep exact same labels as the existing full-adjacency and chunked-adjacency
   paths.

## Implementation Options

### Option A: Native-Driven Generic Union Continuation

OptiX writes directly into caller-owned continuation workspaces:

- parent array;
- border-candidate array;
- degree counts;
- optional tile-local scratch.

Pros:

- fewer CuPy launches;
- no neighbor-index table for the continuation path;
- closest to the desired performance shape.

Cons:

- native engine gains a generic graph continuation primitive;
- must prove it is not DBSCAN-specific;
- requires careful atomic-min/union correctness review.

### Option B: Partner-Driven Persistent Tile Continuation

OptiX writes bounded tiles; a long-lived partner kernel consumes each tile with
fewer allocations and fewer launches.

Pros:

- keeps more policy in partner layer;
- easier to test incrementally from the current chunked path.

Cons:

- still needs tile writes and synchronization boundaries;
- may not beat full adjacency when full adjacency fits.

### Option C: Hybrid Planner Only

Improve explicit planning and keep using existing full/chunked paths:

- full adjacency when estimated stream fits a memory budget;
- chunked adjacency otherwise;
- no new primitive yet.

Pros:

- already improved by Goal2452/2453.

Cons:

- does not solve the larger dense-stream case.

## Recommended Path

Implement Option A as a new generic native/partner contract, but only after a
small proof:

1. Write a design review handoff for the exact native ABI names and metadata.
2. Implement a minimal OptiX path for fixed-radius grouped union candidate
   continuation.
3. Keep the app-facing RT-DBSCAN code calling a generic RTDL primitive.
4. Validate exact label signatures against:
   - CPU reference;
   - full adjacency;
   - chunked adjacency.
5. Pod-smoke at:
   - 32,768 points, to ensure no regression versus full adjacency;
   - a larger row where full adjacency is over budget, to test the intended
     win against chunking.

## Non-Goals

- No DBSCAN-native symbol.
- No hidden dispatcher.
- No paper-reproduction claim from one pod row.
- No v2.2 release claim until independent review accepts correctness,
  boundaries, and performance evidence.
- No user-defined shader injection; that remains a future v3.0 lane.

## Claim Boundary

This is a design target only. It does not authorize performance claims or
release claims.

## Verdict

`needs-more-evidence`: the direction is justified, but it requires a native
design review and pod validation before implementation can be treated as
accepted.
