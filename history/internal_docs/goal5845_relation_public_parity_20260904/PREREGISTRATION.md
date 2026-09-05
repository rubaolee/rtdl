# Goal5845 Frozen Engineering Comparison

## Question

Can the ordinary row-returning RTDL public bounded-relation route preserve its
full canonical-row contract, fail-closed status, generic family checks, and two
actual OptiX launches while removing the Goal5843 implementation overhead
relative to the pinned PyOptiX compatible-API baseline?

## Prior diagnostic disclosure

This freeze follows implementation and unregistered diagnostics. On the target
RTX 2000 Ada pod, one 128-sample diagnostic observed approximately 0.366 ms for
the complete RTDL public route, 0.276 ms for its direct native v8 ABI, and a
separate 64-sample diagnostic observed approximately 3.568 ms for PyOptiX. Those
numbers guided engineering only. They are not formal evidence and are not
pooled into this transaction.

## Frozen design

- One clean source commit and one freshly built native DSO are bound before any
  registered worker starts.
- The task is the unchanged Goal5798/Goal5843 4096-by-4096 bounded relation,
  returning exactly 4096 canonical `(source_id, item_id)` rows.
- RTDL and PyOptiX use the same source/indexed boxes and public row oracle.
- Each arm runs in a fresh process in each block.
- Eight blocks alternate arm order. Each worker performs 16 warmups and retains
  all 128 steady samples, for 1024 samples per arm and zero discards.
- Correctness checks and receipt expansion occur outside registered intervals.
- RTDL must expose two successful audited OptiX launches, compact fail-closed
  status, device semantic compaction, and immutable public rows.

## Pass gates

- Every worker and exact public oracle passes.
- All 2048 registered samples are retained.
- Median of the eight within-block `RTDL/PyOptiX` median ratios is at most 1.25.
- Every within-block `RTDL/PyOptiX` median ratio is at most 1.50.
- Median within-block `RTDL public/direct native v8` is at most 1.75.

These are engineering parity gates, not a promise that RTDL intrinsically
outperforms arbitrary hand-optimized PyOptiX code.

## Claim boundary

Passing authorizes only the internal statement that the measured Goal5843
row-path performance defect was removed for this exact implementation,
workload, output contract, software stack, and GPU. It does not authorize a
public or manuscript claim, cross-hardware generalization, arbitrary workload
claim, external consensus, or a language-overhead theorem.
