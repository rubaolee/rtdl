# Phoenix V3 Hausdorff Threshold-Summary Repeat Evidence

status: hausdorff_threshold_summary_repeat5_evidence_not_promoted

This packet compares Embree and OptiX on the same prepared fixed-radius
threshold-decision contract. It is evidence for `threshold_summary`, not
full exact Hausdorff witness materialization and not release authorization.

## Summary

- All pairs match oracle: `True`
- All pairs same decision: `True`
- All pairs repeat/warmup: `True`
- Strongest query OptiX/Embree speedup: `1.8914684826636867`
- Weakest query OptiX/Embree speedup: `1.6854780771390951`
- Strongest phase-total OptiX/Embree speedup: `1.2643173197147244`
- Weakest phase-total OptiX/Embree speedup: `0.5832587404633324`

## Pairs

| Copies | Points/side | Repeat | Embree query | OptiX query | Query speedup | Embree phase total | OptiX phase total | Phase speedup | Oracle |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 16384 | 65536 | 5 | 0.495686 | 0.262064 | 1.89147x | 1.03269 | 1.77056 | 0.583259x | `True` |
| 65536 | 262144 | 5 | 2.1301 | 1.1632 | 1.83124x | 4.39533 | 4.41887 | 0.994673x | `True` |
| 262144 | 1048576 | 5 | 10.2396 | 6.07519 | 1.68548x | 19.9047 | 15.7434 | 1.26432x | `True` |

## Claim Boundary

- Not full exact Hausdorff distance or witness materialization.
- Not X-HD paper reproduction.
- Not broad V3-over-V2 wording.
- Not M7 until external review and Codex consensus.

## Goal-Level Decision Audit

Decision: rerun Hausdorff threshold_summary with same-contract repeat evidence before any M7 reconsideration.

1. Was I foolish?

   No. This directly addresses the repeat1/no-current-RTX blocker without changing the threshold_summary contract.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would be promoting the old repeat1 wall result or switching to full Hausdorff wording.

3. Was there another path?

   Yes. The robot collision flag stream could be tuned next, but its blocker is wall/probe-reference dominance, not just missing repeats.

4. Can I now try a different path that actually solves the problem?

   Yes. Use this repeat evidence to decide whether threshold_summary deserves external row-scoped review or remains a boundary lesson.

