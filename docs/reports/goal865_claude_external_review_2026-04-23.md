# Goal865 External Review — Claude

Date: 2026-04-23
Verdict: **ACCEPT**

## Question

Is it correct and honest to make `road_hazard_screening` explicitly depend on
the Goal864 segment/polygon packet state, with the renamed statuses and strict
`ready_for_review` gate?

## Findings

**Dependency is factually accurate.**
`road_hazard_screening` is built on the segment/polygon hit-count primitive.
Making that dependency machine-readable and explicit does not introduce a new
constraint — it records one that already exists.

**Status renaming is honest and more informative.**
- `needs_segment_polygon_real_optix_artifact` names the exact missing evidence
  rather than leaving it implicit. No ambiguity is added.
- `blocked_by_segment_polygon_gate_failure` correctly attributes the block to
  its upstream source.

**Strict propagation rule is correct.**
Allowing road hazard to reach `ready_for_review` only when the upstream is
`ready_for_review` is the right gate. A downstream app should not outrun its
core primitive in promotion state.

**No overclaiming.**
The packet explicitly sets `allowed_claim_today: "no RTX road-hazard speedup
claim today"` and the boundary statement confirms this goal does not promote
`road_hazard_screening` into an active RTX claim path. The current derived
status (`needs_segment_polygon_real_optix_artifact`) accurately matches the
Goal864 artifact, which shows the OptiX library is missing and no native gate
run succeeded.

**Code and tests are correct.**
All three upstream branches are covered. Test assertions match the production
mapping. CLI test verifies file output and stdout payload. No gaps.

## Verdict

ACCEPT
