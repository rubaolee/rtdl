# Goal1204 Gemini Review Request: Repaired RTX Pod Packet

Please review the Goal1204 repaired RTX pod packet before it is used on a paid RTX cloud pod.

## Files To Review

- `scripts/goal1204_repaired_rtx_pod_packet.py`
- `scripts/goal1204_repaired_rtx_pod_executor.sh`
- `tests/goal1204_repaired_rtx_pod_packet_test.py`
- `docs/reports/goal1204_repaired_rtx_pod_packet_2026-05-01.json`
- `docs/reports/goal1204_repaired_rtx_pod_packet_2026-05-01.md`
- Background repaired local goals:
  - `docs/reports/goal1202_db_chunked_compact_summary_2026-05-01.md`
  - `docs/reports/goal1203_jaccard_chunk_policy_2026-05-01.md`

## Context

Goal1200 found that several RTX pod probes failed or could not support public wording:

- DB 100k/300k failed before the new compact-summary chunking repair.
- Jaccard chunk 64 failed parity and must not be public claim-path evidence.
- Road hazard 20k OptiX was faster than Embree but below the 0.1s timing floor.

Goal1204 is a cost-saving single-pod packet that should validate repaired paths in one session:

- DB Embree/OptiX 100k and 300k compact-summary chunked paths.
- Jaccard OptiX 8192 with public-safe chunk 512.
- Jaccard OptiX 8192 with diagnostic chunk 64, explicitly diagnostic-only.
- Road hazard Embree/OptiX 40k for a same-scale floor-safe rerun.

## Questions

1. Is the pod packet complete enough to justify one paid pod run for these repaired paths?
2. Does it preserve the public-claim boundary, especially for Jaccard chunk 64 and road-hazard floor repair?
3. Are there missing same-scale controls or obvious pod-cost inefficiencies?
4. Verdict: `ACCEPT` or `BLOCK`, with required fixes if blocked.

Please write the review to:

`docs/reports/goal1204_gemini_repaired_rtx_pod_packet_review_2026-05-01.md`
