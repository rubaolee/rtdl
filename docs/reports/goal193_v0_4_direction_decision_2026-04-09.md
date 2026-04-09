# Goal 193: v0.4 Direction Decision

Date: 2026-04-09
Status: proposed direction package

## Inputs reviewed

The proposal below is grounded in the current public and release-facing
surfaces:

- [README](../../README.md)
- [Docs Index](../README.md)
- [Quick Tutorial](../quick_tutorial.md)
- [Release-Facing Examples](../release_facing_examples.md)
- [v0.3 Release Statement](../release_reports/v0_3/release_statement.md)
- [v0.3 Support Matrix](../release_reports/v0_3/support_matrix.md)
- [Architecture, API, And Performance Overview](../architecture_api_performance_overview.md)
- [Vision](../vision.md)
- [Future Ray-Tracing Directions](../future_ray_tracing_directions.md)
- [Ray/Triangle Hit Count feature home](../features/ray_tri_hitcount/README.md)

## Current position after v0.3.0

`v0.3.0` is a real release, but it leaves an intentional tension in the repo
story:

- the strongest stable workload/package identity is still the `v0.2.0` surface
- the newest public-facing attention hook is the `v0.3.0` hidden-star 3D demo
- the front page is honest that RTDL is not a renderer
- but the most visible public proof is still an application demo rather than a
  new workload family

That tension is acceptable for `v0.3.0`, but it is not a strong long-term
release identity for `v0.4`.

## The hard conflict

There are three credible directions for `v0.4`.

### Proposal A: Demo-first v0.4

Make `v0.4` about better applications and stronger 3D demo polish:

- more polished hidden-star variants
- more public videos
- cleaner app wrappers
- stronger cross-backend demo parity

### Proposal B: Backend/platform-first v0.4

Make `v0.4` about broader platform closure:

- more native backend work
- more backend portability
- stronger packaging around the current workloads

### Proposal C: Workload-language-first v0.4

Make `v0.4` about turning the `v0.3.0` 3D proof into new public
non-graphical workload surface:

- promote bounded 3D geometric-query workloads to first-class public features
- keep the application/demo line as proof, not as the product center
- unify the repo story around "RTDL as a language/runtime for geometric
  queries in 2D and bounded 3D"

## Sharp proposal/rebuttal

### Proposal A: double down on demos

Argument for it:

- the public demo is the most attention-grabbing artifact
- `v0.3.0` proved RTDL can support applications
- better demos would make the front page feel stronger

Rebuttal:

- this is the wrong center of gravity for RTDL
- it would make the repo look like it is pivoting into graphics
- it optimizes presentation more than language/runtime substance
- it weakens the honesty boundary already stated on the front page

Hot conflict:

- the front page says RTDL is a non-graphical geometric-query runtime
- a demo-first `v0.4` would make the repo behave like that statement is only a
  disclaimer rather than the actual product identity

Conclusion:

- reject Proposal A as the main `v0.4` release theme
- keep demos as supporting proof, not the main release identity

### Proposal B: double down on backend/platform reach

Argument for it:

- RTDL is fundamentally a multi-backend runtime
- backend maturity remains a differentiator
- more portability would make the runtime story stronger

Rebuttal:

- backend work without new surface semantics does not give users a clearer
  reason to adopt `v0.4`
- it improves infrastructure more than public capability
- it risks another milestone where the public surface still looks like
  "`v0.2.0` workloads plus engineering cleanup"

Hot conflict:

- a backend-first `v0.4` would be rational for the implementation team
- but weak for external users because it does not answer:
  - what new kind of problem can RTDL solve now?

Conclusion:

- backend work should be part of `v0.4`
- but only in support of a new user-visible workload expansion

### Proposal C: convert the 3D proof into a real bounded 3D workload release

Argument for it:

- it aligns with the current front-page honesty boundary
- it turns the `v0.3.0` demo from proof-of-capability into a bridge toward new
  non-graphical workload surface
- it gives `v0.4` a crisp identity: RTDL grows from 2D workload families into
  bounded 3D geometric queries
- it uses the strongest new engineering asset already built in `v0.3.0`:
  multi-backend 3D ray/triangle query support

Rebuttal risk:

- "is this just graphics by another name?"

Counter-rebuttal:

- not if the new public surface is defined as bounded geometric-query work such
  as:
  - `ray_tri_hitcount_3d` as a public feature line
  - point-in-mesh / point-in-volume style inclusion tests
  - occlusion/visibility queries framed as geometric predicates
