# External Review Handoff: Goal4164 RT-DBSCAN All-Predicate-Only Mode

Please perform a read-only independent review of Goal4164.

## Scope

Review the two Goal4164 commits:

- `d25eff11` - `Goal4164 add RTDBSCAN all-predicate-only mode`
- `73a6cb4e` - `Goal4164 add all-predicate pod evidence`

Primary files:

- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `docs/reports/goal4164_rt_dbscan_all_predicate_only_mode_2026-06-09.md`
- `docs/reports/goal4164_all_predicate_only_mode_pod.json`
- `tests/goal4164_rt_dbscan_all_predicate_only_mode_test.py`

Context files:

- `docs/reports/goal4158_predicate_all_true_fast_path_pod_result_2026-06-09.md`
- `docs/reports/goal4159_mixed_predicate_direct_status_gap_2026-06-09.md`
- `docs/reviews/goal4160_claude_review_goal4155_4159_rtdbscan_predicate_direct_status_2026-06-09.md`
- `docs/reviews/goal4160_gemini_review_goal4155_4159_rtdbscan_predicate_direct_status_2026-06-09.md`
- `docs/reports/goal4162_predicate_border_assignment_policy_metadata_2026-06-09.md`
- `docs/reports/goal4163_rt_dbscan_route_advisor_after_predicate_gap_2026-06-09.md`

## Questions

1. Does Goal4164 expose the Goal4158 all-predicate fast path as an explicit user-selected mode without hidden dispatch?
2. Does the mode fail closed for mixed predicate rows, with a clear fallback to `optix_rt_core_grouped_stream_numba_column_signature_3d`?
3. Does the pod artifact prove both branches on `NVIDIA RTX 4000 Ada Generation, 550.127.05` at commit `d25eff118d8590068c5aa0ead9c557240ae3a06c`?
4. Does the implementation keep the native engine/app boundary intact and avoid adding DBSCAN-specific native ABI or semantics?
5. Does the report avoid overclaiming release readiness, broad RT-core speedup, route promotion, or whole-app speedup?

## Expected Output

Write one review file:

- Claude: `docs/reviews/goal4165_claude_review_goal4164_rtdbscan_all_predicate_only_2026-06-09.md`
- Gemini: `docs/reviews/goal4165_gemini_review_goal4164_rtdbscan_all_predicate_only_2026-06-09.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

This is a review request only. Do not edit source code.
