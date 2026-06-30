# External Review Handoff: Goal4093-4097 RT-DBSCAN Partition Chain

Please perform a read-only independent review of the RTDL Goal4093-4097 chain.

## Scope

Review these reports, artifacts, source changes, and tests:

- `docs/reports/goal4093_partition_summary_non_skip_pair_stream_2026-06-09.md`
- `docs/reports/goal4094_current_route_decision_after_non_skip_partition_stream_2026-06-09.md`
- `docs/reports/goal4095_partition_convergence_phase_breakdown_2026-06-09.md`
- `docs/reports/goal4096_device_partition_key_decode_2026-06-09.md`
- `docs/reports/goal4097_current_route_decision_after_device_key_decode_2026-06-09.md`
- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `src/rtdsl/current_benchmark_route_decisions.py`
- `tests/goal4093_partition_summary_non_skip_pair_stream_test.py`
- `tests/goal4095_partition_convergence_phase_breakdown_test.py`
- `tests/goal4096_device_partition_key_decode_test.py`
- `tests/goal4097_current_route_decision_after_device_key_decode_test.py`

## Questions

1. Are Goal4093 and Goal4096 genuine generic runtime improvements rather than app-specific engine logic?
2. Does Goal4095 correctly identify the remaining bottleneck as a fused/native fixed-radius grouped-union producer problem?
3. Do the pod artifacts support the reported improvements:
   - Goal4093 non-skip stream: 1.5x-2.6x fewer materialized rows with modest build-time improvement;
   - Goal4096 device key decode: 1.18x-1.47x non-skip build speedup over Goal4093;
   - prepared reuse still not default-worthy: clustered 0.849x over five runs, road 0.602x over five runs.
4. Is Goal4097 correct to keep the current RT-DBSCAN route as RTDL/OptiX grouped stream plus Numba continuation rather than promoting `partition_convergence_hybrid`?
5. Are all claim boundaries intact: no release, public speedup, broad RT-core, whole-app, paper-reproduction, hidden-dispatch, automatic partner-selection, app-specific native-engine, native ABI, or true-zero-copy claims?

## Expected Output

Write a review to:

- Claude: `docs/reviews/goal4098_claude_review_goal4093_4097_rtdbscan_partition_chain_2026-06-09.md`
- Gemini: `docs/reviews/goal4099_gemini_review_goal4093_4097_rtdbscan_partition_chain_2026-06-09.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
