# External Review Handoff: Goals4065-4067 RT-DBSCAN Partition Preview Chain

Date: 2026-06-09

Please perform an independent read-only review of the Goal4065-4067 chain on
current `main`.

## Scope

Review these deliverables:

- `docs/reports/goal4065_rt_dbscan_prepared_partition_signature_app_mode_2026-06-09.md`
- `docs/reports/goal4065_rt_dbscan_prepared_partition_signature_app_mode_pod_smoke.json`
- `docs/reports/goal4066_partition_pair_count_then_emit_preview_2026-06-09.md`
- `docs/reports/goal4066_pair_count_then_emit_timing_pod.json`
- `docs/reports/goal4067_rt_dbscan_partition_pair_enumeration_option_2026-06-09.md`
- `docs/reports/goal4067_rt_dbscan_partition_pair_enumeration_option_pod_smoke.json`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/README.md`
- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `tests/goal4065_rt_dbscan_prepared_partition_signature_app_mode_test.py`
- `tests/goal4066_partition_pair_count_then_emit_preview_test.py`
- `tests/goal4067_rt_dbscan_partition_pair_enumeration_option_test.py`

## Questions

1. Do Goals4065-4067 preserve the app-agnostic native-engine boundary? In
   particular, confirm that the new functionality is generic fixed-radius
   graph/partition/pair enumeration logic and does not introduce DBSCAN-specific
   native ABI or native engine behavior.
2. Is the RT-DBSCAN app integration honest? It should expose explicit
   benchmark-app modes and a user-selected `--partition-pair-enumeration`
   option, not hidden dispatch or automatic partner choice.
3. Does Goal4066 correctly frame `device_count_then_emit` as a memory-pressure
   improvement with near-parity timing, not a broad speedup claim?
4. Does Goal4067 correctly preserve existing defaults through `mode_default`
   while allowing explicit `device_count_then_emit` selection?
5. Are all claim boundaries closed: no release authorization, no public speedup
   wording, no broad RT-core claim, no whole-app claim, no true-zero-copy claim,
   no default-route promotion?
6. What must happen before this partition-preview lane can become a promoted
   v2.x route?

## Expected Output

Write exactly one review file:

- Claude: `docs/reviews/goal4068_claude_review_goal4065_4067_rt_dbscan_partition_preview_2026-06-09.md`
- Gemini: `docs/reviews/goal4069_gemini_review_goal4065_4067_rt_dbscan_partition_preview_2026-06-09.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

This review must be independent from Codex authoring. Codex+Codex is invalid
consensus.
