# Goal1639 v1.6.x OptiX Collect-K Graph Direction 3-AI Consensus

## Verdict

`do_not_revive_old_per_level_graph_replay`

Codex, Claude, and Gemini agree that the old per-level CUDA graph replay path should not be revived as a production `COLLECT_K_BOUNDED` optimization from the current evidence.

## Consensus

The accepted interpretation is:

- Goal1637 shows the final-pair mark kernel is small; the large observed cost is host-visible wait / stream dependency time.
- Goal1638 shows a small positive graph replay signal at the largest legal single-pair diagnostic size, but the old probe cannot run at the current final-pair `segment_capacity=131072` target because its total-block guardrail is `1..512`.
- Historical Goal1560/Goal1561 rejection of per-call/per-level graph replay remains valid.
- A production candidate should only be pursued as a prepared end-to-end stable-topology graph or equivalent dependency-chain restructuring measured at the real final-pair scale.

## Next Probe

The next safest probe is a new production-relevant diagnostic that measures the real final-pair chain at `pair_count=1` and `segment_capacity=131072`:

- Direct sequence: final merge/materialize, mark, prefix, compact.
- Candidate sequence: prepared stable-topology CUDA graph or equivalent stream-dependency restructuring.
- Required comparison: replay or steady-state candidate timing versus the direct path at the same scale.
- Required isolation: if a device-to-host count dependency remains on the critical path, record it separately rather than attributing it to kernel execution.

## Claim Boundary

This consensus does not authorize public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-application speedup claims, release tags, or release action.
