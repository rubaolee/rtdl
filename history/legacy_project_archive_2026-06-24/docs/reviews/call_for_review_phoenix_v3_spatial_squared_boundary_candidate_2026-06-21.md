# Call For Review: Phoenix V3 Spatial Guarded Squared-Boundary Candidate

Please perform a critical external review of the Phoenix V3 Spatial
`point_location_topology_stream` guarded squared-boundary candidate.

Write your review to:

`docs/reviews/claude_phoenix_v3_spatial_squared_boundary_candidate_review_2026-06-21.md`

Use one verdict:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

## Context

Phoenix V3 is currently blocked as a major user-responsible V3 release because
it has 12 M7-qualified rows across 8 of 9 planned capability families. The
missing family is `point_location_topology_stream`.

The new candidate changes the generic OptiX relation-status corrected scalar
count executor under an explicit, default-off native flag:

`RTDL_OPTIX_RELATION_STATUS_CORRECTED_EXACT_F64_SQUARED_BOUNDARY`

It keeps the prior default-off zero-status prefilter flag:

`RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO`

The candidate replaces most full f64 membership boundary segment tests with
squared fast-path comparisons, but falls back to the existing
`sqrt(len2)`/`eps * len` predicate inside a small threshold guard band. The
equivalence packet records why this fallback is required: pure squared
comparison mismatches the old predicate on endpoint-adjacent floating cases.
It is intended to be generic closed-shape point-location predicate work, not
RayJoin-specific logic.

## Files To Review

- Source:
  - `src/native/optix/rtdl_optix_workloads.cpp`
- Candidate packet:
  - `docs/rebuild/v3/phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.md`
  - `docs/rebuild/v3/phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.json`
- Predicate-equivalence packet:
  - `docs/rebuild/v3/phoenix_v3_spatial_squared_boundary_equivalence_2026-06-21.md`
  - `docs/rebuild/v3/phoenix_v3_spatial_squared_boundary_equivalence_2026-06-21.json`
- Generator and test:
  - `scripts/v3_phoenix_spatial_squared_boundary_equivalence.py`
  - `tests/v3_phoenix_spatial_squared_boundary_equivalence_test.py`
  - `scripts/v3_phoenix_spatial_relation_status_squared_boundary_candidate.py`
  - `tests/v3_phoenix_spatial_relation_status_squared_boundary_candidate_test.py`
- POD evidence:
  - `docs/rebuild/v3/evidence/phoenix_v3_spatial_guarded_squared_boundary_20260621/baseline_prefilter_zero_repeat50_sample7.json`
  - `docs/rebuild/v3/evidence/phoenix_v3_spatial_guarded_squared_boundary_20260621/guarded_squared_prefilter_zero_repeat50_sample7.json`
  - `docs/rebuild/v3/evidence/phoenix_v3_spatial_guarded_squared_boundary_only_20260621/default_no_prefilter_repeat50_sample3.json`
  - `docs/rebuild/v3/evidence/phoenix_v3_spatial_guarded_squared_boundary_only_20260621/guarded_squared_only_no_prefilter_repeat50_sample3.json`
- Prior near-miss and author bar:
  - `docs/rebuild/v3/phoenix_v3_spatial_relation_status_prefilter_zero_experiment_2026-06-21.json`
  - `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_author_basis_same_county_2026-06-21.json`

## Key Facts To Audit

- Dataset: `data/rayjoin_public_cdb/br_county.cdb`
- POD/GPU: RTX 4000 Ada, driver 550.127.05, `213.173.108.14:11592`
- Candidate route: `relation_status_corrected_executor_validated`
- repeat/warmup/sample: `50 / 5 / 7`
- Baseline prefilter-zero median: `1.8956884741783142 ms`
- Guarded squared-boundary median: `1.0804496705532074 ms`
- Candidate sample range: `1.0787248611450195 ms` to `1.0819695889949799 ms`
- Speedup vs current prefilter-zero route: `1.7545365840203289x`
- Guarded-squared-only, no-prefilter median: `2.8457939624786377 ms`
- Guarded-squared-only speedup vs default no-prefilter route: `1.8991258155389625x`
- Guarded-squared-only does not clear author Query bar by itself.
- RayJoin author Query timer: `1.865660 ms`
- Candidate vs author Query timer: `1.726744013022608x`
- Predicate equivalence: guarded mismatch count `0` across `201260` cases;
  pure squared mismatch count recorded as `10`.
- Exact RTDL row count: `47262`, stable in all samples
- Raw/emitted/boundary/dropped counts match baseline:
  - raw `47570`
  - boundary `47550`
  - emitted `47262`
  - dropped `308`
- Author RayJoin run does not print result count; the author Query timer is a
  performance bar only.
- All public/release/whole-app/paper/RTDL-beats-RayJoin/true-zero-copy/V4 claim
  flags remain false in the candidate packet.
- Candidate is currently pending review and has not been promoted:
  - `m7_candidate: true`
  - `m7_promotion_authorized: false`
  - `m7_qualified_release_rows_added: 0`

## Review Questions

1. Is the source change genuinely generic point-location topology-stream work,
   or does it introduce RayJoin/app-specific behavior?
2. Is the guarded squared boundary test, including fallback, a safe
   correctness-preserving transformation of the existing f64 boundary condition?
3. Does the POD evidence support a serious pending M7 candidate rather than a
   toy or one-off result?
4. Is the comparison against the RayJoin author Query timer worded honestly
   given that the author run does not print result count?
5. Are the claim boundaries strict enough?
6. Before this can become a V3 user-facing M7 row, must the candidate become
   default-on rather than env-gated? If yes, say whether that is P0 or P1.
   Please consider the guarded-squared-only no-prefilter probe: it is a
   material generic optimization by itself, but the author Query bar is cleared
   only by the prefilter-zero plus guarded-squared-boundary combination.
7. List required fixes as P0/P1/P2. If there are no P0 blockers, say so
   explicitly.

## Expected Review Shape

Please include:

- Verdict
- P0 findings
- P1 findings
- P2 findings
- Evidence notes
- Recommendation for whether Codex should proceed to M7-consensus promotion,
  default-on hardening, or rejection/no-go
