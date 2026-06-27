# Call For Review: Phoenix V3 Spatial Relation-Status Exact-F64 Intake

Please critically review the Phoenix V3 Spatial RayJoin relation-status
exact-f64 native scalar-count intake.

This is not a request to bless a release. The desired review outcome is a
hard verdict on whether the current evidence can move from "intake/not-M7" to
"narrow M7 candidate worth further gates", or whether it must remain blocked.

## Files To Review

- Intake markdown:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_intake_2026-06-21.md`
- Intake JSON:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_intake_2026-06-21.json`
- Current queue:
  `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`
- Native source:
  `src/native/optix/rtdl_optix_workloads.cpp`
- Intake test:
  `tests/v3_phoenix_spatial_rayjoin_relation_status_exact_f64_intake_test.py`
- Source-level native test:
  `tests/goal3684_native_relation_status_corrected_scalar_count_test.py`
- POD evidence directory:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_attempt_20260621`
- Prior no-go:
  `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_corrected_no_go_2026-06-21.md`
- Prior exact executor evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_spatial_rayjoin_topology_m3_public_county_exact_executor_repeat50_20260621/summary.json`

## Facts Claimed By The Intake

- Prior relation-status corrected executor failed exact validation at
  `47,259 != 47,262`.
- The repaired native path uses device-side double precision
  `exact_closed_shape_membership_f64` for every AABB candidate.
- The new repeat50/sample5 RTX packet is exact and stable at `47,262` rows.
- Prepared-query median improves from `0.023217812s` to `0.006309319s`
  versus the prior exact executor, a `3.680x` improvement.
- Repeat=50 prepared-query total improves `3.703x`.
- Runner wall improves `1.465x`.
- Native counters: `155,555` raw AABB candidates, `47,550` boundary-status
  candidates, `108,293` exact-f64 rejects, `47,262` emitted exact hits.
- All release, public speedup, RTDL-beats-RayJoin, broad V3-over-V2, and
  true-zero-copy flags remain false.
- Current status remains
  `spatial_rayjoin_relation_status_exact_f64_device_scalar_count_intake_not_m7`.

## Review Questions

1. Is this genuinely a reusable V3 engine capability
   (`point_location_topology_stream` / native scalar-count route), or is it
   effectively Spatial RayJoin-specific tuning?
2. Does the evidence prove exactness strongly enough for an intake packet?
3. Does the evidence justify reopening a narrow M7-candidate review, or should
   it stay intake/not-M7 until additional gates are run?
4. What concrete blockers remain before any row-scoped M7 promotion?
5. Are the docs/tests enforcing the right claim boundary, or are they still
   vulnerable to overclaiming?
6. Are there hidden correctness risks in replacing relation-status keep logic
   with full exact-f64 any-hit counting on device?

## Required Verdict Format

Please return:

- `verdict`: approve-as-intake / approve-to-reopen-M7-candidate / reject
- `must_fix_before_M7`: bullet list
- `should_fix`: bullet list
- `claim_boundary_risks`: bullet list
- `recommended_next_action`: one paragraph

Be strict. A useful negative review is better than a polite approval.
