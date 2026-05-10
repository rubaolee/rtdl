# Goal1643 v1.6.x OptiX Collect-K Merge-Chain Direction 3-AI Consensus

## Verdict

`shift_next_target_to_merge_chain`

Codex, Claude, and Gemini agree that the next `COLLECT_K_BOUNDED` performance target should shift from the final mark/materialize kernels to the merge chain.

## Consensus

The accepted interpretation is:

- Goal1637 and Goal1641 show the final-pair mark and materialize kernels are small.
- Goal1642 shows deferred merge GPU work is large enough to explain the final-pair pre-mark wait.
- Goal1640 shows isolated final four-kernel graph replay is technically viable but too small and too isolated to justify production graph replay.
- The next optimization should reduce merge-chain cost: merge work, merge launch count, intermediate compacting, or dependency layout.

## Next Candidate

The safest next candidate is an opt-in merge-chain diagnostic, not a production flag:

- Measure a merge-chain graph or equivalent dependency-chain restructuring in isolation.
- Preserve parity checks before considering production use.
- Record merge event time, launch count, and total path timing together.
- Treat any positive result as internal evidence until it is measured on the accepted `COLLECT_K_BOUNDED` path.

## Claim Boundary

This consensus does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
