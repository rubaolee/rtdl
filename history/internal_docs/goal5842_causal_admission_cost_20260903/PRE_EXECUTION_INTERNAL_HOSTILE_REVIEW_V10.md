# Goal5842 V10 pre-execution internal hostile review

## Verdict

`ACCEPT_FOR_PREREGISTRATION_AND_GPU_EXECUTION_ONLY`.

V10 is an append-only pre-execution correction to V9. It does not authorize a
performance, overhead, portability, or CGO claim.

## Supersession audit

V9 is preserved byte-for-byte and records zero registered timing and zero
formal GPU executions. Its source manifest was frozen before an inherited
Goal5798 source-contract test exposed a compatibility regression in the
PyOptiX worker. V10 changes that worker only from a conditional expression to
an explicit guarded bulk-copy statement; runtime semantics are unchanged.
The V9 review is restored to its frozen bytes, and all later preflight evidence
is recorded here. No V9 row exists, no task or estimator changed, and no
observed ratio motivated the correction.

## Measurement boundary

All three arms expose the same registered public result: complete canonical
rows for relation and one checked U64 weighted scalar for triangle. Expected
output comparison occurs immediately after every measured call. Direct and
PyOptiX skip the auxiliary triangle per-ray host copy only in their explicit
Goal5842 public-output mode. RTDL retains its internal per-ray materialization
and host reduction as measured implementation cost. Separate no-clock
pre-worker-zero witnesses prove each arm's complete per-ray oracle.

## Unregistered engineering preflight

The Ada pod was used only for correctness/build preflight before a formal V10
transaction. These calls are not registered observations and never enter an
estimator:

- the Direct binary built successfully from candidate source;
- its no-clock relation witness produced 4,096 exact canonical rows from two
  OptiX launches, with zero status and overflow;
- its no-clock triangle witness produced 16,384 exact per-ray values and the
  weighted scalar 65,530 from one OptiX launch;
- a mismatched witness contract and ordinary timing mode was rejected before
  compilation or launch;
- the PyOptiX relation path produced 8,192 raw events and 4,096 exact canonical
  rows with expected-output comparison disabled inside the call;
- the PyOptiX triangle full-output and public-output-only exits agreed on
  scalar 65,530, while only the full exit returned the 16,384-element per-ray
  vector.

The focused Goal5842 plus prepared-cache suite passed 45/45 before V10 freeze.
The modified historical PyOptiX source passed its five immutable-input-reuse
tests. A broader inherited Goal5796/5798 run is not a clean denominator in this
recovery checkout: fifteen tests require historical evidence files absent from
the branch, and one unmodified native source no longer contains a legacy string
asserted by Goal5796. These are not reported as V10 passes or failures.
`clang-format` is unavailable on both the Mac and current pod; the C++ candidate
nevertheless compiled and executed both witness branches. Python syntax, Ruff
checks on current Goal5842 files, Ruff formatting, and `git diff --check`
passed.

## Frozen core and fatal gates

The three Goal5838 core files retain their required hashes. Any pre-worker
witness failure blocks worker zero. Any failure after worker zero terminates
the transaction without retry or dropped rows. One Ada result cannot satisfy
the two-generation gate. Cross-machine raw-time ratios remain forbidden.
External review and consensus remain owner-deferred and absent.
