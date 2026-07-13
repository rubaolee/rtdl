# Goal5065 RT-BarnesHut-Derived Hierarchy Traversal API Design And Plan

Date: 2026-07-06

## Objective

Turn the reusable part of the RT-BarnesHut paper reproduction into a general
RTDL system capability:

```text
prepared hierarchy
  -> aggregate-frontier traversal
  -> inverse-square or scalar reduction
  -> device-resident output columns
```

This must be done without turning RTDL into a custom RT-BarnesHut app.

The paper app remains a user of RTDL. RTDL must provide generic hierarchy
traversal machinery; the paper app must continue to own AuthorOfficial,
author-prepared-state dumps, and author-output comparison.

## Why This Is The Correct Next Step

The RT-BarnesHut paper app closed a bounded same-input reproduction, but its
main RTDL route still depends on:

```text
scripts/goal2547_barnes_hut_3d_scalar_subtree_kernel.py
```

That script contains useful general machinery:

- flattened 3D aggregate hierarchy arrays;
- member and child offset/index tables;
- source/query body columns;
- frontier traversal over a hierarchy;
- inverse-square accumulation on CUDA;
- prepared-array validation and metadata.

If this remains inside a paper-app diagnostic script, the system drifts toward
hidden app-specific infrastructure. If it is extracted carefully into RTDL,
then RT-BarnesHut becomes a normal application using a general language API.

## Core Principle

RTDL is a general spatial/dataflow language. RT-BarnesHut is an app.

Therefore:

- RTDL may expose hierarchy traversal and aggregate reduction primitives.
- RTDL must not expose AuthorOfficial, Treelogy, RTBH, or paper-comparator
  concepts as public system API.
- The app may adapt author dumps into the generic RTDL schema.
- The app may keep exact paper comparator modes such as
  `author-optix-payload`.
- A public API is not accepted as generic until at least one non-RT-BarnesHut
  consumer uses it.

## Proposed Public Concepts

### 1. Flat 3D Hierarchy Schema

Proposed data object:

```python
AggregateHierarchy3D
```

Required columns:

```text
node_cx: float32[N]
node_cy: float32[N]
node_cz: float32[N]
node_half_size: float32[N]
node_mass: float32[N]
member_offsets: int64[N + 1]
member_indices: int64[M]
child_offsets: int64[N + 1]
child_indices: int64[C]
```

Optional continuation columns:

```text
node_next_index: int64[N]
node_resume_index: int64[N]
node_rope_index: int64[N]
```

The names must be generic. If the author-prepared arrays have
`nextPrimId` or `autoRopePrimId`, the paper app maps those names into generic
continuation columns before calling RTDL.

### 2. Prepared Device Hierarchy

Proposed data object:

```python
PreparedAggregateHierarchy3D
```

Responsibilities:

- validate schema;
- move hierarchy columns to device buffers;
- preserve device-residency metadata;
- expose no app-specific names;
- fail closed on inconsistent offsets, invalid node indices, non-contiguous
  buffers, or dtype mismatch.

### 3. Aggregate-Frontier Traversal

Proposed operation:

```python
rtdl.aggregate_frontier_reduce_3d(...)
```

Example:

```python
prepared = rtdl.prepare_flat_hierarchy_3d(
    nodes=nodes,
    members=members,
    children=children,
    continuation=continuation,
)

forces = rtdl.aggregate_frontier_reduce_3d(
    prepared,
    query_points=points,
    query_mass=masses,
    opening=rtdl.SizeDistanceOpening(max_ratio=theta),
    reducer=rtdl.InverseSquareForce(scale=0.1),
)
```

The first version may support a fixed set of reducers:

- `inverse_square_scalar_sum`;
- `inverse_square_force_vector`;
- optionally `aggregate_count` for smoke tests.

### 4. External Prepared-State Adapter

The paper app may provide:

```python
state = rt_barneshut_paper.load_author_prepared_state(path)
prepared = state.to_rtdl_aggregate_hierarchy()
```

