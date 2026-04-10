# Goal 193: v0.4 Direction Decision

Date: 2026-04-09
Status: revised direction package

## Inputs reviewed

The revised proposal below is grounded in:

- [README](../../README.md)
- [Docs Index](../README.md)
- [Quick Tutorial](../quick_tutorial.md)
- [Release-Facing Examples](../release_facing_examples.md)
- [v0.3 Release Statement](../release_reports/v0_3/release_statement.md)
- [v0.3 Support Matrix](../release_reports/v0_3/support_matrix.md)
- [Architecture, API, And Performance Overview](../architecture_api_performance_overview.md)
- [Vision](../vision.md)
- [Future Ray-Tracing Directions](../future_ray_tracing_directions.md)
- [RTNN paper](../../../Downloads/3503221.3508409.pdf)
- [X-HD paper](../../../Downloads/2026-xhd.pdf)

## Current position after v0.3.0

`v0.3.0` released successfully, but it also clarified something important:

- the 3D demo is a useful proof-of-capability
- it is not the right center of gravity for the next milestone
- the repo's durable identity is still "non-graphical geometric-query runtime"

So the next version should not continue the demo line as the main product
story. It should return to RTDL's core lane and add a new non-graphical
workload family.

## The real conflict for v0.4

There are three credible directions.

### Proposal A: Demo-first v0.4

Make `v0.4` about stronger public demos and application polish.

### Proposal B: Backend-first v0.4

Make `v0.4` about more backend closure and backend maturity work on the current
surface.

### Proposal C: New 2D workload-family-first v0.4

Make `v0.4` about adding one real new 2D/non-graphical workload family that
fits RTDL's language/runtime identity and has clear research support.

## Sharp proposal/rebuttal

### Proposal A: double down on demos

Argument for it:

- demos are visible
- demos attract attention
- `v0.3.0` already proved RTDL can sit inside applications

Rebuttal:

- this would keep pushing the repo away from its real identity
- it would make the front-page honesty boundary weaker, not stronger
- it would optimize presentation instead of language/runtime value

Conclusion:

- reject Proposal A as the main `v0.4` theme

### Proposal B: double down on backend maturity

Argument for it:

- RTDL is fundamentally multi-backend
- backend closure still matters for trust and performance

Rebuttal:

- backend work alone still does not answer the user-facing question:
  - what new problem can RTDL solve in `v0.4`?
- it would make `v0.4` feel like infrastructure maintenance rather than a new
  release with new workload substance

Conclusion:

- backend work should support `v0.4`
- but it should not be the release identity

### Proposal C: add a new nearest-neighbor workload family

Argument for it:

- nearest-neighbor search is a clean non-graphical spatial workload family
- it has direct research support in RTNN
- X-HD reinforces that nearest-neighbor search is a meaningful building block
  for later higher-level workloads like Hausdorff distance
- it gives `v0.4` a public identity that is clearly different from both:
  - the current released 2D workload set
  - the `v0.3.0` application/demo proof line

Rebuttal risk:

- "is this too far from the current RayJoin-style line?"

Counter-rebuttal:

- no, because it stays in exactly the same RTDL lane:
  - non-graphical spatial querying
  - backend-heavy traversal
  - row-oriented outputs
- it expands the language/runtime surface without changing the product identity

Conclusion:

- Proposal C is the strongest `v0.4` direction

## Why nearest-neighbor is the right next family

The two papers imply a clear priority order:

- RTNN is directly about neighbor search as a workload family
- X-HD treats nearest-neighbor search as the building block for Hausdorff
  distance

That means:

- nearest-neighbor search is the right `v0.4` headline family
- Hausdorff distance is a plausible later extension, not the first `v0.4`
  headline workload

## Recommended v0.4 theme

Recommended release theme:

- **`v0.4`: neighbor-search workload release**

Recommended headline:

- extend RTDL from the current released workload core into a new
  nearest-neighbor spatial-query family

## Concrete v0.4 objectives

Two decisions are now explicit:

- headline workload family:
  - nearest-neighbor search
- first accepted public workload:
  - fixed-radius neighbor rows

This split is deliberate:

- the family gives `v0.4` its identity
- the first accepted workload keeps the initial scope bounded

### Objective 1: ship fixed-radius neighbor rows

Chosen release target:

- `fixed_radius_neighbors`

Reason:

- cleaner public contract than full KNN
- simpler row semantics
- easier correctness story
- directly supported by RTNN's problem framing

### Objective 2: define the nearest-neighbor public contract

For the new workload family, define:

- point input types
- search radius semantics
- maximum returned neighbor count semantics
- emitted row shape
- duplicate and tie behavior
- exact vs bounded claims

### Objective 3: add one direct non-demo example chain

The front door should include at least one example like:

- `examples/rtdl_fixed_radius_neighbors.py`

It should be:

- small
- non-graphical
- row-oriented
- copy-paste runnable

### Objective 4: add KNN as the second workload in the same family

Second candidate workload:

- `knn_rows`

But it should follow fixed-radius search, not lead the milestone.

### Objective 5: keep Hausdorff distance out of headline scope

The X-HD paper is still valuable, but the lesson for `v0.4` is:

- Hausdorff distance depends on nearest-neighbor search
- therefore Hausdorff distance is a later extension or stretch goal
- it should not be the first release identity of `v0.4`

### Objective 6: align performance and validation story

`v0.4` should clearly distinguish:

- correctness closure
- bounded performance evidence
- external baseline story

Unlike the older 2D PostGIS story, nearest-neighbor search may need a different
external baseline, such as:

- existing GPU/CPU neighbor-search libraries
- brute-force CPU reference on bounded inputs

## What v0.4 should not be

Do not make `v0.4` into:

- a demo-first milestone
- a 3D milestone
- a rendering-adjacent milestone
- a backend-only cleanup release
- a Hausdorff-distance-first release

## Decision

Recommended decision:

- **make `v0.4` a 2D nearest-neighbor workload milestone**
- keep `v0.3.0` 3D work as preserved proof material only
- use RTNN as the primary workload signal
- treat X-HD as supporting evidence that nearest-neighbor search opens a strong
  future path

## Immediate next planning questions

To open `v0.4` cleanly, answer these first:

1. What exact row contract should define `fixed_radius_neighbors`?
2. Should the public family name be:
   - `nearest_neighbors`
   - `fixed_radius_neighbors`
   - `knn_rows`
3. Which backends are required for first closure:
   - CPU reference
   - oracle
   - Embree
   - OptiX
   - Vulkan
4. What is the most honest external baseline for bounded performance comparison?
5. Should `knn_rows` be a same-release secondary feature or a follow-on goal?

## Codex provisional conclusion

The strongest `v0.4` move is not to chase 3D proof work further. It is to add
a nearest-neighbor workload family that is clearly non-graphical, directly
research-backed, and aligned with RTDL's identity as a spatial-query runtime.
