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
- Goal3306 showed that resident prepared point-probe columns help repeated-query timing modestly: point upload leaves the timed lane and PIP prepared-query median improved from about 0.343 ms to 0.317 ms on the same A5000 commit. The native count pass stayed near 0.261 ms, so this is not enough to close the RayJoin gap and is not a one-shot win if point-column preparation is charged to a single query.
- Goal3308 moved the prepared-points count buffer and launch-parameter buffer into the reusable point-probe handle. This improved the PIP prepared-query median again to about 0.303 ms, but the native count pass still stayed near 0.262 ms.
- Goal3310 added a generic prepared-points batch count surface. It improved repeated-query per-request throughput to about 0.242 ms at 32 queued requests on the A5000 RayJoin PIP slice, but it exposed the native scalar-count traversal floor instead of closing the one-shot RayJoin gap.
- Goal3312 tested CUDA graph replay for the prepared-points batch count path. The graph replay returned zeros on a live A5000 smoke while trusted single/batch counts returned the exact count, so the Python wrapper now fails closed on replay mismatch. Do not use this graph path as performance evidence until the native replay mismatch is fixed.
- Goal3314 added an opt-in stream pool for the generic prepared-points batch scalar-count path. On the A5000 RayJoin PIP slice, 8 streams at 32 requests improved repeated-query per-request median time from about 0.236 ms to about 0.0365 ms while preserving exact count 1430. This is repeated-query throughput evidence only, not one-shot RayJoin latency evidence.
- Goal3316 made the `RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT=auto` policy reachable from the probe and recorded effective stream counts in the artifact. On the same A5000 slice, auto selected 8 streams at 32 requests and 16 streams at 64 requests, reaching about 0.0359 ms/request and 0.0343 ms/request respectively. The next runtime ergonomics step is a persistent prepared batch executor or stream pool so streams are not created/destroyed on every batch call.
- Goal3318 added that persistent prepared batch executor for the generic prepared-point scalar-count path. It modestly improved the auto path to about 0.0349 ms/request at 32 requests and 0.0332 ms/request at 64 requests by reusing streams, count buffers, and launch-parameter buffers. The remaining cost is now mostly traversal/count work, so the next large RayJoin-relevant leap likely needs a more compact generic closed-shape predicate-count primitive or prepared boundary/range acceleration.
- Current best direction is still the generic scalar-count lane, now with `device_filtered_prepared_points_validated + inclusive + z_point + scalar count pipeline` when repeated query points can be prepared. Further improvement likely requires a more compact fused native scalar-count path or another generic closed-shape predicate-count primitive that reduces per-request traversal overhead.
- Keep the public claim boundary narrow: these are route-tuning facts, not RayJoin paper reproduction or broad RT-core speedup claims.
