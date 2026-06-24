# Phoenix V3 Grouped-Reduction M7 Feasibility

Status: feasibility packet, not M7 promotion.

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
M7-qualified release rows: 0
```

## Verdict

Grouped reduction is the strongest current reusable V3 performance candidate, but it is not promoted to M7 here.
The reason is precise: hot prepared-query wins are real, while cold/setup and repeat-count policy are not yet a public contract.

## Source Evidence And Warmups

Source evidence files used different warmups: 262144 rows used warmup=1, 524288 rows used warmup=2. Cross-scale rows are therefore feasibility inputs, not standardized scale-ladder timing.
The workload-build fields below record both Embree and OptiX paths; the cheapest path can hide that the other baseline still pays a large cold/setup cost.

| Scale | Source warmup | Mode | Embree workload build | OptiX workload build |
| --- | ---: | --- | ---: | ---: |
| `262144` | 1 | `count` | 6.553s | 0.100s |
| `262144` | 1 | `sum` | 105.158s | 64.077s |
| `524288` | 2 | `count` | 0.199s | 0.197s |
| `524288` | 2 | `sum` | 217.964s | 213.265s |

## Repeat-Aware Summary

| Scale | Mode | Hot OptiX/Embree | Break-even repeats | Repeat 1 end-to-end | Repeat 100 end-to-end | Main blocker |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `262144` | `count` | 9.864x | 1 | 18.081x | 16.458x | `prepared_query_contract_not_yet_public_tutorial` |
| `262144` | `sum` | 202.774x | 1 | 1.625x | 3.115x | `large_sum_workload_build_cost_must_be_prominent` |
| `524288` | `count` | 8.752x | 18 | 0.592x | 2.579x | `single_query_end_to_end_not_optix_win` |
| `524288` | `sum` | 158.010x | 1 | 1.020x | 1.973x | `large_sum_workload_build_cost_must_be_prominent` |

## Boundary

Internal evidence shows the generic prepared grouped-reduction primitive can be much faster than Embree in the hot prepared-query window, especially for repeated queries or sum mode.

Do not claim RayDB-style V3 is 158x faster end to end, do not claim whole-database speedup, and do not hide cold/setup cost behind hot-query ratios.

## M7 Blockers

- `prepared_query_contract_not_yet_public_tutorial`
- `repeat_count_and_amortization_policy_not_reviewed`
- `cold_setup_costs_must_be_reported_next_to_hot_speedups`
- `no_fresh_m7_pod_rerun_after_feasibility_packet`
- `no_public_row_level_external_review_for_promoted_wording`

## Goal-Level Decision Audit

Decision: attempt grouped_reduction M7 feasibility through repeat-aware amortization instead of quoting hot ratios

1. Was I foolish?

   No. The packet tests whether the strongest reusable evidence can become a user-responsible row.

2. If yes, what actions made the decision foolish?

   It would be foolish to promote the 158x sum hot-query ratio without cold/setup cost and repeat-count context.

3. Was there another path?

   Start with Triangle or docs. That remains possible, but grouped_reduction is the cleanest reusable engine candidate.

4. Can I now try a different path that actually solves the problem?

   Compute repeat-aware end-to-end scenarios and keep M7 promotion false unless the public contract is closed.
