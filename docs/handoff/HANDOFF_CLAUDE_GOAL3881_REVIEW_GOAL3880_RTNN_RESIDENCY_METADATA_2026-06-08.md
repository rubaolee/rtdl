# Handoff: Claude Review Goal3880 RTNN Prepared-Session Residency Metadata

Please perform a read-only review of Goal3880, which wires the explicit
prepared-session residency contract into the RTNN benchmark app.

## Files To Inspect

- `examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`
- `docs/reports/goal3880_rtnn_prepared_session_residency_metadata_2026-06-08.md`
- `docs/reports/goal3880_rtnn_prepared_session_residency_a5000/summary.json`
- `docs/reports/goal3880_rtnn_prepared_session_residency_a5000/outputs/rtnn_prepared_optix_scale_default_65536.stdout.json`
- `tests/goal3880_rtnn_prepared_session_residency_metadata_test.py`
- `src/rtdsl/prepared_session_residency.py`

## Review Questions

1. Does the RTNN prepared OptiX payload expose a generic prepared-session cache
   key and policy for its actual arguments without changing the underlying
   runner path or timing behavior?
2. Does the A5000 artifact prove the live app payload includes
   `prepared_session_residency` with `get_or_prepare_explicit_session`,
   `cache_enabled_by_default = false`, and generic primitive
   `fixed_radius_neighbors_3d_ranked_summary`?
3. Are all claim-boundary flags still false, especially automatic
   partner/backend selection and true-zero-copy?
4. Is this a safe first app-level ergonomics step, and what remains before
   learner-facing docs should teach it as a default idiom?

## Validation To Run

If available:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal3880_rtnn_prepared_session_residency_metadata_test tests.goal3877_explicit_prepared_session_reuse_helper_test tests.goal3820_rtnn_prepared_optix_ranked_summary_app_mode_test tests.goal2585_rtnn_benchmark_front_door_test
```

## Required Output

Write the review to:

`docs/reviews/goal3881_claude_review_goal3880_rtnn_residency_metadata_2026-06-08.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`. State explicitly that the review does not
authorize release action, public speedup wording, broad RT-core wording,
true-zero-copy wording, automatic partner/backend selection, or app-specific
native-engine logic.
