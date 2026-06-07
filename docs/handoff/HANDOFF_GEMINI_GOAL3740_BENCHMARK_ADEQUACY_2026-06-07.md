# Handoff: Gemini Review Goal3740 Benchmark-App Adequacy

Please perform an independent Gemini review of Goal3740.

## Scope

Review:

- `src/rtdsl/v2_9_benchmark_adequacy.py`
- `docs/reports/goal3740_benchmark_app_adequacy_after_goal3737_2026-06-07.md`
- `tests/goal3740_benchmark_app_adequacy_after_goal3737_test.py`
- Recent RayJoin evidence:
  - `docs/reports/goal3737_shape_pair_active_count_executor_and_rayjoin_perf_2026-06-07.md`
  - `docs/reports/goal3737_rayjoin_safe_mixed_executor_cross_size_a5000/summary.json`
- Context packet:
  - `docs/reports/goal3567_v2_9_composite_packet_after_raydb_sum_fastpath_2026-06-06.md`
  - `docs/reports/goal3602_v2_9_benchmark_status_after_resident_evidence_2026-06-06.md`

## Questions

1. Does Goal3740 cover all 10 promoted benchmark apps without hiding weak rows?
2. Is the adequacy classification fair after Goal3737, especially:
   - RayJoin as strong but contract-specific,
   - Barnes-Hut as the only `needs_major_followup`,
   - RT-DBSCAN and robot collision as near-parity rather than headline wins?
3. Are the Numba-reference pressure points correct: `spatial_rayjoin`, `rt_dbscan`, and `barnes_hut`?
4. Does the AMD HIPRT preparation scope start from generic primitive mapping rather than app-shaped ports?
5. Does the report avoid release, public speedup, broad RT-core, RayJoin paper-reproduction, true-zero-copy, automatic partner selection, or app-specific native-engine claims?
6. What should be the next engineering step after Goal3740?

## Validation To Run

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3740_benchmark_app_adequacy_after_goal3737_test tests.goal3737_shape_pair_active_count_executor_test
```

## Required Output

Write the review to:

`docs/reviews/goal3741_gemini_review_goal3740_benchmark_app_adequacy_2026-06-07.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
