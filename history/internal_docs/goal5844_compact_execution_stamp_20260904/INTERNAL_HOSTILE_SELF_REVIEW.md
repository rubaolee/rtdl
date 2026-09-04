# Goal5844 internal hostile self-review

Date: 2026-09-04

Status:
`ACCEPT_SOURCE_AND_LOCAL_CORRECTNESS_WITH_GPU_BUILD_AND_PERFORMANCE_GATE_OPEN`

External review count: zero. This is an internal review and cannot be counted
as independent consensus.

## Question under review

Goal5843 measured the ordinary public triangle scalar path at 0.436590 ms,
2.910x the pinned PyOptiX-compatible API on one RTX A6000. Goal5842R1 layer
diagnostics placed the existing native v7 operation near 0.066 ms, provider
execution without the old audit near 0.143 ms, provider execution with the old
audit near 0.236 ms, and the public path near 0.276 ms. Goal5844 asks whether
the remaining public overhead can be reduced without removing semantic,
native-identity, status-before-output, and true-OptiX traversal checks.

## Implemented change

- A versioned native v8 ABI wraps the existing app-neutral v7 triangle
  operation with traversal-audit begin and finish inside one native call.
- The ordinary scalar route receives one native snapshot, validates a compact
  execution stamp, and emits a sealed compact receipt.
- The stamp binds fresh nonce/sequence, launch and context counts, raygen
  count, both program-bundle edges, one nonzero traversable, bundle/traversable
  mixes, provider identity, route identity, semantic identity, and output.
- The steady integrated route no longer calls the separate native cache-digest
  accessor. Native v8 still validates the expected digest in-call and returns
  the exact prepared-input generation, which Python checks.
- Query pointers, scalar/status/fast-receipt storage, and the successful status
  row are retained under the prepared owner's existing process/thread and
  nonreentrancy boundary.
- Full forensic expansion remains available explicitly after execution; it is
  not constructed inside ordinary public timing.
- Old DSOs without v8 continue through the existing v7 plus separate-audit
  route.
- The balanced GPU controller retains all samples, alternates arm order,
  recomputes worker seals and medians, and independently revalidates compact
  and full traversal receipts.

## Hostile findings and resolutions

### Verified: forensic snapshot ownership

The runner expands and retains the provider-owned forensic observation before
entering direct-native attribution. The direct probe uses separate scalar,
status, receipt, and audit-snapshot storage, so it cannot mutate the retained
provider receipt. The two layers remain separately labeled.

### Resolved: unnecessary core authority churn

The first implementation placed checked audit helpers in
`rtdl_optix_core.cpp`. That file is a source-authority anchor for unrelated
physical contracts. The helpers now live only in `rtdl_optix_api.cpp`, next to
the old exported audit wrappers and new v8 ABI. The core file is byte-identical
to HEAD.

### Resolved: mutable ctypes alias risk

The lazy fast-operation receipt references prepared-owner scratch storage.
That object appears only in the owner's latest lifecycle boundary and is
materialized into a plain dictionary whenever the lifecycle receipt is read.
No public execution result retains that mutable view. Compact traversal
receipts are fresh ordinary dictionaries and survive the frozen generic
execution envelope unchanged.

### Resolved: controller trusted worker summaries

The first controller read worker medians without independently checking their
seals or retained samples. It now recomputes each worker seal, sample count,
minimum, median, and maximum; checks source, arm, block, hardware, task and
claim boundaries; rehashes native/device sources; and revalidates RTDL compact
and full receipts.

### Resolved: failure and replay paths

Tests cover native-call failure, compact device-status failure, prepared-input
generation mismatch, and replayed native audit sequence. Each case publishes
no scalar, clears local reuse identity, consumes the failed sequence, and
requires a fresh upload before a later successful execution. Native fresh
upload invalidates any uncommitted predecessor before fallible work, so a
Python-side post-launch proof rejection cannot make stale native state reusable.

## Remaining blocking gates

1. The new C++ path has not been compiled against a real CUDA/OptiX toolchain.
2. Native v8 success, failure cleanup, exact snapshot contents, and DSO symbol
   export have not been exercised on a GPU.
3. No balanced RTDL/PyOptiX Goal5844 timing exists. The 1.25x ratio is an
   engineering target, not a result.
4. If the ratio remains above 1.25x, retained adverse rows must drive the next
   measured optimization. Relabeling the interval or dropping slow samples is
   forbidden.
5. External review remains deferred. No public or manuscript wording is
   authorized even if the internal engineering target passes.

## Local validation

- Goal5844 focused tests: 12/12 PASS.
- Directly related provenance/protocol/cache compatibility set: 51/52 PASS
  with one expected no-GPU platform skip and zero failures.
- Goal5842 causal-admission compatibility set: 40/40 PASS.
- Goal5838 frozen-core seal verification: PASS; all three frozen files are
  unchanged.
- Goal5840--Goal5844 adjacent run: 159 tests executed with five known
  historical/current-tree identity refusals and no new functional failure.
  Two are old Goal5840 repair-freezer replay debts, one is the frozen
  Goal5842R1 implementation-commit check, and two require the current tree to
  equal the old Goal5843 preregistration. These historical artifacts must not
  be rewritten to make a successor worktree appear green.
- Python compile checks and `git diff --check`: PASS.
- A broader ad hoc combination exposed three old Goal5790 integration errors
  before execution because their generated Goal5789 shared-contract freeze is
  absent from the current Git tree. That historical authority was not
  fabricated, and those errors are not counted as Goal5844 functional passes.

The focused count above must be regenerated if tests change before commit.

## Claim ceiling

The implementation supports only this statement before GPU work: RTDL has a
source-level, locally tested compact proof path intended to remove redundant
steady crossings while preserving the public scalar and proof boundary. It
does not yet establish lower latency, PyOptiX parity, a general language
overhead bound, hardware independence, public performance, manuscript
performance, or consensus.
