# Goal1206 Gemini Review Request: Live Pod Merged Evidence

Please review the Goal1206 live RTX pod evidence before any public wording decision.

## Files To Review

- `docs/reports/goal1206_live_pod_result_and_embree4_recovery_2026-05-01.md`
- `docs/reports/goal1206_repaired_rtx_recovery_merge_intake_2026-05-01.md`
- `docs/reports/goal1206_repaired_rtx_recovery_merge_intake_2026-05-01.json`
- Original copied artifact directory:
  - `docs/reports/goal1204_live_pod_2026-05-01/`
- Recovery copied artifact directory:
  - `docs/reports/goal1204_embree4_usr_recovery_live_pod_2026-05-01/`

## Context

Goal1204 ran on an RTX 4090 pod. Initial Embree controls failed because the pod had Ubuntu Embree 3 while RTDL requires Embree 4. OptiX DB/Jaccard/road-hazard rows succeeded. We then installed Embree 4.4.0, exposed it under `/usr/include/embree4` and `/usr/lib/libembree4.so`, and reran only the failed Embree controls into a separate recovery artifact.

The merged intake reports:

- DB compact-summary 100k: Embree 0.338303s, OptiX 0.301344s, ratio 1.12265.
- DB compact-summary 300k: Embree 1.05533s, OptiX 0.906979s, ratio 1.16357.
- Road hazard 40k: Embree 0.814722s, OptiX 0.230652s, ratio 3.53225, OptiX clears 0.1s floor.
- Jaccard 8192 chunk 512: parity true, public-safe chunk policy true.
- Jaccard 8192 chunk 64: diagnostic-only and parity false.

## Questions

1. Is it technically acceptable to merge the original Goal1204 artifact with the Embree4 recovery artifact for evidence interpretation, given the recovery only reran failed controls and preserved the original artifacts?
2. Are the DB and road-hazard ratios valid same-scale candidates for later public wording review?
3. Is Jaccard correctly limited to public-safe correctness/readiness evidence rather than speedup wording?
4. Does the report clearly document the Embree 3 vs Embree 4 pod environment issue and the needed Linux `RTDL_EMBREE_PREFIX` fix?
5. Verdict: `ACCEPT` or `BLOCK`, with required fixes if blocked.

Please write the review to:

`docs/reports/goal1206_gemini_live_pod_merged_evidence_review_2026-05-01.md`
