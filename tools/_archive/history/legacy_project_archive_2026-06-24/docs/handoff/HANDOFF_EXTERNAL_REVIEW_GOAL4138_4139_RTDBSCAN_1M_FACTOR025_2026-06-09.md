# External Review Request: Goal4138/4139 RT-DBSCAN 1M Factor-0.25 Route Guidance

Date: 2026-06-09

Please perform an independent read-only review of Goals 4138 and 4139.

## Files To Review

- `docs/reports/goal4138_tuned_direct_status_1m_factor025_probe_2026-06-09.md`
- `docs/reports/goal4138_tuned_direct_status_warm_one_shot_1m_factor025_pod.json`
- `docs/reports/goal4139_current_route_decision_after_1m_factor025_probe_2026-06-09.md`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `src/rtdsl/current_benchmark_route_decisions.py`
- `tests/goal4138_tuned_direct_status_1m_factor025_probe_test.py`
- `tests/goal4139_current_route_decision_after_1m_factor025_probe_test.py`

## Context

Goal4138 extends the RT-DBSCAN explicit direct-status route evidence to
1,048,576 points for factor `0.25` only. This is intentionally not a full factor
sweep.

Goal4139 updates the current route decision and advisor evidence after the 1M
probe. The route remains advisory only: users choose the partner, route, and
partition-cell factor explicitly. No automatic dispatch, automatic partner
selection, automatic factor selection, release, public speedup wording, broad
RT-core wording, whole-app benchmark wording, paper-reproduction wording,
app-specific engine logic, native ABI additions, AMD performance claims, or
true-zero-copy claims are authorized.

## Verification Already Run By Codex

Command:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4138_tuned_direct_status_1m_factor025_probe_test tests.goal4139_current_route_decision_after_1m_factor025_probe_test tests.goal4134_tuned_direct_status_524k_factor025_probe_test tests.goal4135_current_route_decision_after_524k_factor025_probe_test tests.goal4130_tuned_direct_status_warm_one_shot_probe_test tests.goal4131_current_route_decision_after_warm_one_shot_probe_test tests.goal4126_tuned_direct_status_262k_scale_probe_test tests.goal4127_current_route_decision_after_262k_direct_status_probe_test tests.goal4121_rt_dbscan_explicit_route_choice_advisor_test tests.goal4123_current_route_decision_after_scale_aware_advisor_test tests.goal3938_current_benchmark_route_decision_registry_test tests.goal4091_current_route_decision_after_partition_summary_host_skip_test tests.goal4094_current_route_decision_after_non_skip_partition_stream_test tests.goal4097_current_route_decision_after_device_key_decode_test tests.goal4101_current_route_decision_after_unordered_non_skip_test tests.goal4106_current_route_decision_after_direct_status_comparison_test tests.goal4110_current_route_decision_after_prepared_direct_status_app_mode_test tests.goal4115_current_route_decision_after_shape_dependent_direct_status_test tests.goal4118_current_route_decision_after_tuned_direct_status_test
```

Result: 62 tests OK.

## Key Facts To Audit

The 1M JSON artifact reports:

- `source_commit`: `c9469d43`
- `source_tracked_worktree_dirty`: `false`
- `point_count`: `1048576`
- `partition_cell_factors`: `[0.25]`
- `repeat`: `2`
- `warmup`: `1`

Reported speedups:

| Profile | Replay speedup | One-shot total speedup |
| --- | ---: | ---: |
| clustered3d | 3.430x | 3.383x |
| road3d | 1.396x | 1.705x |
| ngsim_dense | 1.790x | 2.432x |

All rows should preserve component-size signature parity against the current
grouped-stream route.

## Review Questions

1. Does Goal4138 accurately report the 1M factor-0.25-only pod artifact without
   overclaiming a full factor sweep?
2. Are all reported speedup values arithmetically supported by the JSON artifact?
3. Is the road3d concern from the 524k reviews handled honestly? In particular,
   replay speedup rises from 1.367x at 524k to 1.396x at 1M, while one-shot total
   still declines from 1.910x to 1.705x but remains above parity.
4. Does Goal4139 keep the 65k dense replay-vs-one-shot factor distinction
   visible: factor `0.5` for repeated replay, factor `0.25` for one-shot total?
5. Does the advisor remain explicit/advisory only, with no hidden partner,
   route, or factor selection?
6. Are the claim boundaries intact in the report, JSON, advisor, route registry,
   and tests?
7. Are there any blocking issues before the next RT-DBSCAN engineering step?

## Required Output

Write a review file:

- Claude: `docs/reviews/goal4140_claude_review_goal4138_4139_rtdbscan_1m_factor025_2026-06-09.md`
- Gemini: `docs/reviews/goal4141_gemini_review_goal4138_4139_rtdbscan_1m_factor025_2026-06-09.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Include any findings by severity and state release/claim boundaries
explicitly.
