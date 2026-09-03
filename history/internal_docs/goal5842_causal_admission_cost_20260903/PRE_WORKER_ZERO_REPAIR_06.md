# Goal5842 V8 pre-worker-zero failure and V9 design correction

## Status

Goal5842 V8 did not reach worker zero and produced no registered timing. The
failed transaction is preserved at
`pod_artifacts/goal5842_v8_preworker_failure.tar.gz`: 3,346 bytes, SHA-256
`b6a70ec90b40d13269d3b9301c23cb86335c52a2ea34572a6909555362394234`.
It came from source commit
`adb32fbb05e808cb50e2f7ee48e7f7aae4f854ad` on the bound Ada GPU.

The archived execution authority has internal seal
`7a1646533562b9a4f166668d81519723eeb483a272308e21d916cc7b932f43f9`
and file SHA-256
`ee6738ab7e42bb7b8fd791442e87a29ef46053cddce076ca68a0ac3185b432fa`.
The failure marker, command, stdout, and stderr SHA-256 values are respectively
`71222136e24031c38abfdec3ff4d276187b25b7eb3cacb701b630e05162ae4c6`,
`cab7f10b70fc79a6b4447a3d7450cac5f8fb9af04d8a44a4640717d929a0c7e7`,
`527389b531cccfee4e65e0769a7134c6135608a9f8fa8ac6c5ddae28455d022f`,
and
`2af711b9a710f3d3484dfef9a809c1f5f82b3900e17b0f6b62e3ececec340293`.

## Exact failure

V8 completed all 72 relation CHECK_ON calls, all 72 relation CHECK_OFF calls,
and the first triangle CHECK_ON call. It therefore performed 145 untimed
complete GPU executions before failing. The generic public result type exposes
the checked weighted scalar but no `details` attribute. The V8 witness tried to
read `result.details["per_ray_u64"]` and raised `AttributeError`.

This is not a provider failure and not an application-correctness result. It is
a witness contract error. The 145 calls are not pooled into any V9 estimator.

## Measurement-contract audit

The failure exposed a second, methodologically material issue. The V8 baseline
timed experimental oracle work asymmetrically:

- the RTDL generic front door returned and checked only its public weighted
  scalar;
- Direct downloaded and scanned the auxiliary per-ray vector inside its timed
  call;
- PyOptiX downloaded and checked that vector inside its timed call and then
  checked it again in the Goal5842 worker.

All three implementations perform the same ray task, but these registered
intervals did not represent the same public output contract. Running V8 after
only deleting the invalid attribute access would preserve an unfair baseline.

## V9 correction

V9 is an append-only new fair-baseline design, not a retry and not a strict V8
replication. It preserves task values, the causal estimand, schedules, block
counts, statistics, and two-generation hardware gate. It changes only witness
and baseline measurement contracts:

1. Generic RTDL CHECK_ON/CHECK_OFF calls validate the actual public output.
2. A separate untimed fixed-protocol RTDL call validates the triangle per-ray
   vector plus weighted scalar.
3. Existing untimed PyOptiX calls continue to validate full outputs.
4. A new Direct mode executes both tasks with full outputs and no witness-path
   clock calls before worker zero.
5. Every registered baseline interval ends when the implementation's public
   result is materialized. Experimental expected-output comparison occurs
   immediately afterward and outside the interval.
6. The triangle timed contract is the checked weighted scalar for all arms.
   Direct and PyOptiX do not copy the auxiliary per-ray vector to the host in
   that timed mode. RTDL retains its current internal per-ray materialization
   and host reduction as real implementation cost.

Prior V4/V5 partial timing was available before this correction. The correction
is source-contract motivated, has no post-hoc success threshold, and pools no
prior row. This disclosure is mandatory in every Goal5842 report.

## Claim boundary

V8 is a pre-worker-zero engineering failure. V9 may produce at most one
independently recounted hardware-generation result on the current pod. Goal5842
and any CGO performance statement remain incomplete until the exact V9 commit
is replayed on a second GPU architecture generation and the cross-generation
gate passes. External review remains deferred by the owner.
