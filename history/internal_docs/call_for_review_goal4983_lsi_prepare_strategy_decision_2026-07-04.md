# Call For Review: Goal4983 LSI Prepare/Warm Strategy Decision

Date: 2026-07-04

Please review:

```text
history/internal_docs/goal4983_lsi_prepare_strategy_decision_2026-07-04.md
```

## Context

Goal4982 proved that:

- grouped carrier warm-state cost is about `0.10-0.11s`;
- LSI producer remains about `2.69-2.76s` in repeated full-route runs;
- the `0.000000s` LSI repeat diagnostic is not valid timing evidence.

Goal4983 decides how v2.14.3 should treat LSI prepare/warm costs in product claims and final performance matrices.

## Requested Verdict Label

```text
approve_goal4983_keep_lsi_in_fresh_headline_no_warm_only_claim
```

or, if the decision is too conservative or unsupported:

```text
fail_redo_goal4983_lsi_prepare_strategy_not_proven
```

## Review Questions

1. Is it correct that v2.14.3 must keep the `~2.7s` LSI producer cost in the fresh writer-free binary operator headline?

2. Is the report correct to reject the `0.000000s` LSI repeat diagnostic as evidence for a product warm route?

3. Is it correct to allow prepare-once/query-many only as a future or explicitly measured product route, not as the primary v2.14.3 headline?

4. Does the decision prevent the earlier mistake of comparing an amortized/replay RTDL number against an author's fresh overlay computation?

5. Does the report correctly authorize the next gate: correctness/regression plus non-RayJoin genericity before final matrix?

6. Should Goal4983 close with:

```text
warmup_not_product_strategy_keep_fresh_lsi_headline
```
