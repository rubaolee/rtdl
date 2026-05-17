# Handoff: Goal2179 RayJoin LSI Review

Please perform an independent Gemini review of Goal2179 and write the review to:

`docs/reviews/goal2180_gemini_review_goal2179_rayjoin_lsi_2026-05-16.md`

## Files To Read

- `docs/reports/goal2179_rayjoin_lsi_shared_reference_pod_evidence_2026-05-16.md`
- `docs/reports/goal2179_lsi512_shared_reference_pod_2026-05-16.json`
- `tests/goal2179_rayjoin_lsi_shared_reference_pod_evidence_test.py`
- `scripts/goal2159_rayjoin_public_cdb_runner.py`
- `docs/reports/goal2177_rayjoin_overlay_scale_pod_evidence_2026-05-16.md`
- `docs/reviews/goal2178_gemini_review_goal2177_rayjoin_overlay_scale_2026-05-16.md`

## Review Questions

1. Verify that the LSI runner change is a harness/reference-sharing change, not a native engine ABI or app-specific engine change:
   - `_run_lsi_direct_backend`
   - shared CPU Python reference rows
   - existing generic `county_zip_join_reference`
2. Verify the pod artifact numbers:
   - commit: `19a090702c0ea32eee247866743cd44afeb2ede1`
   - case: `lsi_county256_soil256_count512`
   - left segments: `19987`
   - right segments: `6825`
   - candidate pairs: `136411275`
   - rows: `269`
   - shared CPU Python reference build: `51.32344417180866` sec
   - Embree median: `0.20128264278173447`
   - OptiX one-shot median: `0.003221943974494934`
   - prepared OptiX median: `0.021941625513136387`
   - CuPy RawKernel brute-force median: `0.040767318569123745`
   - all backends parity-clean
3. Judge whether the narrow performance interpretation is valid:
   - hot one-shot OptiX beats Embree by `62.472x`
   - hot one-shot OptiX beats CuPy RawKernel brute force by `12.653x`
   - this supports the design conclusion that sparse true-hit LSI can benefit sharply from RT traversal
   - the report correctly separates cold-start/warmup from hot-repeat measurements
4. Verify that the report does not overclaim:
   - no full RayJoin paper reproduction
   - no broad RT-core speedup
   - no v2.0 release authorization
   - no whole-app RayJoin speedup
   - no claim against stronger CUDA/CuPy spatial-indexed baselines
   - no cold-start OptiX claim from the hot median

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This is performance/public-claim-adjacent work, so please be conservative.
