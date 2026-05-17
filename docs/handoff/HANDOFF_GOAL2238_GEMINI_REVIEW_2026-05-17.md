# Handoff: Goal2238 Gemini Review

Please perform an independent Gemini review of Goal2238 and write it to:

`docs/reviews/goal2239_gemini_review_goal2238_closed_shape_membership_2026-05-17.md`

Read these files:

- `docs/research/future_version_to_do_list.md`
- `docs/reports/goal2238_closed_shape_membership_primitive_2026-05-17.md`
- `tests/goal2238_closed_shape_membership_primitive_test.py`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`

Review requirements:

1. Confirm the future-version to-do list exists and is appropriate for catching deferred ideas without making them release commitments.
2. Confirm Goal2238 exposes a generic app-agnostic closed-shape membership surface:
   - `rtdl_optix_run_point_closed_shape_membership_2d`
   - `closed_shape_membership_2d_optix`
   - row fields `point_id`, `shape_id`, `membership`
3. Confirm the new public vocabulary avoids RayJoin/PIP/polygon/county/map/spatial-join naming.
4. Confirm the implementation honestly wraps the existing optimized closed-boundary path and converts legacy internal rows into generic public rows, without claiming the old internal implementation has been fully rewritten.
5. Verify the pod evidence:
   - functional rows: point 1 -> shape 10 and point 3 -> shape 11
   - RayJoin-style 10,000-query probe row match: true
   - generic closed-shape median: `0.03738784417510033`
   - legacy optimized median: `0.03850874863564968`
   - ratio: `0.9708922128019587`
   - row count: 879
6. Check the boundary: no v2.0 release claim, no broad RayJoin/PIP speedup claim, no full RayJoin reproduction claim.

Use one verdict:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Expected likely verdict: `accept-with-boundary`.

State clearly that this is an independent Gemini review distinct from Codex.