This adapter belongs in the paper app, not RTDL core. It may mention:

- `AuthorOfficial`;
- `RTBH_PREPARED_ARRAYS_OUT`;
- `nextPrimId`;
- `autoRopePrimId`;
- `author-optix-payload`.

The RTDL API receives only generic hierarchy and continuation columns.

## Proposed API Sketch

High-level future API:

```python
import rtdl

hierarchy = rtdl.prepare_aggregate_tree_3d(
    points=points,
    masses=masses,
    bucket_size=32,
)

forces = rtdl.aggregate_frontier_reduce_3d(
    hierarchy,
    query_points=points,
    opening=rtdl.SizeDistanceOpening(max_ratio=0.5),
    reducer=rtdl.InverseSquareForce(scale=0.1),
)
```

Near-term API, using externally prepared hierarchy:

```python
hierarchy = rtdl.prepare_flat_hierarchy_3d(
    point_columns=point_columns,
    node_columns=node_columns,
    member_offsets=member_offsets,
    member_indices=member_indices,
    child_offsets=child_offsets,
    child_indices=child_indices,
    continuation_columns=continuation_columns,
)

out = rtdl.aggregate_frontier_reduce_3d(
    hierarchy,
    query_points=point_columns,
    opening=rtdl.SizeDistanceOpening(max_ratio=theta),
    reducer=rtdl.InverseSquareScalarSum(scale=0.1),
)
```

The near-term API is sufficient to migrate the paper app away from direct
`goal2547` script calls.

## Implementation Plan

### Goal5066 - Contract And Schema Gate

Define the public contract for:

- `AggregateHierarchy3D`;
- `PreparedAggregateHierarchy3D`;
- continuation columns;
- opening policies;
- reducers;
- device-residency metadata.

Acceptance:

- no `Author`, `Treelogy`, `RTBH`, or `BarnesHut` names in the generic API;
- examples use generic names such as `SizeDistanceOpening`, not app-identity
  opening names;
- schema validation tests cover dtype, offset, index, and shape failures;
- the contract can express the current 64-body author-prepared synthetic
  case and the 32,768-body author-prepared POD shape.

### Goal5067 - Extract Generic Prepared-Hierarchy Reader/Validator

Move generic prepared-array validation out of the paper app / diagnostic
script into RTDL-owned code.

Acceptance:

- paper app maps author JSON into generic schema;
- RTDL validates only generic names and generic invariants;
- local tests prove the same 64-body prepared hierarchy still matches.

### Goal5068 - Generic CUDA Backend Extraction

Extract the useful CUDA/Torch extension path from
`goal2547_barnes_hut_3d_scalar_subtree_kernel.py` into an RTDL generic backend
module.

Acceptance:

- backend accepts `PreparedAggregateHierarchy3D`;
- backend supports at least `inverse_square_scalar_sum`;
- author-specific traversal policy remains an app adapter or explicitly
  experimental comparator mode, not a public default;
- local unit tests and py_compile pass.

### Goal5069 - Migrate RT-BarnesHut Paper App To The Public API

Replace direct calls to the diagnostic script with calls through the new RTDL
hierarchy API.

Acceptance:

- 32,768-body POD correctness remains:

  ```text
  mismatch_count = 0
  max_rel_error <= previous tolerance
  ```

- narrow force-kernel timing does not materially regress:

  ```text
  resident kernel mean remains <= 1.37 ms, i.e. no more than about +10% over
  the current 1.2389567852020265 ms mean baseline
  ```

- paper app still owns AuthorOfficial, prepared-state dump, and comparator
  reporting.

### Goal5070 - Non-RT-BarnesHut Genericity Smoke

Add a second consumer that is not RT-BarnesHut.

Candidate:

```text
synthetic clustered 3D aggregate density/count query
```

It should use the same:

