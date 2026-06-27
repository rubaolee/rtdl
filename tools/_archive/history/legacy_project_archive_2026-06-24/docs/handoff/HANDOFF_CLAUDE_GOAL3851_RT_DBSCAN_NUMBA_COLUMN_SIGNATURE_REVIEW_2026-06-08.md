# Handoff: Claude Review for Goal3851 RT-DBSCAN Numba Column-Signature Route

Please perform an independent read-only review of Goal3851 on current `main`.

## Scope

Review the Goal3851 implementation and evidence:

- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/README.md`
- `src/rtdsl/current_benchmark_scale_profiles.py`
- `docs/reports/goal3851_rt_dbscan_numba_column_signature_2026-06-08.md`
- `docs/reports/goal3851_rt_dbscan_numba_column_signature_a5000/`
- `tests/goal3851_rt_dbscan_numba_column_signature_test.py`

## Required Review Output

Write the review to:

`docs/reviews/goal3852_claude_review_goal3851_rt_dbscan_numba_column_signature_2026-06-08.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Questions To Answer

1. Does the new `optix_rt_core_flags_numba_prepared_grid_column_signature_3d` mode preserve the app-agnostic native-engine boundary?
2. Does Goal3851 correctly distinguish prepared steady-state payload timing from cold command-line process time?
3. Is the `8.56x` delta against Goal3850 supported by the committed A5000 artifacts, and is it scoped narrowly enough?
4. Does the updated current scale-profile row remain claim-boundary-clean and fail-closed?
5. Does the report avoid overclaiming RT-core, paper-reproduction, whole-app, release, or zero-copy claims?
6. Are there any required-before-next-step fixes, especially around Numba JIT/startup cost, signature correctness, or repeat/warmup semantics?

## Validation To Run

At minimum:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal3851_rt_dbscan_numba_column_signature_test tests.goal3828_current_benchmark_scale_profile_registry_test tests.goal3742_rt_dbscan_numba_grid_reference_test
```

Do not edit source files. This is a read-only review.

