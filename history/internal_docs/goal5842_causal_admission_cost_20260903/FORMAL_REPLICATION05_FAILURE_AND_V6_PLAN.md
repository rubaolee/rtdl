# Goal5842 replication05 terminal failure and V6 plan

## Immutable replication05 status

Replication05 is a terminal failed transaction. It is not resumed, retried,
repaired in place, or reclassified as successful. Its create-only root was
`/workspace/goal5842-ada-472b0fc96-replication05`; worker zero was crossed, and
the transaction wrote `TRANSACTION_FAILED_NO_RETRY.json` after baseline stage
04 failed.

The repository-preserved archive is
`pod_artifacts/goal5842_replication05_failure.tar.gz`: 227,006 bytes, SHA-256
`0dcb379450de007b5494597771b3a50b85e5db572d4e571ef5114170c74e90ce`.
Its exact source commit was
`472b0fc963b317672ca2e3b0dbdb888cf414b3d4`. The controlling V5
preregistration has internal seal
`bcb1980055d608b4b4b7d0242defbfd3f11669aab5a2b6ecc716cb7e669e43cc`
and whole-file SHA-256
`f2d6f7039d27b5fbddd0c5636e994669ab1ffdc22c522cb083bcb4ddc444fdf3`.

Selected archive member whole-file identities are:

| Member | SHA-256 |
|---|---|
| `execution_authority.json` | `884f0f2eacb7cc58bea5221c1f3b409aa77a1dfd2288638d02f083d6428134ed` |
| `gpu_identity_witness.json` | `751450720094751e75325e018b247eb8e1315cf66881f7c2aa2a96550a47c156` |
| `pyoptix_identity_witness.json` | `3eee25d89378909c3a23ac1f4231a6c200ef15d9d0f01008cb9a572d72e7e3ac` |
| `causal/result.json` | `59561f75402918959d5293a15125e429ffe2b645f64a0970aff2f29956bf93c8` |
| `TRANSACTION_FAILED_NO_RETRY.json` | `930a4815aa8c11adf5e3f072eb437e1bcb31e21f8ddb10ac98280bc849fc870c` |
| failed RTDL steady `failure.json` | `6eea83af0160ba75491768dc036bb7726cab7d383d43f3d85f0a825869b036ee` |
| failed RTDL steady `stderr.txt` | `d6670eaa90509486b24eae37b90b77caff5ce80de08fd5aa9df08c72c1ccbb30` |

The bound first-generation device was one NVIDIA RTX 2000 Ada Generation,
compute capability 8.9, UUID
`GPU-f0ab2afa-0ec0-7da9-c951-01fc713ee1e9`, driver 580.159.04. The authority
seal was `beff57f8f0f4543ff6efb6167b36bf537384325c5deadd2227ccec773612ad13`.

## What completed before failure

- The no-registered-timing RTDL identity witness completed six executions over
  all three tasks and preserved exact CHECK_ON/CHECK_OFF executable and output
  identity.
- The no-registered-timing package-front-door PyOptiX witness completed both
  baseline tasks. It used one exact PTX payload for both tasks and registered
  no timing.
- All 216 causal workers completed. Their three descriptive V5 medians were
  38.490055 ms for relation, 34.772631 ms for triangle, and 28.050687 ms for
  sphere. These rows remain failed-transaction diagnostics and are not pooled
  into V6 or any cross-generation estimator.
- Five baseline subworker receipts completed: Direct relation first and steady,
  PyOptiX relation first and steady, and RTDL relation first. The successful
  receipts contain 131 registered execution samples in total.
- The failed RTDL steady process completed one untimed warm-up execution. Its
  next repeated call was rejected before a valid application result existed.

None of these partial results is a Goal5842 performance result. There is no
baseline controller result, independent recount, complete transaction marker,
cross-generation authority, public performance claim, external review, or
consensus.

## Root cause

The public generic-family relation route reaches
`v4_bounded_relation_prepared_runtime.PreparedBoundedRelationOwner`. On its
first execute, native code uploads source rows and deliberately marks the
native source cache valid but uncommitted. The Python owner retained the input
object and ctypes arrays but never called the native digest-bearing commit ABI.
On the second execute it nevertheless requested reuse. Native code correctly
failed closed with:

`V4 prepared bounded relation source-cache reuse is invalid`

The same missing two-phase handoff existed in the public triangle-reduction
prepared owner and would have threatened a later steady row. This is a generic
runtime correctness defect, not an application-specific limitation and not an
opportunity to tune a result after seeing timing. The mature RTDLEXE owner
already implements the intended protocol.

## Correctness repair boundary

The V6 source repair is limited to the two app-neutral public prepared owners:

1. Require and bind the native cache commit and digest-query ABIs.
2. Hash the exact normalized packed dynamic inputs.
3. Commit only after native output validation and traversal-audit completion.
4. Read the digest back and require exact equality before publishing a local
   reusable identity.
5. Require both local immutable-input identity and native digest identity for
   reuse.
6. Clear all local cache identity on every `BaseException` window.
7. Apply the same protocol to relation and triangle; add no task name,
   application semantics, or frozen-core edit.

Repreparing every measured iteration is explicitly rejected: it would hide the
correctness defect and invalidate the preregistered steady-state comparison.
This is a correctness repair between terminal transactions, not a
post-result RTDL-only optimization inside replication05.

## Independent V6 execution

V6 is a new, create-only full replication. It preserves the V5 tasks, inputs,
oracles, causal arms, baseline arms, schedules, phase boundaries, statistics,
and absence of a success threshold. It changes the RTDL provider implementation
only by the disclosed generic correctness repair and strengthens pre-worker-zero
validation.

Before V6 worker zero:

- RTDL CHECK_ON and CHECK_OFF must each execute the relation and triangle
  prepared owner for exactly 8 warm-up-equivalent plus 64 steady-equivalent
  calls. The witness module imports and calls no clock, records no duration,
  and does not consume the public owner's ordinary internal `prepare_seconds`
  field. Sphere remains one complete call per arm.
- Every repeated output, full oracle, executable identity, and traversal receipt
  must pass. The relation and triangle lifecycle receipts must each report 72
  executions per prepared owner.
- The PyOptiX package front door must execute each baseline task 72 times. Its
  witness module imports and calls no clock, records no duration, and must match
  every oracle.
- The exact execution authority, source commit, native DSO, Direct binary,
  provider source, SDK headers, Python environment, and GPU remain hash-bound.

Only after all no-registered-timing witnesses pass may the causal controller
establish worker zero. After worker zero the existing no-retry, no-drop,
no-replacement policy applies. V4 and V5 rows remain excluded from V6
estimators.

## Claim boundary

V6 on the available Ada GPU can establish at most one complete hardware
generation. Goal5842 still requires an exact replay on a distinct NVIDIA GPU
architecture generation and UUID before cross-generation evidence can pass.
Raw timing ratios across machines remain forbidden. External review is deferred
while traveling. No public speedup, CGO-ready result, or consensus wording is
authorized by this plan.
