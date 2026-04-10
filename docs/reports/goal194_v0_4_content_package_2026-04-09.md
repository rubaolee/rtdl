# Goal 194: v0.4 Content Package

Date: 2026-04-09
Status: revised around nearest-neighbor workloads

## Result

The `v0.4` content is now defined as a 2D/non-graphical package rather than a
3D extension of the demo line.

The package below is the handoff-ready content for the next version kickoff.

## Core release identity

Recommended identity:

- **RTDL v0.4: nearest-neighbor workload release**

More explicit reading:

- `v0.2.0` established the stable 2D workload/package core
- `v0.3.0` proved bounded RTDL-plus-Python application capability
- `v0.4` should return to the core RTDL lane and add one new non-graphical
  workload family

## Main public claim for v0.4

The main claim should be:

- RTDL supports a new nearest-neighbor spatial-query family on top of the same
  multi-backend runtime model already used for the released 2D workload core

It should **not** be:

- RTDL makes better demos
- RTDL is now a rendering system
- RTDL broadly supports 3D geometry processing

## The first v0.4 workload anchor

Two decisions are now explicit:

- headline workload family:
  - nearest-neighbor search
- first accepted public workload:
  - `fixed_radius_neighbors`

This resolves the strategic direction cleanly:

- it is a real new workload family
- it is still non-graphical
- it is directly supported by RTNN
- it keeps Hausdorff distance in the correct role as a later derivative, not a
  first release anchor

### Recommended anchor

- **fixed-radius neighbor rows**

Why this is the right first anchor:

- it is simpler than full KNN
- it has clean row semantics
- it is easy to explain publicly
- it matches the RTNN search interface model of radius plus bounded neighbor
  count

### Recommended naming

Prefer public naming like:

- `fixed_radius_neighbors`

Avoid weaker or more confusing names like:

- `rtnn`
- `range_neighbor`
- `point_sphere_hits`

Reason:

- the public feature should describe the workload, not the implementation trick

### Recommended contract

Initial bounded contract for `fixed_radius_neighbors`:

- probe side:
  - 2D points
- build side:
  - 2D points
- inputs:
  - search radius `r`
  - maximum neighbor count `k_max`
- output rows:
  - `query_id`
  - `neighbor_id`
  - `distance`

### Recommended first boundary

The first accepted boundary should be narrow and explicit:

- 2D points only
- Euclidean distance only
- exact row semantics for bounded deterministic inputs
- explicit tie policy
- explicit maximum-row behavior when the true neighbor count exceeds `k_max`

## Secondary supporting surfaces for v0.4

These can support the release, but should not be the headline:

- `knn_rows`
- `nearest_distance`
- later Hausdorff-distance planning
- preserved `v0.3.0` hidden-star demo only as proof-of-capability history

## What v0.4 should ship publicly

### 1. One first-class nearest-neighbor feature home

Add a real feature home for:

- `fixed_radius_neighbors`

It must include:

- purpose
- when to use it
- exact current boundary
- first example
- current backend coverage
- limitations

### 2. One direct non-demo example chain

Add at least one top-level release-facing example, for example:

- `examples/rtdl_fixed_radius_neighbors.py`

That example should be:

- small
- non-graphical
- copy-paste runnable
- clearly row-oriented

### 3. One reference kernel chain

Add readable reference material under:

- `examples/reference/`

So the language/runtime shape is obvious without reading the visual demos.

### 4. One bounded benchmark/evaluation story

`v0.4` should include at least one honest bounded performance or scaling story
for the new neighbor-search line.

The most likely external baselines are:

- brute-force CPU reference
- `scipy.spatial.cKDTree` as the default external CPU baseline
- published neighbor-search libraries from the RTNN comparison set when they
  are reproducible on the target host, especially:
  - `PCLOctree`
  - `FRNN`
  - `FastRNN`

Not:

- PostGIS as the primary comparison story

### 5. One tutorial extension

The current tutorial path should add:

- what neighbor search means in RTDL terms
- how radius and `k_max` shape output rows
- how this differs from the existing join-style families

## Backend acceptance plan

Recommended acceptance layers:

### Required for basic feature closure

- Python reference
- native CPU/oracle
- Embree

### Stronger release target

- OptiX
- Vulkan

### Honest release wording

If GPU backends remain bounded or are not yet performance leaders, the release
docs must say so directly.

## Proposed initial goal order for v0.4

### Goal 1: define the public `fixed_radius_neighbors` contract

Define:

- input types
- output rows
- radius semantics
- `k_max` semantics
- tie policy
- overflow behavior

### Goal 2: add Python/DSL surface for `fixed_radius_neighbors`

Add the user-facing surface cleanly as a new workload family.

### Goal 3: reference and oracle implementation

Get the truth path right before broad backend claims.

### Goal 4: Embree closure

Use Embree as the first high-confidence native backend.

### Goal 5: OptiX and Vulkan closure

Bring the GPU paths in only after the contract and truth path are stable.

### Goal 6: add `knn_rows` as the second workload in the same family

Use the same family framing, but do not let KNN become the first public
contract.

### Goal 7: docs/tutorial/release-facing example chain

Make sure new users can see and run the new workload without touching internal
history.

### Goal 8: bounded benchmark and release audit

Add the evidence layer that turns implementation into releasable surface.

## Non-goals for v0.4

Do not make `v0.4` about:

- new public movies
- demo polish as the main milestone
- generalized 3D work
- Hausdorff distance as the headline release workload
- backend proliferation without a clear new public workload

## Risks and mitigations

### Risk: RTNN-style implementation details overpower the workload story

Problem:

- the repo could talk more about rays, AABBs, and scheduling than about the
  actual workload contract

Mitigation:

- keep the public feature named by the workload
- keep implementation tricks below the contract layer

### Risk: KNN scope creep

Problem:

- jumping to full KNN first would complicate row semantics and closure

Mitigation:

- make fixed-radius neighbor rows the first contract
- add KNN second

### Risk: weak external comparison story

Problem:

- the old PostGIS comparison line does not transfer automatically

Mitigation:

- start with correctness-first closure
- use honest neighbor-search baselines later

### Risk: Hausdorff distraction

Problem:

- the X-HD paper could tempt the milestone into too much distance-workload
  scope at once

Mitigation:

- keep Hausdorff as a later extension after nearest-neighbor closure

### Risk: backend transfer assumptions

Problem:

- the current accepted Embree/native infrastructure is strongest on existing
  join-style workloads
- nearest-neighbor search may require different point/AABB packing and BVH
  ownership choices than the current segment/polygon paths

Mitigation:

- surface this explicitly in Goals 3 and 4
- do not assume the existing Embree path transfers unchanged just because the
  backend name is the same

## Finish line for "v0.4 content is ready"

This package is ready when the next version can start without another strategy
debate.

That condition is now satisfied.

The next kickoff should not ask:

- "what is `v0.4` about?"

It should ask:

- "how do we implement the first `fixed_radius_neighbors` workload cleanly?"
