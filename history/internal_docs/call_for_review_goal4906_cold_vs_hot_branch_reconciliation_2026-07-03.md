# Call For Review — Goal4906 Cold/Hot Branch Reconciliation

Date: 2026-07-03

## Review Target

Please review:

```text
history/internal_docs/goal4906_cold_vs_hot_branch_reconciliation_2026-07-03.md
```

## Context

Claude approved Goal4896 but raised a decision-critical issue: Goal4896's hot
prepared data contradicts Goal4888's earlier `native_rt_traversal_dominated`
branch conclusion.

Goal4906 is the response. It does not add new implementation. It reconciles the
measurement states and selects the correct immediate optimization branch.

## Requested Verdict Labels

Choose one:

```text
approve_goal4906_reconciliation_and_authorize_goal4907
approve_with_required_amendments
block_branch_decision_still_unreconciled
```

## Questions For Reviewer

1. Does Goal4906 correctly preserve Goal4888 as useful cold/early evidence while rejecting its use as the prepared-hot branch gate?
2. Does the evidence table fairly represent Goal4896 and Goals4901-4905?
3. Is it correct to classify the immediate prepared-hot path as Branch A: materialization / prepare / replay / app-layer continuation?
4. Is it correct that Branch B remains a long-term fusion/native direction, but not the immediate next implementation path?
5. Is Goal4907, structural output-chain construction, the right next engineering target after Goal4905 showed file I/O is only about `0.044s` and chain loops dominate the writer?
6. Does the report avoid overclaiming single-run cold speedup, broad RTDL/RayJoin speedup, or AuthorOfficial overall victory?
7. Does the report keep the "not RayJoin-specific core kernel" boundary intact?
8. If not approved, what exact amendment is required before implementation continues?

## Non-Authorization Reminder

This review must not authorize:

- broad performance claims;
- full Section 5.7 eight-pair performance claims;
- modifying correctness/comparator boundaries;
- adding RayJoin-specific RTDL core kernels;
- treating prepared-hot replay as cold single-run performance;
- resurrecting V3/V4 release claims.
