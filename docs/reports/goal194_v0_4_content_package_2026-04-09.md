# Goal 194: v0.4 Content Package

Date: 2026-04-09
Status: prepared

## Result

The `v0.4` content is now defined as a bounded next-version package rather than
an open-ended idea.

The package below is the handoff-ready content for the next version kickoff.

## Core release identity

Recommended identity:

- **RTDL v0.4: bounded 3D geometric-query release**

More explicit reading:

- `v0.2.0` established the stable 2D workload/package core
- `v0.3.0` proved that the same RTDL core can sit inside bounded Python-hosted
  applications
- `v0.4` should turn that proof into one explicit, non-graphical, first-class
  3D workload line

## Main public claim for v0.4

The main claim should be:

- RTDL supports a bounded 3D spatial-data workload family on top of the same
  multi-backend runtime principles already proven in 2D

It should **not** be:

- RTDL makes prettier movies
- RTDL is now a rendering engine
- RTDL broadly supports generic 3D geometry processing

## The first v0.4 workload anchor

Two decisions are now explicit:

- first substrate feature to formalize:
  - `ray_tri_hitcount_3d`
- headline release workload:
  - `point_in_volume`

This resolves the main external tension:

- Claude is right that the package needs a concrete first engineering target
- Gemini is right that `v0.4` still needs a real non-graphical workload and
  cannot stop at generic ray visibility mechanics

### Recommended anchor

- **point-in-volume / point-in-mesh classification**

Why this is the right first anchor:

- it has a clear non-graphical user story
- it is conceptually close to the existing 2D `pip` family
- it can be built honestly on the current bounded 3D ray/triangle primitive
- it keeps RTDL in the spatial-data/runtime lane rather than the graphics lane

### Recommended naming

Prefer public naming like:

- `point_in_volume`

Avoid weaker names like:

- `mesh_visibility_test`
- `raycast_contains`

Reason:

- the feature should read as a spatial-data workload, not as a rendering
  helper

### Substrate feature that should be formalized first

Before `point_in_volume` becomes the release headline, `v0.4` should first
make the already-proven 3D primitive explicit:

- `ray_tri_hitcount_3d`

This work should be described honestly as:

- a contractual and documentation lift of capability already proven in
  `v0.3.0`

not as:

- a wholly new workload family

### Recommended contract

Initial bounded contract for `point_in_volume`:

- probe side:
  - 3D points
- build side:
  - closed triangle meshes
- predicate idea:
  - bounded parity-style inside/outside test built on ray/triangle hit counts
- output:
  - `point_id`
  - `volume_id`
  - `contains`

### Recommended first boundary

The first accepted boundary should be narrow and explicit:

- closed manifold meshes only
- inclusive/exclusive boundary mode must be defined explicitly
- deterministic synthetic and authored fixture sets first
- no claim of robust computational geometry on arbitrary degenerate meshes

## Secondary supporting surfaces for v0.4

These can support the release, but should not be the headline:

- stronger public `ray_tri_hitcount` documentation and examples
- bounded 3D visibility/occlusion examples
- continued hidden-star demo as proof-of-capability regression test

## What v0.4 should ship publicly

### 1. One first-class 3D feature home

Add a real feature home for:

- `point_in_volume`

It must include:

- purpose
- when to use it
- exact current boundary
- first example
- current backend coverage
- limitations

### 2. One direct non-demo example chain

Add at least one top-level release-facing example, for example:

- `examples/rtdl_point_in_volume.py`

That example should be:

- small
- non-graphical
- copy-paste runnable
- clearly useful on its own

### 3. One reference kernel chain

Add readable reference material under:

- `examples/reference/`

So the language/runtime shape is obvious without reading the visual demos.

### 4. One bounded benchmark/evaluation story

`v0.4` should include at least one honest performance or scaling story for the
new 3D line, even if it is small and synthetic at first.

Without that, the new feature will look ornamental rather than like real RTDL
surface area.

Important honesty note:

- `v0.4` may need to begin as a correctness-first 3D release if no honest
  external 3D performance baseline exists yet
- if so, the release docs must say that directly

### 5. One tutorial extension

The current tutorial path is 2D-heavy. `v0.4` should add:

- a short tutorial section that explains how 3D inputs differ
- what the new 3D workload means
- how it relates to the old `pip` mental model

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

If GPU backends are bounded or slower, the release docs must say so directly.
Do not repeat the `v0.3.0` mistake of letting the most visible proof artifact
carry the public identity of the release.

## Proposed initial goal order for v0.4

### Goal 1: formalize `ray_tri_hitcount_3d` as a public feature line

Define:

- public name
- input types
- emit fields
- accepted geometry assumptions
- exact current limitations

### Goal 2: define the public `point_in_volume` workload contract

Define:

- closed/watertight mesh requirement
- accepted boundary policy
- excluded degeneracies
- emitted row shape

### Goal 3: Python/DSL surface for 3D points and volume classification

Add the user-facing surface cleanly, not as internal demo reuse.

### Goal 4: reference and oracle implementation

Get the truth path right before broad backend claims.

### Goal 5: Embree closure

Use Embree as the first high-confidence native backend.

### Goal 6: OptiX and Vulkan closure

Bring the GPU paths in only after the workload contract is stable.

### Goal 7: docs/tutorial/release-facing example chain

Make sure new users can actually see and use the feature without reading
internal reports.

### Goal 8: bounded benchmark and release audit

Add the evidence layer that turns implementation into releasable surface.

## Non-goals for v0.4

Do not make `v0.4` about:

- new public movies
- demo polish as the main milestone
- generalized 3D rendering
- broad 3D LSI/PIP/overlay claims all at once
- backend proliferation without a clear user-visible new workload
- Hausdorff-adjacent workloads as `v0.4` headline scope

## Risks and mitigations

### Risk: identity slop

Problem:

- `v0.4` could still read as "graphics by euphemism"

Mitigation:

- lead with `point_in_volume` or equivalent spatial-data language
- keep demos in supporting role only

### Risk: broad but shallow 3D support

Problem:

- adding many bounded 3D terms without one strong workload

Mitigation:

- make one workload the headline and release gate

### Risk: backend maturity debt

Problem:

- claiming too much before GPU boundaries are proven

Mitigation:

- require reference + oracle + Embree first
- treat OptiX/Vulkan as follow-on closure layers, not automatic entitlement

### Risk: no real user story

Problem:

- generic hit-count promotion feels abstract

Mitigation:

- attach the feature to a concrete non-graphical use case such as:
  - volumetric containment auditing
  - 3D asset occupancy classification
  - 3D point-cloud-in-mesh screening

## Finish line for "v0.4 content is ready"

This package is ready when the next version can start without another strategy
debate.

That condition is now satisfied.

The next kickoff should not ask:

- "what is `v0.4` about?"

It should ask:

- "how do we implement the first bounded `point_in_volume` workload cleanly?"