- flat hierarchy schema;
- prepared device hierarchy;
- aggregate-frontier traversal;
- hierarchy traversal API, but a substantially different reducer and opening
  configuration from RT-BarnesHut. Another inverse-square force field is not
  sufficient as the genericity proof.

Acceptance:

- no author/prepared-dump logic;
- no paper comparator;
- same public API produces deterministic output against a Python reference.

### Goal5071 - POD Gate

Run Linux/POD validation:

- RT-BarnesHut same-input 32,768 correctness;
- RT-BarnesHut narrow force-kernel timing;
- non-RT-BarnesHut genericity smoke;
- device-residency metadata checks;
- public-surface leak scan.

Acceptance:

- correctness closed;
- performance not regressed beyond threshold;
- genericity smoke passes;
- no internal review/process strings leak to public docs.

### Goal5072 - Documentation And Release Boundary

Update docs to explain the new system capability:

```text
RTDL hierarchy traversal / aggregate-frontier API
```

Docs must explicitly separate:

- generic RTDL API;
- RT-BarnesHut paper app;
- AuthorOfficial comparator machinery;
- performance phase boundaries.

Acceptance:

- public docs do not claim full paper Section 5 reproduction;
- public docs do not claim whole-program speedup;
- docs show a clean user-facing code example;
- internal paper-app exact-comparator details remain in paper-app docs.

## Non-Goals

This plan does not authorize:

- full RT-BarnesHut paper Section 5 evaluation reproduction;
- ChaNGa/Treelogy million-scale benchmark matrix;
- promoting `author-optix-payload` as a normal RTDL public traversal policy;
- moving AuthorOfficial patches into core;
- claiming full raw-body-to-force RTDL parity;
- converting RTDL into a raw OptiX callback/shader API.

## Performance Framing Rule

Every future document that quotes the current force-kernel ratio must pair it
with the full phase context:

```text
Narrow force-kernel phase:
  RTDL resident kernel min 1.1904959678649902 ms
  RTDL resident kernel mean 1.2389567852020265 ms
  Author RT force phase 5.579 ms
  RTDL min / Author single = 0.21338877359114364
  RTDL mean / Author single ~= 0.2221

Reported broader envelope:
  RTDL tree preparation + tensor transfer + extension compile + kernel
    ~= 336.98 ms
  Author preprocessing + execution
    ~= 99.91 ms
  RTDL is about 3.37x slower on that broader reported envelope
```

The narrow ratio is useful for checking the force-kernel phase. It is not a
whole-program speedup claim and must not be presented without this context.
Future gates must report min/mean for RTDL and the author-side statistic used
as denominator.

## Risk Register

### R1 - Author Comparator Leakage

Risk: author-specific terms leak into RTDL public API.

Mitigation: API and docs scans for `Author`, `Treelogy`, `RTBH`, and
`author-optix-payload` outside paper app boundaries.

### R2 - Generic API Too Narrow

Risk: the API is shaped around RT-BarnesHut and cannot support a second app.

Mitigation: Goal5070 non-RT-BarnesHut smoke before release.

### R3 - Performance Regression

Risk: extracting the diagnostic kernel into a formal API adds overhead.

Mitigation: compare resident-kernel timing on the 32,768-body POD gate.

### R4 - Overclaiming

Risk: bounded same-input force-kernel reproduction is described as full paper
evaluation reproduction.

Mitigation: docs and manifest keep current claim boundary.

## Success Definition

The next line succeeds when this is true:

```python
prepared = rtdl.prepare_flat_hierarchy_3d(...)
out = rtdl.aggregate_frontier_reduce_3d(prepared, ...)
```

and both of these pass:

1. RT-BarnesHut app still matches AuthorOfficial on the 32,768-body same-input
   POD gate.
2. A non-RT-BarnesHut app uses the same API successfully.

At that point, RT-BarnesHut is no longer the hidden implementation owner of
the hierarchy traversal capability. It becomes one paper app using a general
RTDL language feature.
