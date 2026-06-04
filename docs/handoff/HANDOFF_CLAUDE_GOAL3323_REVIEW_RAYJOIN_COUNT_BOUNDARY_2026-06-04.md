# Handoff: Goal3323 Claude Review Of RayJoin PIP Count Boundary Chain

Date: 2026-06-04
Repo: `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`
Branch: `main`
Expected output: `docs/reviews/goal3323_claude_review_rayjoin_pip_count_boundary_chain_2026-06-04.md`

## Task

Please perform an independent Claude review of the recent RayJoin PIP count chain:

- Goal3318: reusable prepared point / closed-shape scalar-count batch executor.
- Goal3320: full/slice CDB validation boundary.
- Goal3321: app-level validated-domain preflight.
- Goal3322: per-point mismatch diagnosis.

Claude may also inspect Goal3314/3316/3317 if needed for stream-policy context.

## Files To Inspect

- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/rtdsl/optix_runtime.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `scripts/goal3310_rayjoin_pip_batch_scalar_count_probe.py`
- `tests/goal3318_prepared_point_batch_executor_surface_test.py`
- `tests/goal3320_rayjoin_pip_validation_boundary_test.py`
- `tests/goal3321_rayjoin_pip_validated_domain_preflight_test.py`
- `tests/goal3322_rayjoin_pip_per_point_mismatch_diagnosis_test.py`
- `docs/reports/goal3318_prepared_point_batch_executor_2026-06-04.md`
- `docs/reports/goal3320_rayjoin_pip_full_dataset_validation_boundary_2026-06-04.md`
- `docs/reports/goal3320_rayjoin_pip_device_count_validation_matrix_2026-06-04.json`
- `docs/reports/goal3321_rayjoin_pip_validated_domain_preflight_2026-06-04.md`
- `docs/reports/goal3321_rayjoin_pip_preflight_pod_smoke_2026-06-04.json`
- `docs/reports/goal3322_rayjoin_pip_per_point_mismatch_diagnosis_2026-06-04.md`
- `docs/reports/goal3322_rayjoin_pip_per_point_mismatch_diagnosis_2026-06-04.json`
- `docs/research/future_version_to_do_list.md`

## Review Questions

1. Does the Goal3318 executor remain generic and app-agnostic, with no RayJoin-specific native logic?
2. Does Goal3320 correctly interpret the broader CDB validation results: soil slice exact, county full/start256 mismatching?
3. Does Goal3321 make the validation boundary operational without hiding dispatch magic or moving CDB policy into the native engine?
4. Does Goal3322 support the conclusion that the mismatch is a structured overcount/topology/degeneracy boundary rather than random timing or launch instability?
5. Is the proposed next direction correct: a generic face/topology-aware closed-shape membership/count primitive with explicit boundary ownership and duplicate policy, not another RayJoin-specific native function?
6. Are all public claim boundaries still false and sufficiently visible?

## Required Output

Write a Markdown review at:

`docs/reviews/goal3323_claude_review_rayjoin_pip_count_boundary_chain_2026-06-04.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Lead with findings by severity. If there are no blockers, say so explicitly. Do not authorize release, public speedup claims, RayJoin paper reproduction claims, RTDL-beats-RayJoin claims, broad RT-core speedup claims, true-zero-copy claims, or app-specific native-engine direction.

