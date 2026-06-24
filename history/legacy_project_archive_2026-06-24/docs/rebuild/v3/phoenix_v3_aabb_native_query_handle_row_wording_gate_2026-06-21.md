# Phoenix V3 AABB Native Query-Handle Row Wording Gate

Status: `aabb_native_query_handle_row_wording_gate_closed_after_claude_codex_m7_review`

This packet records approved row-scoped wording for the AABB native prepared-query-handle evidence after Claude external review and Codex consensus.
It promotes only the two exact native-query-handle rows and does not authorize release, whole-app, broad AABB, or V3-over-V2 wording.

## Candidate Rows

### aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50

- Generic capability: `aabb_candidate_stream`
- Primitive contract: `generic_prepared_aabb_index_query_2d_native_query_handle`
- Dataset: `jittered_grid`
- AABBs / box queries: `32768` / `32768`
- Warmup / repeat: `3` / `50`
- Cold-plus-collect wall speedup: `1.719x`
- Query-total speedup: `1.867x`
- Matches CPU reference: `true`
- Native query-handle cache observed: `true`
- Prepare note: OptiX prepare remains slower than Embree on this row; the candidate wording therefore uses cold-plus-collect wall and query_total, not prepare-only claims.
- Approved row-scoped wording: On an NVIDIA RTX 4000 Ada Generation GPU, RTDL's OptiX native prepared-query-handle route for `AABB_INDEX_QUERY_2D range_intersection_rows` was 1.719x faster than the RTDL Embree route on a jittered-grid workload with 32,768 AABBs and 32,768 packed box queries, measured as cold prepare plus collect wall time with warmup=3 and repeat=50. Query total was 1.867x faster. OptiX prepare alone remains slower than Embree; the speedup applies to end-to-end prepared-session time. This result is row-scoped and does not claim Contact Manifold solver acceleration, broad AABB-index acceleration, or V3-over-V2 speedup.

### aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50

- Generic capability: `aabb_candidate_stream`
- Primitive contract: `generic_prepared_aabb_index_query_2d_native_query_handle`
- Dataset: `jittered_grid`
- AABBs / box queries: `65536` / `65536`
- Warmup / repeat: `3` / `50`
- Cold-plus-collect wall speedup: `1.637x`
- Query-total speedup: `1.743x`
- Matches CPU reference: `true`
- Native query-handle cache observed: `true`
- Prepare note: OptiX prepare remains slower than Embree on this row; the candidate wording therefore uses cold-plus-collect wall and query_total, not prepare-only claims.
- Approved row-scoped wording: On an NVIDIA RTX 4000 Ada Generation GPU, RTDL's OptiX native prepared-query-handle route for `AABB_INDEX_QUERY_2D range_intersection_rows` was 1.637x faster than the RTDL Embree route on a jittered-grid workload with 65,536 AABBs and 65,536 packed box queries, measured as cold prepare plus collect wall time with warmup=3 and repeat=50. Query total was 1.743x faster. OptiX prepare alone remains slower than Embree; the speedup applies to end-to-end prepared-session time. This result is row-scoped and does not claim Contact Manifold solver acceleration, broad AABB-index acceleration, or V3-over-V2 speedup.

## Remaining Blockers Before M7

- none

## Forbidden Public Wording

- V3-over-V2 speedup
- full Contact Manifold solver speedup
- broad AABB-index acceleration
- all benchmark apps are accelerated
- release-ready
- OptiX prepare phase is faster than Embree
- any AABB native-query-handle row outside the two exact stable row ids

## Checks

- `candidate_evidence_exists`: `true`
- `row_ids_defined`: `true`
- `row_ids_are_unique`: `true`
- `row_ids_are_stable_native_query_handle_ids`: `true`
- `all_rows_clear_material_floor`: `true`
- `all_rows_match_cpu_reference`: `true`
- `raw_oracle_closed`: `true`
- `stability_closed`: `true`
- `review_gate_or_final_reviews_close_public_wording`: `true`
- `gemini_final_attempt_recorded_as_blocked`: `true`
- `source_evidence_flags_remain_false`: `true`

Failed checks: `[]`

## Goal-Level Decision Self-Audit

Decision: Close AABB native-query-handle row wording after Claude external review and Codex consensus while keeping release and broad claims false.

1. Was I foolish? No. The stable row IDs are now reviewed, the approved wording preserves the slower-prepare disclosure, and release/broad flags remain false.
2. If yes, what actions made the decision foolish? The foolish action would be to leave this gate in pre-review draft mode after real Claude/Codex review, or to generalize the two rows into a release claim.
3. Was there another path? Skip row materialization and move to RTNN. That is technically valid, but it leaves an already material AABB candidate with avoidable local blockers.
4. Can I now try a different path? Use this wording closure as an exact-row input to the AABB review gate, then continue RTNN and Spatial without broad V3-over-V2 wording.
