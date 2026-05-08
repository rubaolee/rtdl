# Goal 1567: output-indexed collect-k fused materialize+mark diagnostic

## Verdict

The output-indexed merge-path fused materialize+mark diagnostic preserves
parity on the controlled RTX pod probe, but it is still slower than the
existing four-kernel reference block. Do not promote this design into the
production `COLLECT_K_BOUNDED` path.

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- Commit base while testing: `b96a0a48` plus local Goal 1567 diagnostic edits
- Library: `build/librtdl_optix.so`
- Probe: `scripts/goal1567_v1_5_4_optix_collect_k_output_indexed_fused_probe.py`
- Reference block: materialize, mark, prefix, compact
- Candidate block: output-indexed merge-path materialize+mark, prefix, compact
- Repeats: `2000`
- Segment capacity: `2048`

## Result

| pair count | mismatches | reference us/replay | fused us/replay | reference/fused |
|---:|---:|---:|---:|---:|
| 1 | 0 | 10.905596 | 11.840938 | 0.921x |
| 4 | 0 | 11.679407 | 13.041909 | 0.896x |
| 16 | 0 | 17.101512 | 21.461749 | 0.797x |

## Interpretation

The reviewed stable merge-path logic is correct in this diagnostic. It avoids
Goal 1565's resets and atomics, but the extra merge-path binary searches are
still more expensive than the saved mark launch at this scope.

This is a better negative than Goal 1565: it shows the loss is no longer caused
by atomic block-count accumulation. The remaining cost is the output-indexed
merge-path work itself, especially the second lookup used for predecessor
comparison.

## Next Direction

Do not continue compact-level fusion by adding more complex merge-path logic
unless a narrower microbenchmark proves the predecessor lookup can be removed
or amortized. The next practical path should be profiling-driven:

- inspect whether the current accepted long-case profile is still dominated by
  launch overhead or by merge work;
- if launch overhead remains dominant, investigate larger-level batching or
  persistent-topology reuse only for repeated compatible calls;
- if merge work dominates, stop launch-reduction work and move to algorithmic
  changes outside this compact-level block.

This result is diagnostic only and does not authorize public speedup wording.
