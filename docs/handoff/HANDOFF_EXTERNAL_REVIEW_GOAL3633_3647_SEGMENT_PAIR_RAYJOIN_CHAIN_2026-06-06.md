# Handoff: External Review for Goals 3633-3647 Segment-Pair / RayJoin Prepared-Left Chain

Date: 2026-06-06

Please review the Goal3633-Goal3647 chain on current `main` at or after commit
`e60c8040`.

## Requested Output

Write one review document:

- Gemini:
  `docs/reviews/goal3648_gemini_review_segment_pair_rayjoin_prepared_left_chain_3633_3647_2026-06-06.md`
- Claude, if available later:
  `docs/reviews/goal3649_claude_review_segment_pair_rayjoin_prepared_left_chain_3633_3647_2026-06-06.md`

Use verdicts only from:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

## Scope To Review

Source commits:

- `4a537484` Goal3633 expose grouped count status pointers
- `11b9721c` Goal3633 record segment pair status residency evidence
- `381b5d99` Goal3635 record segment pair large grid stress
- `1eeff46c` Goal3637 add optional segment ambiguity status route
- `e6e961d0` Goal3637 record optional ambiguity status evidence
- `89bae35b` Goal3639 add sparse segment pair stress cases
- `89efb63a` Goal3639 record sparse segment pair diagnostic
- `8a71e5f2` Goal3641 cap segment pair runner count vectors
- `c4a1a3e0` Goal3643 add prepacked left segment timing mode
- `d89b92ee` Goal3643 record prepacked left segment sparse diagnostic
- `1276d8d6` Goal3645 add prepared segment left-set count route
- `6e061d83` Goal3645 record prepared left-set sparse route evidence
- `0d27bdab` Goal3646 record prepared left-set amortized sparse probe
- `fd7abe1d` Goal3647 route RayJoin LSI dense count through prepared left set
- `e60c8040` Goal3647 record RayJoin LSI prepared-left route evidence

Primary files:

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal3631_segment_pair_backend_conformance_runner.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`

Primary reports/artifacts:

- `docs/reports/goal3633_segment_pair_status_device_columns_2026-06-06.md`
- `docs/reports/goal3635_segment_pair_status_large_grid_stress_2026-06-06.md`
- `docs/reports/goal3637_segment_pair_optional_ambiguity_status_2026-06-06.md`
- `docs/reports/goal3639_segment_pair_sparse_grid_rt_index_diagnostic_2026-06-06.md`
- `docs/reports/goal3643_segment_pair_prepacked_left_sparse_diagnostic_2026-06-06.md`
- `docs/reports/goal3645_prepared_segment_left_set_sparse_count_route_2026-06-06.md`
- `docs/reports/goal3646_prepared_segment_left_set_amortized_sparse_probe_2026-06-06.md`
- `docs/reports/goal3647_rayjoin_lsi_prepared_left_route_adoption_2026-06-06.md`

Tests:

- `tests.goal3631_segment_pair_backend_conformance_a5000_test`
- `tests.goal3633_segment_pair_status_device_columns_test`
- `tests.goal3635_segment_pair_status_large_grid_stress_test`
- `tests.goal3637_segment_pair_optional_ambiguity_status_test`
- `tests.goal3639_segment_pair_sparse_grid_rt_index_diagnostic_test`
- `tests.goal3641_segment_pair_runner_count_vector_cap_test`
- `tests.goal3643_segment_pair_prepacked_left_sparse_diagnostic_test`
- `tests.goal3645_prepared_segment_left_set_sparse_count_route_test`
- `tests.goal3646_prepared_segment_left_set_amortized_sparse_probe_test`
- `tests.goal3647_rayjoin_lsi_prepared_left_route_adoption_test`

Recommended validation command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3647_rayjoin_lsi_prepared_left_route_adoption_test tests.goal3646_prepared_segment_left_set_amortized_sparse_probe_test tests.goal3645_prepared_segment_left_set_sparse_count_route_test tests.goal3643_segment_pair_prepacked_left_sparse_diagnostic_test tests.goal3641_segment_pair_runner_count_vector_cap_test tests.goal3639_segment_pair_sparse_grid_rt_index_diagnostic_test tests.goal3637_segment_pair_optional_ambiguity_status_test tests.goal3635_segment_pair_status_large_grid_stress_test tests.goal3633_segment_pair_status_device_columns_test tests.goal3631_segment_pair_backend_conformance_a5000_test
```

## Questions To Answer

1. Does the new native prepared-left segment-set ABI remain app-agnostic, or does it leak RayJoin-specific behavior into the engine?
2. Does the Python wrapper manage native prepared-left lifetime safely enough for the current evidence packet?
3. Do Goal3645 and Goal3646 correctly distinguish hot-route/repeated-call evidence from one-shot app-wall timing?
4. Is the Goal3647 same-slice LSI comparison honestly scoped as a matching visible count contract, not a full RayJoin reproduction?
5. Are all release, broad speedup, true zero-copy, RT-core, whole-app, and paper-reproduction claims still blocked?
6. What should the next engineering target be: larger RayJoin same-slice scaling, prepared-left route integration into more benchmark packets, or another generic device-resident primitive?

## Expected Boundary

The intended verdict is likely `accept-with-boundary` if the implementation and
artifacts are sound. Do not authorize release readiness or public claims from
this review alone.
