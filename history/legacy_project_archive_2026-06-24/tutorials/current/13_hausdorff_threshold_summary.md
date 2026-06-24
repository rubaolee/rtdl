# Hausdorff Threshold Summary

Status: V3 rebuild tutorial with one exact row-scoped M7 qualification, not a
release claim.

The row is useful and reviewed, but it is still not a release claim.

This lesson shows a practical V3 boundary: threshold decisions can benefit from
RTDL's prepared OptiX route, but that is not the same as full exact Hausdorff
distance or witness materialization.

## Current Evidence

The same-contract repeat=5 RTX rerun used `directed_threshold_prepared`,
threshold `0.4`, and warmup `1`.

| Copies | Points/side | Query OptiX / Embree | Phase-total OptiX / Embree | Reading |
| ---: | ---: | ---: | ---: | --- |
| 16,384 | 65,536 | 1.891x | 0.583x | query win, phase-total regression |
| 65,536 | 262,144 | 1.831x | 0.995x | query win, phase-total parity |
| 262,144 | 1,048,576 | 1.685x | 1.264x | candidate large-row win |

The M7-qualified row uses the follow-up five-sample stability rerun of the
largest row:

```text
row: hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped
query speedup mean: 1.639x
phase-total speedup mean: 1.240x
weakest phase-total speedup: 1.224x
phase-total includes scene preparation
```

## What To Learn

- `threshold_summary` is a scoped threshold-decision route.
- One exact large row is M7-qualified after Claude/Codex review.
- Smaller Hausdorff threshold-summary rows are not phase-total wins.
- The row is not full exact Hausdorff distance or witness materialization.
- V2.14 paired context is modest, not broad V3-over-V2 proof.

## Source Packets

- `docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_repeat5_rtx_evidence_2026-06-21.md`
- `docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_summary_repeat5_20260621/summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_hausdorff_threshold_summary_large_stability_20260621/summary.json`
- `docs/reviews/claude_phoenix_v3_hausdorff_threshold_summary_p0_repair_final_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_hausdorff_threshold_summary_p0_repair_2ai_consensus_2026-06-21.md`

## Claim Boundary

Allowed, exact-row only:

```text
RTDL V3 includes a generic Hausdorff threshold-summary route where, at
1,048,576 points per side and threshold 0.4 on a single RTX 4000 Ada pod,
prepared OptiX fixed-radius threshold decisions beat the same-contract Embree
route across five independent paired process samples: query speedup mean
1.639x, phase-total speedup mean 1.240x (phase-total includes scene
preparation), weakest phase-total speedup 1.224x, with repeat=5/warmup=1
inside each sample. Smaller rows in the same rerun are query wins but not
phase-total wins.
```

Forbidden:

```text
Do not claim RTDL computes full Hausdorff faster.
Do not claim Hausdorff V3 is faster end to end.
Do not claim X-HD is reproduced.
Do not claim V3 broadly accelerates Hausdorff over V2.
Do not claim OptiX is faster for all Hausdorff scales.
Do not claim OptiX is faster for all threshold values.
Do not claim OptiX is faster for all RTX GPUs.
```
