# Goal5842 V6 pre-worker-zero failures and V7 repair

Date: 2026-09-03

## Classification

Goal5842 V6 did not reach worker zero and produced no registered timing. Two
create-only preflight roots are preserved byte-for-byte in
`pod_artifacts/goal5842_v6_preworker_failures.tar.gz`:

- bytes: `3761`
- SHA-256: `9f32d8aab3be262148bc10eeac55c92f950d483207240c42323371b5a0839bb1`
- source commit: `1a2b98abf5c04c095f81f05b17f91a62e120ffca`

Neither attempt is a completed V6 transaction, a performance observation, or
evidence that may be pooled into a later estimator.

## Attempt 1

The first root, `goal5842-ada-1a2b98abf-replication06`, failed in stage 00
before execution authority was created. The non-login process environment did
not expose `nvcc` on `PATH`. It performed zero GPU calls and observed zero
registered timings. This is an environment invocation defect, not a scientific
result.

## Attempt 2

The second root, `goal5842-ada-1a2b98abf-replication06-env02`, supplied the
frozen CUDA environment explicitly. Stage 00 passed and created an execution
authority. Stage 01 then completed all 72 timer-free relation CHECK_ON calls.
Every call matched the frozen output and reported
`optix_traversal_observed`. After that loop, the witness incorrectly searched
for `execution_count` at the top level of the public generic lifecycle receipt.

The public receipt intentionally has two layers:

1. `rtdl.generic_family_lifecycle.v1`, which owns generic identity and
   lifecycle policy;
2. `provider_receipt`, which owns provider-specific execution state and its
   `execution_count`.

The witness raised before completing its first arm because it ignored that
documented nesting. No causal worker, baseline subworker, or registered clock
started. The 72 untimed GPU calls are disclosed engineering evidence that the
V6 two-phase prepared-cache repair survives the repeated execution shape; they
are not a complete V6 witness and cannot count toward V7.

## V7 repair boundary

V7 changes only the witness interpretation and its evidence schema. It now:

- requires the outer schema to be `rtdl.generic_family_lifecycle.v1`;
- requires a mapping-valued `provider_receipt`;
- validates the exact expected provider lifecycle schema for each task;
- reads the integer execution count from that nested provider receipt; and
- emits both lifecycle schema identities for independent recount.

The independent recount implements the same two-layer validation separately.
A local regression test proves that a top-level-only `execution_count` is
rejected. V7 repeats all 290 RTDL witness calls and all 144 PyOptiX witness
calls before worker zero. It preserves the V6 tasks, inputs, schedules, phase
boundaries, statistics, hardware design, and claim ceiling. V7 is an
append-only full replication, not a retry of V6.

## Claim boundary

This repair authorizes only a new V7 pre-worker-zero attempt. It does not
reclassify either V6 root as success, authorize timing claims, establish a
second GPU generation, or provide external review or consensus.
