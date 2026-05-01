# Goal1205 Gemini Review Request: Repaired RTX Pod Intake

Please review the Goal1205 intake tool before the next paid RTX pod run.

## Files To Review

- `scripts/goal1205_repaired_rtx_pod_intake.py`
- `tests/goal1205_repaired_rtx_pod_intake_test.py`
- `docs/reports/goal1205_repaired_rtx_pod_intake_local_prep_2026-05-01.md`
- Related packet:
  - `scripts/goal1204_repaired_rtx_pod_packet.py`
  - `scripts/goal1204_repaired_rtx_pod_executor.sh`
  - `docs/reports/goal1204_repaired_rtx_pod_packet_2026-05-01.md`

## Context

Goal1204 prepares a single paid-pod batch for repaired DB compact-summary chunking, Jaccard chunk policy, and road-hazard timing-floor repair. Goal1205 prepares the local intake script that will parse the copied-back Goal1204 artifact.

The intake must:

- Mark DB repair passed only when both Embree and OptiX 100k/300k rows are `ok` and both report chunked compact-summary metadata.
- Mark Jaccard ready only when chunk 512 is public-safe and chunk 64 is diagnostic-only.
- Mark road hazard as a same-scale public-positive candidate only when OptiX clears the 0.1s floor and is faster than same-scale Embree.
- Preserve the boundary that no public docs, release, or speedup wording are authorized by the intake alone.

## Questions

1. Is the intake schema aligned with the Goal1204 executor output labels and JSON shapes?
2. Are the decision rules conservative enough for public-claim discipline?
3. Are any missing fields or failure modes likely to make post-pod interpretation unsafe?
4. Verdict: `ACCEPT` or `BLOCK`, with required fixes if blocked.

Please write the review to:

`docs/reports/goal1205_gemini_repaired_rtx_pod_intake_review_2026-05-01.md`
