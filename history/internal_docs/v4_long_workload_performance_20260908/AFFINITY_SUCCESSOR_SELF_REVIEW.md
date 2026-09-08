# CPU-affinity successor self-review

Date: 2026-09-08, America/New_York. Status: formal transaction and independent
recount complete. This is an internal critical review, not an external
acceptance or claim authorization.

## Review question

Does exact worker CPU affinity repair a real measurement defect without
changing the application work, weakening PyOptiX, or turning a failed
transaction into a selectively relabeled pass?

## What is defensible

1. The unlocked transaction is complete adverse evidence, not an aborted
   diagnostic. All 240 workers and ten unit-endpoint evaluations are retained.
   Eight passed; Particle prepared and LibRTS range prepared failed only the
   worst-block gate.
2. The two failures were isolated to sub-millisecond prepared actions. Their
   paired medians passed, while individual blocks reached 1.462108x and
   1.563658x. Complete and multi-second graph rows did not show the same
   instability.
3. A separate balanced eight-block diagnosis changed only process affinity and
   brought both worst blocks below 1.02x. This establishes a concrete,
   reproducible measurement mechanism rather than a speculative source-code
   explanation.
4. Commit `02e84374f` changes only generic measurement tooling and tests. It
   does not alter an app path, callback, native DSO, PTX, `.rtdlexe`, workload,
   output contract, timer, repetition count, arm implementation, or threshold.
5. The control is symmetric: old RTDL, successor RTDL, and public PyOptiX all
   run on the same registered logical CPU. The worker binds before imports and
   records exact preflight and postflight state.
6. The successor has a new source identity, config, dry run, preregistration,
   schedule, output root, and independent recount. No sample from the unlocked
   transaction or affinity diagnosis is eligible for pooling.

## Remaining attack surfaces

### CPU 8 was selected after diagnosis

The diagnostic used CPU 8 before the formal successor was frozen. Therefore,
the formal result can establish performance under a registered stable CPU, but
not invariance over arbitrary host CPUs. The same-CPU comparison remains fair
within each block. The report must disclose selection chronology and must not
claim that affinity eliminates every infrastructure source of variance.

If GPU budget remains after formal closure, a clearly non-evidence sensitivity
check on several allowed CPU IDs should test whether the two short prepared
ratios remain within the engineering range. Such a check cannot change or
filter the formal transaction.

### GPU clocks are not locked

The container rejected the application-clock lock. Balanced arm order and
fresh processes mitigate order effects but do not prove clock invariance. The
report must retain raw block ranges, machine identity, and the failed lock
attempt. It may not describe the GPU as clock-locked.

### Affinity can improve RTDL more than PyOptiX

That is not itself bias: the paths have different host control overhead, and
both are constrained identically. However, the result should be described as
performance under a controlled host scheduler, not as a GPU-kernel-only ratio.
Prepared wall time includes each public arm's required synchronous host work.

### Very short rows remain intrinsically sensitive

The main directive prioritizes natural long work. Particle and LibRTS prepared
actions remain sub-millisecond, so their eight-block values are regression and
fixed-cost evidence rather than the headline long-workload result. Graph
cit-Patents/4M is the registered multi-second prepared natural computation.

### Schedule hashes have two representations

The preregistration stores the canonical JSON digest of the schedule payload.
The controller summary stores the byte SHA-256 of `SCHEDULE.json`. These are
intentionally different values. Controller admission and independent recount
validate both; reports must label them accurately rather than compare the two
as if they were the same hash.

## Pre-formal custody findings

- The first candidate config was serialized with sorted keys, changing the
  semantically registered arm order. Validation rejected it before worker zero.
  It remains under its original filename and is not called a dry-run result.
- The first freeze command omitted repository `PYTHONPATH`; it failed before
  creating preregistration bytes. The corrected invocation created a new file
  once. This operational failure is disclosed but did not alter the frozen
  protocol.
- The final dry run passed 15/15 workers, output parity, zero retry/discard, and
  exact affinity `{8}` both before and after every worker.

## Final internal verdict

The successor is internally accepted for the registered method and engineering
target. The wholly fresh transaction completed 240/240 workers, 80/80 paired
cells, 1,248 retained timed samples, and 120 warmups with exact output parity,
exact `{8}` preflight/postflight affinity, and zero retry, discard, or timeout.
All ten evaluations passed both thresholds. A different clean checkout imported
no project module, verified all raw hashes, reconstructed every journal and
cell, reproduced the controller projection exactly, and returned
`PASS__METHOD_AND_TARGET`.

The complete deterministic archive has 1,049 members, 730,851 bytes, and
SHA-256
`ef2ca7890c9d415dc1edbe71966aabc512209c9d8608d4eaf460c7c1fddf8bdc`.
A second deterministic archive was byte-identical. This closes the internal
method and engineering gate, not manuscript/public authorization.

The CPU-selection and unlocked-clock limitations above remain material. A
multi-CPU sensitivity study would strengthen robustness but is not allowed to
filter, replace, or relabel the passing formal transaction. Manuscript wording
must also state that only cit-Patents/4M is a multi-second prepared natural
computation and that the Particle route is a fixed app-shaped standard-library
specialization. New paper bytes require a separate claim and final-byte review.
