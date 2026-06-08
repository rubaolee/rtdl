# Handoff: Claude Review for Goal3853 Barnes-Hut Numba Force-Summary Timing

Please perform an independent read-only review of Goal3853 on current `main`.

## Scope

Review:

- `examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py`
- `examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
- `docs/reports/goal3853_barnes_hut_numba_force_summary_2026-06-08.md`
- `docs/reports/goal3853_barnes_hut_numba_force_summary_a5000/`
- `tests/goal3853_barnes_hut_numba_force_summary_test.py`

## Required Output

Write the review to:

`docs/reviews/goal3854_claude_review_goal3853_barnes_hut_numba_force_summary_2026-06-08.md`

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Questions

1. Does Goal3853 correctly preserve the app-agnostic native-engine boundary?
2. Does the force-summary path honestly avoid Python force-row dictionaries while still producing the documented checksum summary?
3. Is the `median_force_kernel_sec ~= 0.009s` evidence supported by the A5000 artifacts?
4. Does the report correctly state that process time remains startup/JIT dominated and avoid overclaiming a cold-process speedup?
5. Does forwarding `query_repeat` / `warmup` into `partner_exact_force` preserve prior behavior for non-summary or validation-inclusive modes?
6. Are there required-before-next-step fixes?

## Validation

At minimum:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest tests.goal3853_barnes_hut_numba_force_summary_test tests.goal3828_current_benchmark_scale_profile_registry_test
```

Do not edit source files.

