# External Review Request: Goals4085-4088 Partition Summary Chain

Date: 2026-06-09

Please perform a read-only review of the RT-DBSCAN fixed-radius grouped-union
partition-summary chain:

- Goal4085: `docs/reports/goal4085_partition_summary_build_feasibility_2026-06-09.md`
- Goal4086: `docs/reports/goal4086_grouped_union_native_api_feasibility_after_partition_probe_2026-06-09.md`
- Goal4087: `docs/reports/goal4087_prepared_partition_summary_reuse_threshold_2026-06-09.md`
- Goal4088: `docs/reports/goal4088_device_partition_summary_host_aabb_skip_2026-06-09.md`

Also inspect:

- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `scripts/goal4085_partition_summary_build_feasibility.py`
- `scripts/goal4087_prepared_partition_summary_reuse_threshold.py`
- `tests/goal4085_partition_summary_build_feasibility_test.py`
- `tests/goal4086_grouped_union_native_api_feasibility_after_partition_probe_test.py`
- `tests/goal4087_prepared_partition_summary_reuse_threshold_test.py`
- `tests/goal4088_device_partition_summary_host_aabb_skip_test.py`

## Questions

1. Does Goal4088 preserve the app-agnostic runtime boundary while removing only
   unused host work for device-backed partition enumeration?
2. Do the pod artifacts justify the claim that build time improved 1.6x-2.3x
   without changing pair/status counts?
3. Is the default-route policy correct: keep the current RTDL/OptiX grouped
   stream plus Numba route, and keep partition convergence explicit/unpromoted?
4. Does Goal4087 correctly bound prepared reuse as a repeated-run niche rather
   than a default route?
5. Is the next engineering direction correct: cheaper native/device producer or
   fused safe-full/ambiguous work stream, not more wrapper tuning?

## Output Paths

Claude review path:

`docs/reviews/goal4089_claude_review_goal4085_4088_partition_summary_chain_2026-06-09.md`

Gemini review path:

`docs/reviews/goal4090_gemini_review_goal4085_4088_partition_summary_chain_2026-06-09.md`

Use one of these verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Do not mutate source files. If you run tests, record the command and result in
the review. Do not authorize release, public speedup, broad RT-core,
whole-app acceleration, true-zero-copy, automatic partner selection, hidden
dispatch, or app-specific native-engine logic.
