# Handoff: Goal2171 RayJoin Overlay Seed Baseline Review

Please perform an independent Gemini review of Goal2171 and write the review to:

`docs/reviews/goal2172_gemini_review_goal2171_rayjoin_overlay_seed_baseline_2026-05-16.md`

## Files To Read

- `docs/reports/goal2171_rayjoin_overlay_seed_baseline_2026-05-16.md`
- `docs/reports/goal2171_rayjoin_overlay_seed_baseline_pod_2026-05-16.json`
- `tests/goal2171_rayjoin_overlay_seed_baseline_test.py`
- `scripts/goal2159_rayjoin_public_cdb_runner.py`
- For context only:
  - `docs/reports/goal2169_optix_lsi_device_candidate_filter_2026-05-16.md`
  - `docs/reviews/goal2170_gemini_review_goal2169_optix_lsi_device_filter_2026-05-16.md`

## Review Questions

1. Verify that the artifact-backed numbers in the report match the JSON:
   - CPU median: `0.15251125488430262`
   - Embree median: `0.02216548379510641`
   - OptiX median: `0.025159044191241264`
   - rows: `14036`
   - commit: `7e4f440425b8e19caed147097945504b47aa9b81`
2. Verify that the interpretation is bounded:
   - RTDL accelerates this bounded overlay-seed row over the CPU Python reference.
   - OptiX is RT-core-accelerated but does not beat Embree on this row.
   - The report does not claim full RayJoin reproduction, broad RT-core speedup, or v2.0 release readiness.
3. Check whether the proposed next engineering target is technically reasonable:
   - a prepared/reused generic OptiX shape-pair relation surface, analogous to the prepared LSI surface from Goal2163.
4. Check whether the test meaningfully protects the artifact, claim boundary, and next-step interpretation.

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This is a performance/public-claim-adjacent goal, so please be conservative about claim wording.