- the demo remains evidence, not the target

Hot conflict:

- this direction forces RTDL to choose substance over spectacle
- it says the correct response to a successful demo is not "make prettier
  videos" but "extract the real workload surface the demo proved we can
  support"

Conclusion:

- Proposal C is the strongest `v0.4` direction

## Recommended v0.4 theme

Recommended release theme:

- **`v0.4`: bounded 3D geometric-query release**

Recommended headline:

- extend RTDL from the stable `v0.2.0` 2D workload/package surface and the
  `v0.3.0` application proof layer into a first-class bounded 3D
  geometric-query surface

## Concrete v0.4 objectives

Two decisions have to be separated clearly:

- the first 3D substrate feature to formalize
- the headline release workload that gives `v0.4` its identity

The current package now commits to both:

- first substrate feature to formalize:
  - `ray_tri_hitcount_3d`
- headline release workload:
  - `point_in_volume`

This split resolves the strongest external objections:

- Claude is right that the package was not actionable until one concrete first
  target was chosen
- Gemini is right that `v0.4` still needs a real non-graphical 3D workload
  rather than stopping at generic ray visibility mechanics

### Objective 1: formalize the bounded 3D query substrate

Promote:

- `ray_tri_hitcount_3d`

to a real public feature line with:

- a feature home
- a direct non-demo example
- explicit input/output contracts
- explicit backend support wording

Important honesty note:

- this is not a wholly new workload family
- it is a contractual and documentation lift of capability already proven in
  `v0.3.0`

### Objective 2: ship one real non-graphical 3D workload

Chosen release target:

- `point_in_volume`

Reason:

- it provides the non-graphical user story that the 3D ray/triangle substrate
  alone does not
- it is the cleanest 3D analog to the current `pip` mental model
- it uses the proven 3D primitive without making RTDL look like a renderer

### Objective 3: define exact public contracts

For every new `v0.4` 3D feature:

- input types
- precision limits
- backend coverage
- accepted boundaries
- exact vs bounded claims

### Objective 4: add one non-demo user-facing 3D example chain

The front-door examples should include at least one 3D example that is clearly
non-graphical:

- not a movie
- not a polished visual artifact
- a direct geometric-query example that shows why 3D support matters

This is a release-entry requirement, not an optional side objective.

### Objective 5: keep demos as proof, not product center

The hidden-star demo should remain:

- public proof that RTDL can sit inside a Python-hosted application

It should not become:

- the main definition of RTDL

### Objective 6: align performance and validation story

`v0.4` should force a cleaner release story:

- which 3D workloads are reference-clean on which backends
- which ones are bounded
- which ones are performance claims versus proof-of-capability claims

Important honesty note:

- `v0.4` may begin as a correctness-first 3D release rather than a
  performance-first one
- if no honest external 3D comparison baseline exists yet, the release docs
  must say that directly rather than silently inheriting the `v0.1`/`v0.2`
  performance narrative

## What v0.4 should not be

Do not make `v0.4` into:

- a "better movie" release
- a pure backend-refactor release
- a vague "more demos, more platforms" milestone

Those would consume effort without solving the core identity split left by
`v0.3.0`.

## Decision

Recommended decision:

- **make `v0.4` a workload-language-first milestone**
- use the `v0.3.0` hidden-star and ray/triangle work as supporting evidence
- convert bounded 3D query capability into explicit non-graphical public
  workload surface

## Immediate next planning questions

To open `v0.4` cleanly, answer these first:

1. What exact accepted-boundary wording will define `point_in_volume`:
   - closed or watertight meshes only
   - boundary policy
   - excluded degeneracies
2. Which backends must be required for `v0.4` acceptance:
   - CPU reference
   - oracle
   - Embree
   - OptiX
   - Vulkan
3. What is the minimal non-demo 3D example that teaches the new feature
   directly?
4. Is `v0.4` a correctness-first release, or is there an honest external 3D
   baseline for a performance story?

## Codex provisional conclusion

The strongest `v0.4` move is not to chase prettier demos. It is to:

- formalize `ray_tri_hitcount_3d` as a real public substrate feature
- then make `point_in_volume` the concrete non-graphical workload that gives
  the release its identity

That package is clearly non-graphical, explicitly contracted, and honest about
backend maturity.
