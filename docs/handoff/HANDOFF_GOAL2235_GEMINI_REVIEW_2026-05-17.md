# Handoff: Goal2233 + Goal2235 Gemini Review

Please perform a precise independent Gemini review of the prepared ray/segment
group-count work and write the result to:

`docs/reviews/goal2236_gemini_review_goal2233_2235_prepared_group_count_2026-05-17.md`

Important: this review is about ray/segment/group-count primitives only. Do not
describe database fields, DB clauses, `OptixDbDatasetImpl`, or
`PreparedOptixExecution`; those are unrelated to this goal.

Read these files:

- `docs/reports/goal2233_prepared_ray_segment_group_count_2026-05-17.md`
- `docs/reports/goal2235_prepared_ray_segment_odd_parity_2026-05-17.md`
- `tests/goal2233_prepared_ray_segment_group_count_test.py`
- `tests/goal2235_prepared_ray_segment_odd_parity_test.py`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`

Facts to verify from source and reports:

1. Goal2233 adds prepared scene reuse for `rtdl_optix_prepare_ray_segment_group_count_2d`, `rtdl_optix_run_prepared_ray_segment_group_count_2d`, and destroy.
2. Goal2235 adds compact odd-parity output via `rtdl_optix_run_prepared_ray_segment_group_odd_parity_2d` and Python `PreparedOptixRaySegmentGroupCount2D.run_odd_parity`.
3. The API vocabulary is app-agnostic: rays, segments, group ids, counts, parity. It must not be described as RayJoin, PIP, polygon, county, map, or spatial-join logic.
4. Pod evidence:
   - Goal2233 prepared full-count median: 0.820912s
   - Goal2235 compact odd-parity median: 0.282348s
   - legacy optimized PIP median in Goal2235 probe: 0.031503s
   - compact odd-parity matched legacy positive rows exactly: 879 rows
5. Boundary:
   - these goals do not authorize v2.0 release,
   - do not authorize broad RayJoin/PIP speedup claims,
   - do not claim fully device-resident grouped reduction,
   - and conclude that a better generic closed-shape membership or predicate primitive is still needed for RayJoin-style PIP performance.

Use one verdict:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Expected likely verdict: `accept-with-boundary`.

The review must state clearly that it is an independent Gemini review distinct
from Codex.
