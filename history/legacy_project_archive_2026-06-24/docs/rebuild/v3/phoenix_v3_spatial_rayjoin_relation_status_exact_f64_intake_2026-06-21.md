# Phoenix V3 Spatial Relation-Status Exact-F64 Intake

Status: `spatial_rayjoin_relation_status_exact_f64_device_scalar_count_intake_not_m7`

This is an intake packet, not release authorization and not an M7 promotion.

## What Changed

- Previous relation-status corrected executor failed exact validation: candidate minus exact `-3`.
- Current native source uses `exact_closed_shape_membership_f64` on the device for each AABB candidate.
- Current public-county POD repeat50/sample5 evidence is exact and stable at `47262` rows.
- Full M3 phase table is present and all public/release claim flags remain false.

## Evidence

- New repeat packet: `docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_attempt_20260621/relation_status_exact_f64_repeat50_sample5.json`
- New smoke packet: `docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_attempt_20260621/relation_status_exact_f64_smoke.json`
- Build log: `docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_attempt_20260621/build-optix.log`
- Source manifest: `docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_attempt_20260621/source_manifest.sha256`
- Previous exact-executor packet: `docs/rebuild/v3/evidence/phoenix_v3_spatial_rayjoin_topology_m3_public_county_exact_executor_repeat50_20260621/summary.json`
- Previous no-go packet retained: `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_corrected_no_go_2026-06-21.json`

## Comparison Against Exact Executor

| Metric | Exact executor | Exact-f64 device scalar | Ratio |
| --- | ---: | ---: | ---: |
| Prepared query median | 0.023217812s | 0.006309319s | 3.680x |
| Prepared query repeat total | 1.168836027s | 0.315663926s | 3.703x |
| Runner wall median | 2.893970855s | 1.974891372s | 1.465x |
| Topology continuation median | 0.023139639s | 0.000000000s | n/a |

## Native First-Sample Counters

- Raw AABB candidate count: `155555`
- Boundary-status candidate count: `47550`
- Dropped by exact-f64 predicate: `108293`
- Emitted exact count: `47262`
- Row stream materialized: `False`

## Claim Boundary

- M7 rows added: `0`
- Release authorized: `false`
- Public speedup claim authorized: `false`
- Broad V3-over-V2 claim authorized: `false`
- RTDL-beats-RayJoin claim authorized: `false`
- True zero-copy claim authorized: `false`

## Checks

- `new_evidence_exists`: `true`
- `new_smoke_exists`: `true`
- `build_log_exists`: `true`
- `build_succeeded`: `true`
- `source_manifest_exists`: `true`
- `native_source_uses_exact_f64_full_predicate`: `true`
- `native_source_no_longer_keeps_status_one_without_exact_check`: `true`
- `smoke_exact_count_matches`: `true`
- `repeat_exact_count_matches`: `true`
- `row_count_consistent`: `true`
- `full_m3_phase_table_complete`: `true`
- `failed_checks_empty`: `true`
- `claim_flags_false`: `true`
- `native_scalar_count_no_row_stream`: `true`
- `native_exact_device_scalar_count`: `true`
- `old_no_go_retained`: `true`
- `old_no_go_added_no_m7_rows`: `true`

Failed checks: `[]`

## Interpretation

The prior relation-status route failed because it could not recover float32 device-prefilter false negatives. The current native source uses a device-side double full closed-shape predicate for each AABB candidate, which restores exact public-county parity and removes host topology continuation from the prepared query path. This is generic engine progress, not release or M7 authorization.

## Goal-Level Decision Self-Audit

Decision: Treat the exact-f64 relation-status scalar-count repair as a new Phoenix intake, not an automatic M7 promotion.

1. Was I foolish? No. The old route failed exactness; the repair changed the generic device predicate semantics and reran real POD evidence before any promotion.
2. If yes, what actions made the decision foolish? The foolish action would be to erase the old no-go, claim the smoke run as release evidence, or describe the row as RTDL beating RayJoin without author-basis review.
3. Was there another path? I could have abandoned Spatial after the no-go and tuned another app. That would avoid risk but would leave a known generic topology-stream bottleneck unsolved.
4. Can I now try a different path? Keep the route behind not-M7 gates, request 2-AI review, and only then consider a narrow row-scoped candidate.
