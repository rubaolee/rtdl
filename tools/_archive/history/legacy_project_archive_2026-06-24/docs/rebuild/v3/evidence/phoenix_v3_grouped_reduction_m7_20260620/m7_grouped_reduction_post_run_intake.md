# Phoenix V3 Grouped-Reduction M7 Post-Run Intake

Status: fresh M7 rerun intake, not M7 promotion.

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

Both source evidence files used warmup=3. Cross-scale rows still remain post-run intake evidence until external review.
The workload-build fields below record both Embree and OptiX paths; the cheapest path can hide that the other baseline still pays a large cold/setup cost.

| Scale | Source warmup | Mode | Embree workload build | OptiX workload build |
| --- | ---: | --- | ---: | ---: |
| `262144` | 3 | `count` | 0.111s | 0.102s |
| `262144` | 3 | `sum` | 1.809s | 1.724s |
| `524288` | 3 | `count` | 0.199s | 0.197s |
| `524288` | 3 | `sum` | 3.512s | 3.465s |

## Repeat-Aware Summary

| Scale | Mode | Hot OptiX/Embree | Break-even repeats | Repeat 1 end-to-end | Repeat 100 end-to-end | Main blocker |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `262144` | `count` | 9.538x | 14 | 0.736x | 2.452x | `single_query_end_to_end_not_optix_win` |
| `262144` | `sum` | 224.269x | 2 | 0.999x | 32.395x | `single_query_end_to_end_not_optix_win` |
| `524288` | `count` | 8.819x | 14 | 0.683x | 2.633x | `single_query_end_to_end_not_optix_win` |
| `524288` | `sum` | 180.509x | 1 | 1.016x | 33.608x | `prepared_query_contract_not_yet_public_tutorial` |

## Boundary

Internal evidence shows the generic prepared grouped-reduction primitive can be much faster than Embree in the hot prepared-query window, especially for repeated queries or sum mode.

Do not claim the fresh grouped_reduction hot-query ratios, up to 224.269x, are end-to-end speedups; do not claim whole-database speedup; and do not hide cold/setup cost behind hot-query ratios.

## M7 Blockers

- `prepared_query_contract_not_yet_public_tutorial`
- `repeat_count_and_amortization_policy_not_reviewed`
- `cold_setup_costs_must_be_reported_next_to_hot_speedups`
- `no_public_row_level_external_review_for_promoted_wording`
- `fresh_rerun_requires_external_review_before_m7_promotion`

## Goal-Level Decision Audit

Decision: classify fresh grouped_reduction M7 rerun evidence without promoting it

1. Was I foolish?

   No. The packet tests whether the strongest reusable evidence can become a user-responsible row.

2. If yes, what actions made the decision foolish?

   It would be foolish to promote the fresh 224.269x hot-query ratio without cold/setup cost and repeat-count context.

3. Was there another path?

   Start with Triangle or docs. That remains possible, but grouped_reduction is the cleanest reusable engine candidate.

4. Can I now try a different path that actually solves the problem?

   Compute repeat-aware end-to-end scenarios and keep M7 promotion false unless the public contract is closed.
