# External Review Handoff: Goal4100-4101 RT-DBSCAN Unordered Partition Stream

Please perform a read-only independent review of the RTDL Goal4100-4101 chain.

## Scope

Review these reports, artifacts, source changes, and tests:

- `docs/reports/goal4100_unordered_non_skip_partition_stream_2026-06-09.md`
- `docs/reports/goal4100_unordered_non_skip_build_pod.json`
- `docs/reports/goal4100_unordered_non_skip_reuse_pod.json`
- `docs/reports/goal4100_unordered_non_skip_phase_pod.json`
- `docs/reports/goal4101_current_route_decision_after_unordered_non_skip_2026-06-09.md`
- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `src/rtdsl/current_benchmark_route_decisions.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `tests/goal4100_unordered_non_skip_partition_stream_test.py`
- `tests/goal4101_current_route_decision_after_unordered_non_skip_test.py`

You may also reference the immediate predecessor evidence:

- `docs/reports/goal4096_device_partition_key_decode_2026-06-09.md`
- `docs/reports/goal4096_partition_summary_build_after_device_key_decode_pod.json`
- `docs/reports/goal4096_partition_reuse_after_device_key_decode_pod.json`
- `docs/reports/goal4096_device_partition_key_decode_phase_breakdown_pod.json`

## Questions

1. Is Goal4100 a genuine generic runtime/contract improvement rather than app-specific engine logic?
2. Is the new `device_count_then_emit_non_skip_unordered` contract correctly separated from the sorted `device_count_then_emit_non_skip` stream via `pair_order = device_atomic_append_unordered`?
3. Do the pod artifacts support the reported localized improvements:
   - build medians improve by 1.13x-1.17x over Goal4096 sorted non-skip;
   - emit medians improve by 1.38x-2.32x;
   - prepared reuse still remains below the current recommended route, with clustered at 0.851x over five runs and road at 0.605x?
4. Is Goal4101 correct to keep the current RT-DBSCAN route as RTDL/OptiX grouped stream plus Numba continuation instead of promoting `partition_convergence_hybrid`?
5. Are all claim boundaries intact: no release, public speedup, broad RT-core, whole-app, paper-reproduction, hidden-dispatch, automatic partner-selection, app-specific native-engine, native ABI, or true-zero-copy claims?
6. Is the stated next engineering target correct: a fused/native fixed-radius grouped-union primitive that avoids the double pass and full partition-pair materialization?

## Expected Output

Print a Markdown review only. Do not edit files directly.

Save/capture the output as:

- Claude: `docs/reviews/goal4102_claude_review_goal4100_4101_rtdbscan_unordered_stream_2026-06-09.md`
- Gemini: `docs/reviews/goal4103_gemini_review_goal4100_4101_rtdbscan_unordered_stream_2026-06-09.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
