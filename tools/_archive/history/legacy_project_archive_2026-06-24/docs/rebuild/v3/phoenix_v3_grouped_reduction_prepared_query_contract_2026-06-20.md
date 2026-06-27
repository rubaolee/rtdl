# Phoenix V3 Grouped-Reduction Prepared-Query Contract

Status: prepared-query contract draft, not release authorization.

```text
status: prepared_query_contract_draft_not_release
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promotion_authorized: false
Phoenix M7-qualified release rows: 0
```

## User Problem

Run repeated grouped count/sum queries over a fixed-schema table with known row and group-key counts, without writing custom native code for that application.

This contract exists because the fresh grouped_reduction pod evidence is useful
but not yet user-publishable. A user must be able to tell whether they are
running one query, repeated prepared queries, or a whole database/application
workflow.

## Public Contract Draft

- Scope: prepared repeated grouped reductions over a fixed schema.
- Fixed before prepare: row count, group-key column, number of distinct groups, integer value column for sum, query/filter shape, backend, operation, and group capacity.
- Operations in this packet: `group_count`, `group_sum_i64`.
- Backends in this packet: `embree`, `optix`.
- Partner continuation required: `false`.
- Native app-engine customization allowed: `false`.
- Output contract: one output row per group key must match the CPU reference exactly for count and integer sum on the stated table dimensions.
- Overflow policy: `fail_closed`.

## Timing Contract

- Hot prepared-query field: `elapsed_median_sec`.
- Repeat end-to-end formula:
  `cold_prepare_total_sec + repeat_count * elapsed_median_sec`.
- Repeat scenario values are formula projections: `True`.
- Projection note: Repeat-scenario values are computed from measured cold prepare and the measured hot-query median. They are not independent multi-query end-to-end runs.
- Minimum warmup for M7: `3`.
- Required repeat counts for reporting:
  `[1, 2, 5, 10, 25, 50, 100]`.
- Single-query end-to-end timing, break-even repeat count, and cold/setup cost
  must be shown next to any hot-query speedup.

## Supersession Note

The formula-projected repeat profile below is retained as the contract draft's
derivation record. Current sum-only candidate wording is no longer based on
these modeled repeat100 values. It is superseded by actual repeat100 pod
evidence:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_repeat100_actual_pod_evidence_2026-06-20.md
```

## Candidate Rows

| Row | Mode | Rows | Groups | Hot OptiX/Embree | Repeat 1 end-to-end | Modeled repeat 100 end-to-end | Break-even repeats | Recommended public repeat | Status |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| grouped_reduction_count_repeat100_262144 | count | 262,144 | 1,024 | 9.538x | 0.736x | 2.452x | 14 | None | candidate_needs_public_row_review_not_m7 |
| grouped_reduction_sum_repeat100_262144 | sum | 262,144 | 1,024 | 224.269x | 0.999x | 32.395x | 2 | 100 | candidate_needs_public_row_review_not_m7 |
| grouped_reduction_count_repeat100_524288 | count | 524,288 | 2,048 | 8.819x | 0.683x | 2.633x | 14 | None | candidate_needs_public_row_review_not_m7 |
| grouped_reduction_sum_repeat100_524288 | sum | 524,288 | 2,048 | 180.509x | 1.016x | 33.608x | 1 | 100 | candidate_needs_public_row_review_not_m7 |

## Repeat Profile

These values are formula projections from measured cold prepare and measured
hot-query median. They are not independently measured multi-query loops.

| Row | Repeat 1 | Repeat 2 | Repeat 5 | Repeat 10 | Repeat 25 | Repeat 50 | Repeat 100 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| grouped_reduction_count_repeat100_262144 | 0.736x | 0.758x | 0.821x | 0.926x | 1.224x | 1.678x | 2.452x |
| grouped_reduction_sum_repeat100_262144 | 0.999x | 1.367x | 2.465x | 4.271x | 9.517x | 17.726x | 32.395x |
| grouped_reduction_count_repeat100_524288 | 0.683x | 0.709x | 0.785x | 0.910x | 1.261x | 1.781x | 2.633x |
| grouped_reduction_sum_repeat100_524288 | 1.016x | 1.417x | 2.611x | 4.565x | 10.177x | 18.776x | 33.608x |

## Promotion Gates

- `fresh_pod_artifacts_copied_back`
- `cpu_reference_match_for_every_promoted_backend_row`
- `same_contract_embree_and_optix_rows`
- `warmup_at_least_3_for_every_promoted_row`
- `cold_prepare_total_sec_reported`
- `hot_query_elapsed_median_sec_reported`
- `repeat_1_end_to_end_reported`
- `break_even_repeat_count_reported`
- `chosen_public_repeat_count_named_in_wording`
- `whole_app_speedup_claim_authorized_false`
- `final_external_public_row_review_required`

## Draft Candidate Wording

The following wording is not publishable. It is here so reviewers can decide
whether a prepared repeated-query row is a real user-facing V3 row.

- Draft only: on the RTX 4000 Ada pod, the fixed-schema prepared grouped sum row with 262144 rows and 1024 groups showed 224.269x hot prepared-query OptiX-over-Embree speedup and 32.395x modeled repeat 100 end-to-end speedup after counting cold prepare once (modeled from measured cold prepare plus 100 times the measured hot-query median, not from an independently measured 100-query loop). This wording is not publishable until external public-row review closes.
- Draft only: on the RTX 4000 Ada pod, the fixed-schema prepared grouped sum row with 524288 rows and 2048 groups showed 180.509x hot prepared-query OptiX-over-Embree speedup and 33.608x modeled repeat 100 end-to-end speedup after counting cold prepare once (modeled from measured cold prepare plus 100 times the measured hot-query median, not from an independently measured 100-query loop). This wording is not publishable until external public-row review closes.

## Forbidden Claims

- Do not claim: V3 is 224x faster end to end
- Do not claim: RayDB is 224x faster end to end
- Do not claim: RTDL is a DBMS or SQL engine
- Do not claim: grouped_reduction proves broad V3 speedup over V2.x
- Do not claim: whole-app or whole-database speedup is authorized
- Do not claim: hot prepared-query speedup can be quoted without cold cost and repeat count

## Next Actions

- Seek external review of this contract packet.
- If accepted, choose whether M7 promotes a repeat 100 grouped_sum prepared-query row or keeps grouped_reduction internal.
- If promotion is attempted, write final public row wording and run another review before editing tutorials.

## Goal-Level Decision Audit

Decision: write a public prepared-query contract before any grouped_reduction M7 promotion

1. Was I foolish?

   No. The contract closes the exact blocker found by the fresh evidence review.

2. If yes, what actions made the decision foolish?

   It would be foolish to publish the hot-query speedups without a fixed-schema, cold-cost, and repeat-count user contract.

3. Was there another path?

   Move to another candidate immediately. That remains available, but grouped_reduction is closest to a reusable M7 row.

4. Can I now try a different path that actually solves the problem?

   Make the user contract executable and reviewed before changing public tutorials or wording.
