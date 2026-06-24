# Phoenix V3 Spatial Exact-F64 Adverse-Subset Parity

Status: `spatial_rayjoin_relation_status_exact_f64_adverse_subset_parity_pass_not_m7`

This packet closes the adverse-subset parity blocker only. It does not promote M7.

## Evidence

- Evidence: `docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_adverse_subset_20260621/br_county_subset_relation_status_exact_f64_r20_s5.json`
- Dataset: `tests/fixtures/rayjoin/br_county_subset.cdb`
- GPU: `NVIDIA RTX 4000 Ada Generation, 550.127.05`
- Count mode: `relation_status_corrected_executor_validated`
- Query repeat: `20`
- Sample repeat: `5`

## Result

- Row count: `6`
- Row count consistent: `true`
- Prepared-query median: `0.000101637s`
- Prepared-query repeat total median: `0.002076499s`
- Runner wall median: `0.004245825s`
- Query-stream residency: `device_resident_prepared_point_probe_columns_with_reusable_relation_status_corrected_executor`

## Native First-Sample Counters

- Raw AABB candidate count: `6`
- Boundary-status candidate count: `6`
- Dropped by exact-f64 predicate: `0`
- Emitted exact count: `6`
- Row stream materialized: `False`

## Claim Boundary

- Adverse-subset parity closes blocker: `true`
- M7 rows added: `0`
- M7 promotion authorized: `false`
- Release authorized: `false`
- Public speedup claim authorized: `false`
- Broad V3-over-V2 claim authorized: `false`
- RTDL-beats-RayJoin claim authorized: `false`
- True zero-copy claim authorized: `false`

## Checks

- `evidence_exists`: `true`
- `status_non_authorizing`: `true`
- `dataset_is_adverse_subset`: `true`
- `count_mode_validated_exact_f64`: `true`
- `sample_repeat_is_five`: `true`
- `query_repeat_is_twenty`: `true`
- `failed_checks_empty`: `true`
- `summary_row_count_consistent`: `true`
- `summary_row_count_is_six`: `true`
- `full_m3_table_complete`: `true`
- `m7_rows_added_zero`: `true`
- `m7_promotion_false`: `true`
- `release_false`: `true`
- `all_top_level_claim_flags_false`: `true`
- `all_sample_claim_flags_false`: `true`
- `all_samples_row_count_six`: `true`
- `all_samples_query_stream_resident`: `true`
- `all_samples_prepared_handle_generic`: `true`
- `all_samples_native_scalar_count`: `true`
- `all_samples_relation_status_correction_used`: `true`
- `all_samples_no_row_stream_materialized`: `true`
- `first_sample_validation_authority_recorded`: `true`

Failed checks: `[]`

## Interpretation

The exact-f64 relation-status scalar-count route also passes the small br_county_subset adverse/parity fixture with row_count 6, full M3 accounting, prepared query-stream residency, and no public claim flags. This closes only the adverse-subset parity blocker; it does not authorize M7, release, RayJoin-author comparison, paper reproduction, broad V3-over-V2 wording, or true zero-copy wording.

## Goal-Level Decision Self-Audit

Decision: Record Spatial exact-f64 adverse-subset parity as a blocker closure, not a promotion.

1. Was I foolish? No. The public-county repair needed a second small adverse fixture before it could even remain under review as a generic point-location route.
2. If yes, what actions made the decision foolish? The foolish action would be to use this tiny subset as speed evidence or to treat parity on one adverse fixture as release readiness.
3. Was there another path? I could have skipped the subset and kept chasing timing. That would leave a correctness hole open and make the 3.680x internal delta easier to overclaim.
4. Can I now try a different path? Close only this blocker, keep author-basis and external-review gates open, and move the route forward only through M7 review discipline.
