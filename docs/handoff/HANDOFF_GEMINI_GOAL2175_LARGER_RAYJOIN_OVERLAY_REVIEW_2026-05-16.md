# Handoff: Goal2175 Larger RayJoin Overlay Review

Please perform an independent Gemini review of Goal2175 and write the review to:

`docs/reviews/goal2176_gemini_review_goal2175_larger_rayjoin_overlay_2026-05-16.md`

## Files To Read

- `docs/reports/goal2175_larger_rayjoin_overlay_seed_reference_fix_and_pod_evidence_2026-05-16.md`
- `docs/reports/goal2175_overlay_count256_shared_reference_pod_2026-05-16.json`
- `tests/goal2175_larger_rayjoin_overlay_seed_reference_fix_and_pod_evidence_test.py`
- `tests/goal2175_overlay_reference_pair_set_materialization_test.py`
- `src/rtdsl/reference.py`
- `scripts/goal2159_rayjoin_public_cdb_runner.py`
- `docs/reports/goal2173_prepared_optix_shape_pair_relation_2026-05-16.md`
- `docs/reviews/goal2174_gemini_review_goal2173_prepared_optix_shape_pair_relation_2026-05-16.md`

## Review Questions

1. Verify that the `overlay_compose_cpu` reference change is a correctness-harness optimization, not a semantic change:
   - same output fields
   - same LSI and first-vertex PIP dependency flag semantics
   - pair-set materialization is reasonable for larger overlay rows
2. Verify the pod artifact numbers for `overlay_county256_soil256`:
   - commit: `9a4b8ae1ef054406eeda8475a51f24ed3f225459`
   - left polygons: `241`
   - right polygons: `236`
   - rows: `56876`
   - shared CPU Python reference rows: `56876`, built once and reused by four backends
   - CPU/native-oracle median: `2.1851774686947465`
   - Embree median: `0.13478228449821472`
   - OptiX one-shot median: `0.07310969196259975`
   - prepared OptiX median: `0.07800947688519955`
   - all four backends parity-clean
3. Judge whether the narrow performance interpretation is valid:
   - one-shot OptiX beats Embree by `1.844x` on this exact same-contract row
   - prepared OptiX beats Embree by `1.728x` on this exact same-contract row
   - prepared OptiX is not always faster than one-shot OptiX
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
