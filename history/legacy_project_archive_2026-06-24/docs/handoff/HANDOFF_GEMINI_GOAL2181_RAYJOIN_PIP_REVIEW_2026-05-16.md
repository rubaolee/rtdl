# Handoff: Goal2181 RayJoin PIP Review

Please perform an independent Gemini review of Goal2181 and write the review to:

`docs/reviews/goal2182_gemini_review_goal2181_rayjoin_pip_2026-05-16.md`

## Files To Read

- `docs/reports/goal2181_rayjoin_pip_shared_reference_pod_evidence_2026-05-16.md`
- `docs/reports/goal2181_pip512_shared_reference_pod_2026-05-16.json`
- `tests/goal2181_rayjoin_pip_shared_reference_pod_evidence_test.py`
- `scripts/goal2159_rayjoin_public_cdb_runner.py`
- `docs/reports/goal2179_rayjoin_lsi_shared_reference_pod_evidence_2026-05-16.md`
- `docs/reports/goal2177_rayjoin_overlay_scale_pod_evidence_2026-05-16.md`

## Review Questions

1. Verify that the PIP runner change is a harness/reference-sharing change, not a native engine ABI or app-specific engine change:
   - `_run_pip_direct_backend`
   - shared CPU Python reference rows
   - existing generic `rayjoin_point_location_positive_hits_reference`
2. Verify the pod artifact numbers:
   - commit: `173a12bca288a9bbddff4386fb1417c4d388be75`
   - case: `pip_county512`
   - points: `512`
   - polygons: `481`
   - candidate pairs: `246272`
   - rows: `1430`
   - CPU/native-oracle median: `0.01641024276614189`
   - Embree median: `0.004545821808278561`
   - OptiX median: `0.0047996435314416885`
   - all backends parity-clean
3. Judge whether the boundary interpretation is valid:
   - Embree and OptiX both beat CPU/native-oracle
   - Embree is slightly faster than OptiX on this PIP row
   - this supports the conclusion that OptiX does not win every RayJoin subproblem
4. Verify that the report does not overclaim:
   - no full RayJoin paper reproduction
   - no broad RT-core speedup
   - no v2.0 release authorization
   - no whole-app RayJoin speedup
   - no claim that OptiX wins every RayJoin subproblem

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This is performance/public-claim-adjacent work, so please be conservative.
