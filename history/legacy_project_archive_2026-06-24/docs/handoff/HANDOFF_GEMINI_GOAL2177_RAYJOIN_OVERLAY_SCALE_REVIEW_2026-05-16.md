# Handoff: Goal2177 RayJoin Overlay Scale Review

Please perform an independent Gemini review of Goal2177 and write the review to:

`docs/reviews/goal2178_gemini_review_goal2177_rayjoin_overlay_scale_2026-05-16.md`

## Files To Read

- `docs/reports/goal2177_rayjoin_overlay_scale_pod_evidence_2026-05-16.md`
- `docs/reports/goal2177_overlay384_scale_pod_2026-05-16.json`
- `docs/reports/goal2177_overlay512_scale_pod_2026-05-16.json`
- `tests/goal2177_rayjoin_overlay_scale_pod_evidence_test.py`
- `scripts/goal2159_rayjoin_public_cdb_runner.py`
- `docs/reports/goal2175_larger_rayjoin_overlay_seed_reference_fix_and_pod_evidence_2026-05-16.md`
- `docs/reviews/goal2176_gemini_review_goal2175_larger_rayjoin_overlay_2026-05-16.md`

## Review Questions

1. Verify that the two new scale cases are generic overlay-seed cases and do not add app-specific native engine behavior:
   - `overlay_county384_soil384`
   - `overlay_county512_soil512`
2. Verify the pod artifact numbers:
   - commit: `f161c8aafdfc0a469c4e23f92859b810e9f9b8be`
   - 384 row count: `130320`
   - 384 CPU/native-oracle median: `11.283897565677762`
   - 384 Embree median: `0.4652921035885811`
   - 384 OptiX one-shot median: `0.1776761505752802`
   - 384 prepared OptiX median: `0.18610582500696182`
   - 512 row count: `233766`
   - 512 CPU/native-oracle median: `35.65697741787881`
   - 512 Embree median: `1.1881687752902508`
   - 512 OptiX one-shot median: `0.3221710389479995`
   - 512 prepared OptiX median: `0.33615634217858315`
   - all backends parity-clean for both cases
3. Judge whether the narrow scale interpretation is valid:
   - one-shot OptiX beats Embree by `2.619x` on 384
   - one-shot OptiX beats Embree by `3.688x` on 512
   - the OptiX-over-Embree advantage widens from the accepted Goal2175 256 row to 384 and 512
   - prepared OptiX remains useful as an option but is not the fastest path for these one-shot rows
4. Verify that the report does not overclaim:
   - no full RayJoin paper reproduction
   - no broad RT-core speedup
   - no v2.0 release authorization
   - no whole-app RayJoin speedup
   - no claim against stronger CUDA/CuPy spatial-prefilter baselines

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This is performance/public-claim-adjacent work, so please be conservative.
