# Future Version To-Do List

This file catches design ideas that should not interrupt the current release or internal-preview lane.

## Generic Adapter Naming

- Consider introducing a generic alias for the Hausdorff adapter shape now named `directed_hausdorff_2d_partner_columns`.
- Candidate generic concept: `directed_max_of_nearest_distance_2d` or `max_distance_nearest_candidate_2d`.
- Rationale: the current native/runtime layers remain app-agnostic, but the adapter name carries algorithm vocabulary. A generic primary name plus `hausdorff` as a discovery alias would improve reuse and align with the primitive discovery duplicate gate.
- Boundary: do not rename the public benchmark app casually; preserve user compatibility and only add aliases/migration helpers when this becomes a real versioned goal.

## Generic Closed-Shape Boundary Selection

- Add a generic prepared point-to-closed-shape boundary-selection primitive inspired by the RayJoin PIP benchmark gap.
- Candidate generic concept: `point_closed_shape_best_boundary_crossing_2d` or `point_closed_shape_first_crossing_2d`.
- Rationale: RayJoin's fast PIP path traces one upward ray per point and keeps the best crossing boundary event/edge on device. RTDL's current generic point/closed-shape membership count can now use device-filtered scalar count and `z_point` traversal, but it still trails RayJoin on the same slice because it is a membership-count contract over polygon AABBs rather than an edge-range best-crossing contract.
- Engine boundary: this must stay generic. The native engine should expose prepared edge/range traversal and return typed boundary-event columns such as query id, shape id, boundary id, crossing parameter, and tie-break status. RayJoin-specific map ids, simulation-of-simplicity policy, polygon assignment interpretation, and output-chain logic stay in the benchmark app or partner layer.
- Likely prerequisites: prepared edge AABB/range acceleration, deterministic tie-break policy, typed boundary-event columns, optional per-query best-event reduction, and same-contract validation against the existing exact inclusive membership path.
- Boundary: do not merge RayJoin-specific `closest_eid` semantics into the public engine ABI. This belongs in a future v2.x/v3.x primitive design, not in the current v2.8 route-tuning evidence.

## RayJoin PIP Scalar-Count Lessons

- Goal3300 proved that materializing generic boundary-event columns plus grouped count is the wrong performance route for PIP membership/count on the 512-feature RayJoin slice: the grouped count is cheap, but boundary-event column production emits thousands of rows and is much slower than scalar count.
- Goal3303 ruled out two easy scalar-count knobs: prepared closed-shape edge layout was slower on the A5000 slice, and `crossing_only` boundary mode failed exact inclusive validation (`129 != 1430`).
- Current best direction is still the generic scalar-count lane (`device_filtered_validated + inclusive + z_point + scalar count pipeline`), with further improvement likely requiring launch/Python overhead amortization, resident prepared query columns, or a more compact fused native scalar-count path.
- Keep the public claim boundary narrow: these are route-tuning facts, not RayJoin paper reproduction or broad RT-core speedup claims.
