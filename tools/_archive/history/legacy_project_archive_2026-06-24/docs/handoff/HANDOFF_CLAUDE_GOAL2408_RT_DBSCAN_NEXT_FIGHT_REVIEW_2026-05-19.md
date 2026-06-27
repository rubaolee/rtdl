# Claude Handoff: Goal2408 RT-DBSCAN Next-Fight Review

Date: 2026-05-19

Please act as an independent external reviewer for the next RT-DBSCAN benchmark
fight. Codex has written a plan, but the next implementation should not start
until you challenge it.

## Read First

- `docs/reports/goal2405_rt_dbscan_rt_count_threshold_device_columns_2026-05-19.md`
- `docs/reports/goal2407_rt_dbscan_rt_core_graph_union_negative_result_2026-05-19.md`
- `docs/reports/goal2408_codex_rt_dbscan_next_fight_plan_2026-05-19.md`
- `docs/research/future_version_to_do_list.md`
- `src/rtdsl/partner_adapters.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`

## Review Questions

1. Do you accept Codex's conclusion that Goal2407 should remain a negative
   result and that raw OptiX any-hit atomic union should not be promoted?
2. Is Candidate B, the generic fixed-radius cell-graph all-core continuation,
   actually the best next implementation target?
3. What exact correctness risks must be guarded if point-level connectivity is
   summarized through cell-level components?
4. Should the next fight instead be prepared CuPy grid continuation, compact RT
   edge stream plus partner union, or another generic primitive?
5. Does the proposed direction preserve the app-agnostic RTDL engine boundary,
   with no DBSCAN-native ABI or hard-coded cluster expansion?
6. What pod evidence would be enough to decide whether Goal2409 succeeded or
   failed?

## Output

Write your review to:

`docs/reviews/goal2409_claude_review_goal2408_rt_dbscan_next_fight_plan_2026-05-19.md`

Use one of these verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please include a concise recommendation for the next implementation target.
If you disagree with Codex, say so plainly and propose the better fight.

## Boundary

The RTDL native engine must remain app-agnostic. Do not recommend adding a
DBSCAN-shaped native ABI, DBSCAN-specific OptiX continuation, or release/perf
claim expansion before pod evidence exists.
