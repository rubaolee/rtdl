# Goal1646 v1.6.x OptiX Collect-K Good-Win Next Candidate 3-AI Consensus

## Verdict

`next_good_win_requires_merge_chain_restructure`

Codex, Claude, and Gemini agree that small local rewrites are unlikely to reach the `1.3x-1.5x` good-win target. The next serious candidate must restructure the merge chain.

## Consensus

The accepted interpretation is:

- Larger CUB tile candidates failed at runtime with CUDA invalid-argument errors.
- Raising the compact min-capacity routed work through an older merge path and was much slower.
- The vector-load candidate preserved parity but regressed performance.
- The remaining high-leverage target is reducing merge-chain work or merge-chain dependency overhead, not final mark/materialize kernels.

## Next Candidate

The next candidate should be an opt-in cooperative or multi-level merge-chain probe:

- Keep the current accepted path as the control.
- Implement a diagnostic path only; do not enable it by `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE`.
- Measure parity, merge event time, wrapper median, and profile total time against the same `candidate_count=262144` accepted workload.
- Only consider promotion if the candidate reaches at least `1.15x` in a first probe and has a plausible path to `1.3x`.

## Claim Boundary

This consensus does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
