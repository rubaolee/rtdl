# Handoff: Goal3325 Gemini Review Of RayJoin Boundary And Candidate Primitive

Date: 2026-06-04
Repo: `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`
Branch: `main`
Expected output: `docs/reviews/goal3325_gemini_review_rayjoin_boundary_candidate_2026-06-04.md`

## Task

Please perform an independent Gemini review of the RayJoin PIP boundary chain and the newly added candidate primitive:

- Goal3320: broader CDB validation boundary.
- Goal3321: app-level validated-domain preflight.
- Goal3322: per-point mismatch diagnosis.
- Goal3324: `candidate.closed_shape_topology_membership_count_2d` in the primitive hierarchy and generated catalog.

## Files To Inspect

- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `src/rtdsl/primitive_hierarchy.py`
- `src/rtdsl/primitive_discovery.py`
- `docs/rtdl_primitive_catalog.md`
- `docs/reports/goal3320_rayjoin_pip_full_dataset_validation_boundary_2026-06-04.md`
- `docs/reports/goal3320_rayjoin_pip_device_count_validation_matrix_2026-06-04.json`
- `docs/reports/goal3321_rayjoin_pip_validated_domain_preflight_2026-06-04.md`
- `docs/reports/goal3321_rayjoin_pip_preflight_pod_smoke_2026-06-04.json`
- `docs/reports/goal3322_rayjoin_pip_per_point_mismatch_diagnosis_2026-06-04.md`
- `docs/reports/goal3322_rayjoin_pip_per_point_mismatch_diagnosis_2026-06-04.json`
- `docs/reports/goal3324_closed_shape_topology_membership_candidate_2026-06-04.md`
- `tests/goal3320_rayjoin_pip_validation_boundary_test.py`
- `tests/goal3321_rayjoin_pip_validated_domain_preflight_test.py`
- `tests/goal3322_rayjoin_pip_per_point_mismatch_diagnosis_test.py`
- `tests/goal3324_closed_shape_topology_membership_candidate_test.py`

## Review Questions

1. Are the validation artifacts internally consistent and correctly interpreted?
2. Does the preflight API make the fast path fail closed without becoming hidden dispatcher magic?
3. Does the mismatch diagnosis support a topology/boundary/duplicate-policy design hypothesis?
4. Does the candidate primitive remain app-agnostic and duplicate-gated?
5. Are the generated catalog and tests aligned with the hierarchy source of truth?
6. Are all release, public speedup, RTDL-beats-RayJoin, RayJoin reproduction, broad RT-core, and true-zero-copy claims still blocked?

## Required Output

Write a Markdown review at:

`docs/reviews/goal3325_gemini_review_rayjoin_boundary_candidate_2026-06-04.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Do not authorize release, public speedup claims, RayJoin paper reproduction claims, RTDL-beats-RayJoin claims, broad RT-core speedup claims, true-zero-copy claims, or app-specific native-engine direction.

