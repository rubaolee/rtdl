# Phoenix V3 13-Row Release Gate Update Review Request

Reviewer: Claude
Requested by: Codex
Date: 2026-06-22

## Scope

Please critically review the Phoenix V3 gate update that integrates the newly accepted Spatial default-path row into the current release surface.

This is not a request to authorize V3 release by default. The requested verdict is whether the gate update is internally consistent and whether any blocker remains before release authorization.

## Files To Review

- `scripts/v3_phoenix_next_engine_work_queue.py`
- `scripts/v3_phoenix_release_surface_breadth_gate.py`
- `scripts/v3_phoenix_release_readiness_gate.py`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json`
- `docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md`
- `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`
- `docs/reviews/claude_phoenix_v3_spatial_default_path_promotion_review_2026-06-22.md`
- `docs/reviews/codex_phoenix_v3_spatial_default_path_promotion_2ai_consensus_2026-06-22.md`

## Current Intended State

- Base M7 packet remains historical and unmodified at 12 rows.
- The current release surface is 13 rows: 12 base rows plus one reviewed Spatial supplemental row:
  `point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7`.
- Capability coverage is now 9/9 planned generic capability families.
- The Spatial row is accepted only as a bounded default-path topology-stream row.
- The Spatial row does not authorize RTDL-beats-RayJoin, whole Spatial RayJoin, public speedup, true zero-copy, V4 embedding, package-install, portability, or broad V3-over-V2 wording.
- Release remains blocked with `release_authorized: false` because there is not yet a fresh aggregate 13-row release-readiness consensus.

## Local Verification Already Run

```text
py -3 -m unittest tests.v3_phoenix_next_engine_work_queue_test tests.v3_phoenix_release_surface_breadth_gate_test tests.v3_phoenix_release_readiness_gate_test
Ran 12 tests ... OK
```

## Questions

1. Are the three gate scripts and generated artifacts internally consistent?
2. Is it correct that the stale `missing_point_location_topology_stream_m7_capability_family` blocker is removed?
3. Is it correct that release remains blocked pending a fresh aggregate 13-row release-readiness consensus?
4. Are there any P0/P1 issues before Codex records a 2-AI consensus for this gate update?

Please answer with:

- Verdict: one of `approve_not_release`, `approve_with_amendments_not_release`, `block_p0`, or `block_p1`.
- Findings ordered by severity.
- Required fixes, if any.
- Explicit statement whether this review authorizes release. It should not unless you intentionally say so.
