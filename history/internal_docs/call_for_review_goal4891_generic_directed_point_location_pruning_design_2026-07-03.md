# Call For Review: Goal4891 Generic Directed Point-Location Pruning Design

Date: 2026-07-03

Requested reviewers: Claude / Antigravity

Requested verdict labels:

- `approve_goal4891_design_authorize_pruning_proof_goal`
- `approve_with_amendments`
- `block_goal4891_redesign`

## Context

Goal4890 measured the traversal work denominator for the Australia
representative Section 5.7 workload and found that RTDL's public directed
point-location/PIP primitive performs 915x-6069x more segment-loop work than
AuthorPatch. Antigravity approved this result and authorized a generic pruning
design goal.

Goal4891 is that design goal. It does not implement code.

## File To Review

```text
history/internal_docs/goal4891_generic_directed_point_location_pruning_design_2026-07-03.md
```

Related evidence:

```text
history/internal_docs/goal4890_traversal_work_count_probe_result_2026-07-03.md
history/internal_docs/antigravity_goal4890_traversal_work_count_probe_review_2026-07-03.md
```

## Design Claim

The next proof should target a generic RTDL directed point-location
candidate-pruning mechanism, not writer work, Numba continuation work,
prepared-session work, row-buffer work, native micro-tuning, raw callbacks, or a
RayJoin-specific hidden kernel.

Recommended first proof:

- keep the public API shape unchanged;
- implement generic in-traversal pruning for directed point-location;
- preserve byte equality on Australia representative;
- measure query count, candidate segment-loop count, positive face count, and
  traversal time;
- require at least 10x candidate-count reduction on map0 before continuing;
- validate at least one second non-RayJoin-shaped synthetic directed
  point-location workload before claiming genericity.

## Review Questions

1. Does the design correctly respond to Goal4890's candidate-explosion evidence?
2. Is Route B, generic in-traversal pruning over the existing public directed
   point-location primitive, the right first proof?
3. Are the Route A/B/C distinctions clear enough to prevent a full compiler
   project from starting too early?
4. Is the 10x hard gate / 100x strong gate reasonable for a first proof?
5. Does the design sufficiently prevent a RayJoin-specific fast path from being
   smuggled in?
6. Is "no raw public callback API" the right boundary?
7. Are the verification gates enough before implementation?
8. What amendments are required before authorizing the implementation proof?

## Non-Authorization

This review request does not authorize implementation yet. It also does not
authorize:

- public performance claims;
- RayJoin-specific shortcuts;
- raw OptiX callback APIs;
- prepared sessions;
- row-buffer ABI;
- Numba partner API implementation;
- native micro-tuning before candidate reduction;
- public docs/release changes.
