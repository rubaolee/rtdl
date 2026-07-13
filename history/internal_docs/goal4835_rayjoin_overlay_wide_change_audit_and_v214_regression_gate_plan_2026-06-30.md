# Goal4835 Plan — RayJoin Overlay Wide-Change Audit and v2.14 Regression Gate

Date: 2026-06-30

Status: `in_progress`

## Purpose

Goal4834 closed the focused directed point-location SoS correctness repair:

- synthetic contract tests passed;
- rebuilt RTDL OptiX matched the public County x Soil answer byte-for-byte;
- no performance-win claim was authorized.

However, Claude's Goal4833 method review requires a wider cleanup before the
RayJoin line can safely proceed: broad edits to `src/rtdsl/rayjoin_overlay.py`
must not be grandfathered by the Goal4834 public-sample success, and any core
semantics change needs a v2.14-wide regression gate.

Goal4835 therefore audits every current RayJoin overlay behavioral change and
establishes the regression gate for the v2.14 product line.

## Scope

In scope:

1. Classify each current `rayjoin_overlay.py` behavioral change as:
   - `contract_supported`;
   - `externally_reviewed_prior_goal`;
   - `test_supported_but_needs_external_review`;
   - `insufficiently_supported_block_next_claim`;
   - `should_revert_before_release_claim`.
2. Link each retained change to a paper/source contract, synthetic test, and/or
   external review.
3. Run focused local tests for the RayJoin contract surface.
4. Run an available v2.14 regression gate locally; if full matrix is too large
   for the current turn, record the exact command and current partial gate
   status rather than pretending completion.
5. Write a review packet that asks whether the wide changes may remain.

Out of scope:

- new performance tuning;
- full Section 5.7 eight-pair claim;
- Embree work;
- V3/V4 work;
- public user-facing doc changes.

## Current Wide Changes To Audit

| Change area | File symbols | Prior evidence |
| --- | --- | --- |
| Per-map midpoint face storage | `RayjoinOverlayIntersection.mid_point_polygon_id_map0/map1`, `_assign_midpoint_faces`, `_midpoint_face_for_map`, `_assemble_output_chains` | Goal4820 + Antigravity review; public sample byte-equal |
| Non-finite midpoint filtering | `_midpoint_points_from_lsi_rows_numpy`, `_midpoints_for_sorted_xsects`, `midpoint_pip` telemetry | Goal4826 + Antigravity review; finite-query product invariant |
| Author scaled coordinate materialization | `_rayjoin_scaling_constants`, `_rayjoin_author_scale_array`, `_rayjoin_scaled_intersection_points_for_pairs`, `_rows_from_segment_pair_ids(... scale_bounds=...)` | Goal4827 + Antigravity review; author `ExactPoint`/internal-coordinate contract |
| Scaled/rational sorting and midpoint projection | `RayjoinOverlayIntersection.scaled_*`, `_sort_xsects_for_map(... scale_bounds=...)`, `_midpoints_for_sorted_xsects(... scale_bounds=...)` | Goal4827 + tests; still needs explicit Goal4835 audit closure |
| OptiX SoS reported-distance comparator | `directed_segment_sos_*` in `rtdl_optix_core.cpp` | Goal4834 + Antigravity review; synthetic gate |
| v2.14-wide regression | `scripts/run_test_matrix.py --group full` or bounded substitute | Outstanding before broad claim |

## Acceptance Gates

Goal4835 may close only if:

1. The audit table is written with one row per behavioral change.
2. Every retained wide change has at least one explicit test and/or prior
   external review reference.
3. Any insufficiently supported change is marked as a blocker for broad claims.
4. Focused RayJoin tests pass locally.
5. A v2.14 regression gate is run or explicitly recorded as outstanding with
   the exact command and reason.
6. A call-for-review packet is written.

## Decision Audit Requirement

At completion, answer:

1. Was I stupid?
2. If yes, what action made it stupid?
3. Was there another path that avoided being stuck on the wrong idea?
4. Can I now switch to the path that actually solves the problem?
