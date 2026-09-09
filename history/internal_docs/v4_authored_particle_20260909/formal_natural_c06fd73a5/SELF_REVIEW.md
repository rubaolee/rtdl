# Self-review: natural-scale Particle successor

Date: 2026-09-09

Verdict: `INTERNAL_ACCEPT_PREPARED_PATH__SETUP_DEBT_REMAINS`.

## Passed checks

- Exact commit/tree, GPU, native library, PyOptiX PTX, input, oracle and output
  identities are bound.
- The 57-test focused suite passed before the final source was pushed.
- A pre-worker-zero RTDL target-compatibility probe rejected the previously
  observed mixed PTX toolchain and passed under the registered toolchain.
- Eight fresh-process paired blocks use four A-first and four C-first orders.
- All 16 workers, 48 timed samples and 16 warmups are retained; retries,
  discards, timeouts and wrong outputs are zero.
- Both arms reuse resident queries and return the complete contiguous
  `uint32[160000000,3]` output.
- The compiler optimization is selected by verified Callback IR structure,
  not by application identity or data values.
- A separate clean clone independently reconstructed all numerical results and
  evidence bindings without importing the controller.

## Adverse facts preserved

- The formal v2 worker-zero PTX target failure remains archived.
- Pinning only the Numba binding was shown insufficient before the final
  protocol; the v3 protocol also binds CUDA component selection and probes the
  real RTDL route before preregistration.
- RTDL preparation is approximately 24.259 seconds versus 10.241 seconds for
  PyOptiX. The prepared-path pass does not erase this setup debt.
- The natural 160M action is approximately 0.35 seconds, not one second.
- No complete/lifecycle endpoint, cross-generation replication, locked-clock
  run, lead review or external review exists for this successor.

## Rejected shortcuts

- The composer target-identity check was not relaxed.
- The old failed transaction was not resumed, relabeled or pooled.
- No output bytes, D2H transfer, public validation or worst block was removed.
- The task was not padded with repeated queries, repeated actions, sleeps or
  slowed baseline code.
- No Particle-specific native entrypoint or application formula was added.

## Next gate

Before any complete-path performance wording, remove redundant fallback-leaf
compilation from the fully admitted inline route, measure exact preparation
phases, and run a new same-contract complete/prepared transaction only if the
source changes. Public and manuscript claims remain false until lead review.
