# Call For Review: Phoenix V3 Spatial Default-Path Promotion

Reviewer: Claude

Date: 2026-06-22

## Request

Please thoroughly and critically review the Phoenix V3 Spatial guarded squared-boundary default-path evidence.

The decision under review is narrow:

- Accept or reject the default-path promotion of the generic `point_location_topology_stream` candidate as a row-scoped M7 candidate for V3 Phoenix.
- Do not authorize broad V3-over-V2, whole-app, paper reproduction, RTDL-beats-RayJoin, zero-copy, or V4/embedding claims.
- Verify whether it is acceptable to move from "P1 default-path blocked" to "default-path evidence accepted, pending/eligible for release-surface gate update."

## Files To Inspect

- Candidate packet: `docs/rebuild/v3/phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.md`
- Candidate JSON: `docs/rebuild/v3/phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.json`
- Native source: `src/native/optix/rtdl_optix_workloads.cpp`
- Source contract test: `tests/goal3684_native_relation_status_corrected_scalar_count_test.py`
- Candidate test: `tests/v3_phoenix_spatial_relation_status_squared_boundary_candidate_test.py`
- Default-path POD evidence: `docs/rebuild/v3/evidence/phoenix_v3_spatial_default_path_20260622/default_path_guarded_squared_repeat50_sample7.json`
- Disable-control evidence: `docs/rebuild/v3/evidence/phoenix_v3_spatial_default_path_20260622/disable_control_both_zero_repeat10_sample1.json`
- Build log: `docs/rebuild/v3/evidence/phoenix_v3_spatial_default_path_20260622/build_optix.log`
- Previous Claude review: `docs/reviews/claude_phoenix_v3_spatial_squared_boundary_candidate_review_2026-06-21.md`
- Previous Codex consensus: `docs/reviews/codex_phoenix_v3_spatial_squared_boundary_candidate_2ai_consensus_2026-06-22.md`

## Evidence Summary

- Source now defaults both controls on through `relation_status_corrected_default_enabled(...)`.
- False-like values `0/false/off/no` disable each control.
- Default-path POD run used no enabling env flags:
  - median prepared query: `1.0805986821651459 ms`
  - exact row count: `47,262`
  - raw candidates: `[47,570]`
  - boundary candidates: `[47,550]`
  - dropped candidates: `[308]`
  - author Query timer bar: `1.865660 ms`
  - default-path vs author Query timer: `1.7265058997313072x`
  - default-path margin under author Query: `0.7850613178348542 ms`
- Disable-control smoke with both env flags set to `0`:
  - median prepared query: `5.804896354675293 ms`
  - raw candidates: `[155,555]`
  - dropped candidates: `[108,293]`
  - exact row count still `47,262`
  - default path is `5.371926183589535x` faster than this disable control.
- Guarded equivalence packet still records zero guarded mismatches and 10 pure-squared mismatch risks.
- All release/public/broad/zero-copy/V4 flags remain false.

## Questions

1. Does the default-path source change actually make the optimized route user-facing without relying on hidden enabling env flags?
2. Are the POD evidence, disable-control evidence, exact-count checks, and equivalence checks sufficient for a row-scoped M7 candidate?
3. Are there any P0/P1 blockers before the release-surface gate may count this as one `point_location_topology_stream` row?
4. Are the claim boundaries strict enough, especially around the author Query timer not printing a result count?
5. What exact follow-up wording or gate updates should Codex make if you accept this candidate?

Please return a verdict using one of:

- `accept`
- `accept_with_boundary`
- `reject`

Include concrete blockers and recommended edits.
