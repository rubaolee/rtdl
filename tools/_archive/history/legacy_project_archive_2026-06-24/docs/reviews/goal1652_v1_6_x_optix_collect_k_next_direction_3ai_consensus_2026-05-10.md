# Goal1652 v1.6.x OptiX Collect-K Next Direction 3-AI Consensus

## Verdict

`accepted_directional_consensus`

Codex, Claude, and Gemini agree that the current v1.6.x OptiX collect-k
evidence supports a narrowed optimization direction rather than more broad
candidate searching.

## Inputs

- Goal1649 rejected full cooperative merge fusion at `262144` because current
  full-level cooperative residency exceeds the A4500 bound.
- Goal1650 fixed `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1` so long counts use
  the accepted CUB tiled path.
- Goal1651 rejected fused materialize+mark because it preserved parity but
  regressed performance.
- Goal1652 rejected non-CUB `4096` tile sort because it preserved parity but
  regressed performance severely.

External reviews:

- `docs/reviews/claude_goal1652_next_optix_collect_k_direction_review_2026-05-10.md`
- `docs/reviews/gemini_goal1652_next_optix_collect_k_direction_review_2026-05-10.md`

## Consensus

- Preserve the CUB tile-sort path for the current `262144` count class.
- Do not revisit non-CUB tiled sorting for this count class without a new
  reason; Goal1652 is a strong negative result.
- Do not pursue full-grid cooperative synchronization for the current
  `262144` merge shape; Goal1649 is a residency blocker, not a tuning miss.
- Do not pursue heavy fused kernels that require extra clearing or atomics
  unless a new design avoids Goal1651's cost pattern.
- Focus next on merge-side work after CUB sorting: merge synchronization,
  launch structure, metadata handling, and possibly a structural k-way merge.

## Ranked Next Candidates

1. Re-measure deferred merge synchronization at the corrected Goal1650
   `262144` fastest baseline and record it as accepted or rejected with
   artifacts.
2. Investigate CUDA Graph or stream-capture feasibility for the fixed merge
   dispatch sequence if the launch side remains material after deferred-sync
   remeasurement.
3. Investigate a CUB-preserving larger-tile option only if CUB can still provide
   a single efficient sort dispatch rather than per-tile manual sort launches.
4. Treat k-way merge as the higher-effort structural candidate because it
   directly attacks merge levels and merge synchronization.

## Claim Boundary

This is an engineering-direction consensus, not a public performance claim. It
does not authorize public speedup wording, stable `COLLECT_K_BOUNDED`
promotion, release tags, or release action.
