# Self-review: authored Particle formal successor

Date: 2026-09-09

Verdict: `INTERNAL_ACCEPT_WITH_STRICT_CLAIM_BOUNDARY`.

## Checks completed

- Exact source, tree, native, PTX, input, GPU and output identities are bound.
- The 67-test focused suite passed on the target before execution.
- Calibration was C-only and occurred before preregistration.
- Eight paired blocks have balanced order and fresh processes.
- All 3,440 primary timings, all eight blocks and both lifecycle workers are
  retained; retries and discards are zero.
- Both arms use resident query batches and transfer zero query bytes inside the
  primary timer.
- Both arms execute real OptiX and return the same complete `uint32[5000,3]`
  output.
- The independent recount imports no formal controller and reconstructs every
  worker median, block ratio, aggregate, bootstrap interval and lifecycle
  ratio from raw worker bytes.
- The recount verifies all 18 retained complete outputs byte-for-byte against
  the preserved oracle.
- A byte-corruption regression test proves that output mutation is rejected.
- No Particle vocabulary or application formula was added to `src/rtdsl` or
  `src/native`.

## Material limitations

1. This is a roughly 0.15-0.17 ms prepared call, not a natural task lasting at
   least one second.
2. Each worker retains its final complete output, not all 3,440 complete output
   vectors. Every timed call did perform the exact oracle check.
3. The lifecycle observation has one worker per arm and is adverse at
   `9.773846648838797x`.
4. The RTDL and PyOptiX host wrappers implement the same external output
   contract but do not execute byte-identical host control code. RTDL includes
   more public receipt/digest work inside its timer.
5. GPU clocks were not locked. Pairing and balanced order reduce but do not
   eliminate temporal variation.
6. Sampled GPU memory is a 5 ms lower-bound observation, not allocator-level
   peak memory authority.
7. This is one Ada GPU and has no cross-generation replication.
8. Independent external review is absent. No manuscript number should be
   changed from this internal result alone.

## Rejected alternatives

- The early comparator that uploaded seven query columns on every timed call
  was rejected as unfair before formal worker zero.
- The passing `832c97e02` transaction was not declared final because it retained
  only per-worker output hashes. It remains immutable predecessor evidence.
- The result was not improved by dropping the worst block, subtracting host
  work, pooling old diagnostics or changing the registered thresholds.
- A post-download shell command used zsh's read-only variable name `status`
  after the recount had already succeeded. The wrapper print/exit step failed;
  no GPU action was repeated. A direct `cmp` rerun returned zero and proved the
  two independently generated recount JSON files byte-identical.

## Remaining blocker

The Particle row is not closed for the long-workload directive until a real
distinct-query batch takes at least one second at the prepared endpoint and is
measured under the same complete-output, resident-query and no-app-engine-logic
rules. This report is a strong short-task overhead result, not that missing
natural-task authority.
