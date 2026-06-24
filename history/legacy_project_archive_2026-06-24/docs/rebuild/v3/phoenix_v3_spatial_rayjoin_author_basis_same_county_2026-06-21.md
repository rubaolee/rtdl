# Phoenix V3 Spatial Same-County Author Timing Basis

Status: `spatial_rayjoin_same_county_author_timing_present_not_m7`

This packet records a same-dataset RayJoin author timing basis for the
current Spatial exact-f64 candidate. It is not an M7 promotion.

## Verdict

- Same-dataset author timing basis present: `true`
- Author result count printed: `false`
- Author result count parity verified: `false`
- M7 promotion authorized: `false`
- RTDL-beats-RayJoin claim authorized: `false`

## Author Run

- Dataset: `data/rayjoin_public_cdb/br_county.cdb` as both `-poly1` and `-poly2`
- Query exec: `/workspace/RayJoin_fresh/release/bin/query_exec`
- GPU: `NVIDIA RTX 4000 Ada Generation, 550.127.05`
- Warmup/repeat: `5` / `50`
- Query point count from `optixLaunch` width: `342738`
- Query launch count: `55`
- RayJoin author Query timer: `1.865660 ms`
- RayJoin wrapper elapsed: `6.765306 s`

## RTDL Exact-F64 Reference

- Intake packet: `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_intake_2026-06-21.json`
- Count mode: `relation_status_corrected_executor_validated`
- Exact count: `47262`
- RTDL prepared-query median: `6.309319 ms`
- RTDL runner-wall median: `1.974891 s`
- Query-stream residency: `device_resident_prepared_point_probe_columns_with_reusable_relation_status_corrected_executor`

## Comparison

- RayJoin author Query speedup vs RTDL exact-f64 prepared query: `3.382x`
- RTDL exact-f64 prepared query relative to RayJoin author Query: `0.296x`
- RTDL runner-wall vs RayJoin wrapper ratio, not public-claim-authorized: `3.426x`

RayJoin author Query is the internal query_exec timer. RTDL exact-f64 prepared query is the RTDL M3 prepared-query median for the reusable device scalar-count executor. The timers are useful author-basis evidence, but they are not a whole-app or paper comparison and RayJoin does not print the result count in this run.

## Remaining Blockers Before M7

- `external_ai_review_missing`
- `codex_consensus_response_missing_after_external_review`
- `rayjoin_author_result_count_not_printed_or_public_scope_review_missing`
- `rayjoin_author_query_faster_than_rtdl_exact_f64_query`
- `route_name_semantically_stale_relation_status_corrected`
- `public_wording_review_missing`

## Checks

- `author_artifact_dir_exists`: `true`
- `author_stderr_exists`: `true`
- `author_stdout_empty_or_exists`: `true`
- `author_timing_query_ms_present`: `true`
- `author_repeat50_warmup5_launch_count`: `true`
- `author_query_point_count_positive`: `true`
- `same_public_county_dataset_sha_recorded`: `true`
- `query_exec_sha_recorded`: `true`
- `same_gpu_recorded`: `true`
- `rtdl_exact_f64_intake_not_m7`: `true`
- `rtdl_exact_count_47262`: `true`
- `author_query_faster_than_rtdl_prepared_query`: `true`
- `claim_flags_false`: `true`

Failed checks: `[]`

## Goal-Level Decision Self-Audit

Decision: Record same-dataset RayJoin author timing for the Spatial exact-f64 candidate without promoting it.

1. Was I foolish? No. The author run closes the missing-timing fact but shows RayJoin author Query is faster than the current RTDL exact-f64 prepared-query path.
2. If yes, what actions made the decision foolish? The foolish action would be to claim RTDL beats RayJoin, ignore that RayJoin does not print a result count here, or compare wrapper elapsed times as public speedup evidence.
3. Was there another path? I could have left the blocker as missing. That would be stale now that the POD author run exists.
4. Can I now try a different path? Use this packet to update the review gate from missing author timing to author timing present but not-M7, then continue only through external review, wording review, or generic engine work.
