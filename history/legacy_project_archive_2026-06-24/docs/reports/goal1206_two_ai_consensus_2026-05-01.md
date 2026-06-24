# Goal1206 Two-AI Consensus

Date: 2026-05-01

Verdict: `ACCEPT`

## Scope

Goal1206 interprets the Goal1204 RTX 4090 pod run together with the Embree4 recovery controls.

## Evidence

- Original artifact: `docs/reports/goal1204_live_pod_2026-05-01/goal1204_repaired_rtx_pod.tgz`
- Original artifact SHA256: `4f2674d27ee3a0947e080c565da1af5330be11d8b49d76328056d8522238d7d8`
- Recovery artifact: `docs/reports/goal1204_embree4_usr_recovery_live_pod_2026-05-01/goal1204_embree4_usr_recovery.tgz`
- Recovery artifact SHA256: `cc4778da52198efcf451101283aeb7a0dd2d8f335b9e58a1d7e364fb188aa953`
- Merged intake: `docs/reports/goal1206_repaired_rtx_recovery_merge_intake_2026-05-01.md`
- Result report: `docs/reports/goal1206_live_pod_result_and_embree4_recovery_2026-05-01.md`
- Gemini review: `docs/reports/goal1206_gemini_live_pod_merged_evidence_review_2026-05-01.md`

## Conclusions

- Merging the original Goal1204 artifact with the targeted Embree4 recovery controls is accepted because the recovery only reran failed Embree controls and preserved the original failure artifact.
- `database_analytics` compact-summary chunking is repaired at 100k and 300k on the RTX pod evidence set:
  - 100k: Embree `0.338303s`, OptiX `0.301344s`, ratio `1.12265`.
  - 300k: Embree `1.05533s`, OptiX `0.906979s`, ratio `1.16357`.
- `road_hazard_screening` is a same-scale, floor-safe positive candidate:
  - 40k: Embree `0.814722s`, OptiX `0.230652s`, ratio `3.53225`.
- `polygon_set_jaccard` has correctness/readiness evidence for public-safe chunk `512`, but chunk `64` remains diagnostic-only and parity-failing.

## Non-Blocking Follow-Up

The Linux Embree runtime should respect `RTDL_EMBREE_PREFIX`. The current Linux default to `/usr` caused avoidable pod setup failure when Embree 4 was installed under `/opt/embree-4.4.0`.

## Boundary

Goal1206 accepts the merged evidence as technically sound. It does not by itself authorize public docs, release, or final public RTX speedup wording. A separate public wording decision/review should promote any claims.
