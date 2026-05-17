# Goal2240: Closed-Shape Membership 2-AI Consensus

Status: accepted with boundary.

## Evidence

- Codex implementation/report: `docs/reports/goal2238_closed_shape_membership_primitive_2026-05-17.md`
- Gemini review: `docs/reviews/goal2239_gemini_review_goal2238_closed_shape_membership_2026-05-17.md`
- Test gate: `tests/goal2238_closed_shape_membership_primitive_test.py`

## Consensus

Codex and Gemini agree that Goal2238 is a valid app-agnostic primitive
improvement:

- `rtdl_optix_run_point_closed_shape_membership_2d` is exposed as a generic
  native OptiX ABI.
- `closed_shape_membership_2d_optix` is exposed as the Python helper.
- The public row vocabulary is `point_id`, `shape_id`, and `membership`.
- The future-version to-do list now captures deferred ideas without authorizing
  release work by itself.

## Performance Evidence

On the RTX pod, the 10,000-query RayJoin-style probe showed:

- row match: `true`
- row count: `879`
- generic closed-shape median: `0.03738784417510033`
- legacy optimized median: `0.03850874863564968`
- ratio: `0.9708922128019587`

The accepted narrow conclusion is that the generic closed-shape wrapper reaches
the same performance class as the existing optimized closed-boundary path on
this probe, while preserving the app-agnostic public surface.

## Boundary

This does not authorize:

- v2.0 release,
- broad RayJoin speedup claims,
- broad PIP speedup claims,
- full RayJoin reproduction claims,
- or a claim that the old internal closed-boundary implementation has been fully
  rewritten.

The next RayJoin reproduction step remains a larger workload-level project with
its own evidence and consensus.
