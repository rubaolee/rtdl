# Claude Review Request - Phoenix V3 Hausdorff Threshold-Summary P0 Repair Final Review

Please critically review the repaired Phoenix V3 Hausdorff evidence packet:

`docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_repeat5_rtx_evidence_2026-06-21.md`

and:

`docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_repeat5_rtx_evidence_2026-06-21.json`

Also inspect the stability repair artifact:

`docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_summary_large_stability_20260621/summary.json`

Context:

Your prior review approved the largest row conditionally, but blocked promotion
on two P0s:

1. Missing variance/stability data.
2. Missing oracle definition.

The repaired packet now adds:

- an oracle definition based on `expected_tiled_hausdorff(copies=N)`;
- a prepared-mode timing definition;
- single-pod/threshold/input-size scope limits;
- a five-sample independent paired process rerun for the large row, with all
  phase-total pairs above 1x and weakest phase-total speedup 1.224x.

Candidate wording under final review:

```text
RTDL V3 includes a generic Hausdorff threshold-summary route where, at
1,048,576 points per side and threshold 0.4 on a single RTX 4000 Ada pod,
prepared OptiX fixed-radius threshold decisions beat the same-contract Embree
route across five independent paired process samples: query speedup mean
1.639x, phase-total speedup mean 1.240x, weakest phase-total speedup 1.224x,
with repeat=5/warmup=1 inside each sample. Smaller rows in the same rerun are
query wins but not phase-total wins.
```

Please return Markdown only and do not edit files.

Required verdict shape:

1. Verdict: approve, approve with amendments, or reject.
2. Whether both previous P0s are now closed.
3. Whether the candidate wording is safe for row-scoped M7.
4. Any remaining P0/P1 fixes.
5. Exact final allowed wording if approved.
6. Exact forbidden wording.

Guardrails:

- Do not approve broad V3-over-V2 claims.
- Do not approve full Hausdorff witness/materialization claims.
- Do not approve X-HD paper reproduction claims.
- Do not approve all-scale/all-threshold/all-GPU wording.
- Keep the final claim row-scoped and same-contract.
