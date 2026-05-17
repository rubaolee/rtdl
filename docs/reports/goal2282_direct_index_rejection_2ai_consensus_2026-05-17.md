# Goal2282: Direct-Index Rejection 2-AI Consensus

Status: accepted.

## Scope

Goal2282 closes the Goal2279/2280 direct-index host exact-refinement experiment.
The decision is narrow: direct primitive-index threading through the OptiX
segment-pair candidate row is rejected for the current v2.0 RayJoin/LSI
optimization lane, and the implementation was reverted.

## Evidence

- Codex implementation attempt:
  - `ffedd43aad096d40e1a1e7c863573c6b25733c54`
  - `2a63e71dcb31f7227673d2055b749757aa5e8f9b`
- Revert commits on `main`:
  - `5dbe9863`
  - `ad78015d`
- Same-pod A/B report:
  `docs/reports/goal2280_direct_index_refinement_negative_ab_probe_2026-05-17.md`
- Canonical paired summary:
  `docs/reports/goal2280_direct_index_ab_same_pod_summary_2026-05-17.json`
- Gemini review:
  `docs/reviews/goal2281_gemini_review_goal2280_direct_index_negative_probe_2026-05-17.md`

## Consensus

Codex verdict: `accept` the rejection and revert.

Gemini/Antigravity verdict: `accept`.

The agreed interpretation is:

- raw witness rows regressed in the canonical same-pod A/B (`0.944x`);
- scalar count was effectively neutral (`1.004x`);
- direct-index host exact refinement is not an accepted v2.0 performance win;
- `main` should stay on the accepted Goal2275 cached-lookup implementation;
- future work should target generic device-resident or partner-continuation
  paths for segment-pair predicate/count, without RayJoin-specific native
  engine logic.

## Claim Boundary

Allowed claim:

RTDL tested and rejected direct-index host exact refinement for the prepared
segment-pair path on the recorded RTX A5000 RayJoin-exported 100k LSI stream.

Not allowed:

- direct-index speedup claim;
- whole RayJoin speedup claim;
- RayJoin paper reproduction claim;
- RTDL beats RayJoin claim;
- broad RT-core acceleration claim;
- true zero-copy or pure device-resident continuation claim.
