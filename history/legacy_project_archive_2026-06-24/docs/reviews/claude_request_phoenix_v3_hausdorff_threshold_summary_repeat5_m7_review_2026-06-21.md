# Claude Review Request - Phoenix V3 Hausdorff Threshold-Summary Repeat=5 M7 Review

Please critically review this Phoenix V3 evidence packet:

`docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_repeat5_rtx_evidence_2026-06-21.md`

and its machine-readable companion:

`docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_repeat5_rtx_evidence_2026-06-21.json`

Review question:

Can the largest Hausdorff threshold-summary row be promoted to a row-scoped M7
V3 claim, while the smaller rows remain blocked?

Candidate wording under review:

```text
RTDL V3 includes a generic Hausdorff threshold-summary route where prepared
OptiX fixed-radius threshold decisions are 1.685x faster in query time and
1.264x faster in phase-total time than the same-contract Embree route at
1,048,576 points per side, threshold 0.4, repeat=5/warmup=1, on an RTX 4000 Ada
pod. Smaller rows in the same rerun are query wins but not phase-total wins.
```

Please return a concise but critical Markdown review with:

1. Verdict: approve, approve with required amendments, or reject.
2. Whether the evidence satisfies row-scoped M7 for the largest row only.
3. Whether the mixed small/mid phase-total rows must block broader wording.
4. Any P0/P1 fixes required before classification packet updates.
5. Exact allowed wording if approval is possible.
6. Exact forbidden wording.

Guardrails:

- Do not approve broad V3-over-V2 claims.
- Do not approve full Hausdorff witness/materialization claims.
- Do not approve X-HD paper reproduction claims.
- Do not approve all-scale Hausdorff claims.
- Require the final claim to stay row-scoped and same-contract.
