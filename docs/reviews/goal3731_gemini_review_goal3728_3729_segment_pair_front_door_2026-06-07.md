# Gemini Review: Goal3728-3729 Segment-Pair Exact Count Front Door (2026-06-07)

## Verdict

accept

## Analysis

### 1. Is the front-door API generic and contract-shaped, or does it leak RayJoin/app semantics into the runtime?
The front-door API is generic and contract-shaped, and does not leak RayJoin/app semantics into the runtime. It names only segment pairs, prepared left/right sets, exact count, output contract, route, and backend, avoiding domain-specific terms. This is confirmed by explicit checks for forbidden terms in the test suite.

### 2. Is it appropriate that the front door routes to `count_prepared_left_grouped_range_direct_intersection(...)` while keeping the older `count_prepared_left(...)` route unchanged?
Yes, it is appropriate. The new front door provides access to a validated fast route (Goal3725) without altering the existing `count_prepared_left(...)` any-hit route or adding new native symbols. This ensures backward compatibility and allows for controlled adoption of the optimized path.

### 3. Does the RayJoin benchmark app adoption preserve app/engine separation?
Yes, the RayJoin benchmark app adoption preserves app/engine separation. The app wires its LSI scalar/count mode to the generic front door without embedding RayJoin-specific logic into the native engine. App-specific policy and interpretation remain in the Python application layer, as confirmed by the `segment_pair_count_route` metadata showing generic primitive details.

### 4. Does the pod artifact prove the app used the front door at runtime?
Yes, the pod artifact proves the app used the front door at runtime. The `summary.json` explicitly shows `"front_door_schema": "rtdl.optix.segment_pair_prepared_left_exact_intersection_count.front_door.v1"` within the `segment_pair_count_route` metadata, and the `native_phase_timings` record `"mode": "count_prepared_left_grouped_range_direct_intersection"`. This directly confirms the usage of the new front door and its underlying optimized route.

### 5. Are the claim boundaries strong enough, given the strong single-contract timing from Goal3725?
Yes, the claim boundaries are strong enough. Both Goal3728 and Goal3729 reports explicitly state that this work does not authorize public speedup claims, RayJoin paper reproduction claims, or any broad release or acceleration claims. The front door is also marked as "experimental." The pod artifact further confirms that all relevant claim boundary flags are `false`, maintaining strict control over what can be claimed.

### 6. What should the next engineering target be after this adoption: grouped count/Boolean continuations, additional RayJoin contracts/datasets, or a non-diagnostic API promotion gate?
Based on the "Next Step" section in the Goal3728 report, the next engineering target should be grouped count/Boolean continuations. This should only be pursued if they remain generic (contract-shaped) and are backed by robust pod evidence, similar to the current work.

## Evidence Verified

Goal3729 pod app validation:
- GPU: NVIDIA RTX A5000, driver 580.126.09.
- Commit: `a546fa58`.
- Dataset: RayJoin bundled Brazil soil + county CDB pair.
- Count: 20,860.
- Prepared query median: 0.000269813 s.
- Native phase mode: `count_prepared_left_grouped_range_direct_intersection`.
- Front-door schema: `rtdl.optix.segment_pair_prepared_left_exact_intersection_count.front_door.v1`.
- Primitive: `SEGMENT_PAIR_INTERSECTION_ROWS_2D`.
- Output contract: `scalar_exact_count`.
- All claim-boundary flags false.
