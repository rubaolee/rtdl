# Goal5845 bounded-relation public-path performance report

## Decision

Goal5845 is internally complete at exactly
`PASS__GOAL5845_RELATION_PUBLIC_STEADY_PERFORMANCE_DEBT_CLOSED__EXTERNAL_REVIEW_PENDING`.
For the frozen 4,096-by-4,096 custom-AABB closed-relation task returning 4,096
canonical `(source_id, indexed_id)` rows, the ordinary prepared RTDL public
path measured 366.340 us and the pinned PyOptiX compatible-API path measured
3,486.126 us. The preregistered median within-block RTDL/PyOptiX ratio was
`0.1049444491x`, or `9.5289x` in the reciprocal direction. All eight blocks
passed; the worst RTDL/PyOptiX block ratio was `0.1073019810x`.

This closes the exact prepared steady row-returning performance debt exposed by
Goal5843. It does not establish cold-start parity, a best-possible PyOptiX
lower bound, arbitrary relation workloads, cross-hardware generality, a public
paper claim, external review, or consensus.

## Why this work was necessary

Goal5843 retained an adverse relation result: the then-current RTDL public
row path measured 12.774231 ms on RTX A6000, `3.332872x` its pinned PyOptiX
arm and `9.950x` Direct. That evidence remains immutable and is not pooled with
Goal5845. It showed that the language/runtime path could erase the benefit of
the native RT operation through redundant host work. A language intended to
make RT cores easier to use cannot defend that cost as an abstraction tax.

Profiling found that ordinary execution paid for forensic work intended for an
explicit diagnostic path:

1. Native v3 materialized per-launch role/status rows and seven counters.
2. Python unpacked, sorted, deduplicated, repacked, and rehashed relation rows.
3. Owner, protocol, family bridge, and public family layers repeatedly copied
   or canonicalized the same immutable output and proof objects.
4. Callback-output digests and generic envelope identities were recomputed even
   when exact prepared inputs and canonical bytes were unchanged.

These costs did not add an independent correctness fact to each steady call.

## Repair

The repair is generic and application-neutral.

- Native ABI
  `rtdl_optix_v4_execute_prepared_bounded_relation_callback_v8` executes the
  existing two-pass relation traversal and emits an integrated compact
  traversal stamp in the same call.
- Canonicalization sorts and uniques directly in the persistent pinned host
  output buffer. It returns canonical packed `u32` pairs once instead of
  copying through another native vector and then rebuilding the relation in
  Python.
- The ordinary path validates a fixed 128-byte operation receipt, a 28-byte
  compact control record, the exact output bytes, source generation/reuse,
  device compaction, upload/build counts, and both real OptiX launches.
- The Python owner admits only a factory-created immutable
  `ValidatedBoundedRelationRows` object bound to the exact packed-byte digest.
  Unchanged output bytes reuse that object; changed bytes are decoded and
  validated again.
- Protocol and family layers use the fast branch only for the exact validated
  internal row and receipt types. Plain mappings and external providers retain
  the strict generic envelope path.
- `include_diagnostics=True` preserves the full v3 status/counter path. The
  ordinary result explicitly states that raw rows were not materialized.

No database, collision, graph, or benchmark-app name or predicate was added to
the engine. The native concept is only a bounded canonical binary relation;
application predicate encoding stays outside the engine.

## Frozen experiment

The preregistration was committed before the formal GPU transaction. Both arms
used:

- task `CUSTOM_AABB_CLOSED_RELATION_COUNT_V1`;
- input SHA-256
  `8606dd3c22d424a7ee2d64b61918f6185d39d8090d1a0a64001de65054d25e0e`;
- output SHA-256
  `2fb668490480cbb5d4d9bbf5a8d357435eff5fc6bb3532427ac2726cdaa88c77`;
- 4,096 indexed boxes, 4,096 source boxes, and 4,096 canonical public rows;
- two actual OptiX launches per execution;
- one RTX 2000 Ada Generation GPU, compute capability 8.9, driver 580.159.04;
- OptiX 9.0.0 headers and CUDA 12.8.93;
- fresh process per arm/block, 16 warmups, and 128 retained samples;
- eight balanced alternating-order blocks and 1,024 samples per arm;
- zero discarded samples.

The RTDL arm used a clean source checkout at commit
`22c6a45020e3da6894fa108fe92d50fbd2c5aa27`, tree
`d3efda68c1a1b7f70c6538e9f97daf73b3648731`, and fresh DSO SHA-256
`2383cc988ca7b5c99112c1b360a1c36380de88e750959fb4b17d9012d4e8efb8`.
The PyOptiX source was pinned to commit
`3144f224c0fd18733925faf3d8fb82c7376b8dcf`, tree
`0bf0ec24efb4a43f129aee25dd265aa8149374e3`.

Two setup refusals occurred before timing: the first omitted the explicit
single-device environment value, and the second supplied SDK string `9.0`
instead of manifest-exact `9.0.0`. Neither created a worker or timing sample.
They are recorded in `POD_TRANSACTION.json` and are not scientific attempts.

## Results

| Metric | RTDL | Pinned PyOptiX | RTDL/PyOptiX |
|---|---:|---:|---:|
| Pooled public median | 366.340 us | 3,486.126 us | 0.1051x |
| Primary median of 8 block ratios | - | - | 0.104944x |
| Worst block | 373.940 us | 3,484.931 us | 0.107302x |
| Public samples | 1,024 | 1,024 | - |
| Canonical rows per call | 4,096 | 4,096 | exact match |

The reciprocal of the primary ratio is `9.5289x`. Derived canonical-row
throughput is approximately 11.18 million rows/s for RTDL and 1.175 million
rows/s for this pinned PyOptiX arm. These rates describe only this fixed
prepared task.

| Block | Order first | RTDL us | PyOptiX us | RTDL/PyOptiX |
|---:|---|---:|---:|---:|
| 0 | RTDL | 365.170 | 3,484.995 | 0.104784x |
| 1 | PyOptiX | 367.335 | 3,485.191 | 0.105399x |
| 2 | RTDL | 365.845 | 3,515.896 | 0.104055x |
| 3 | PyOptiX | 363.070 | 3,468.611 | 0.104673x |
| 4 | RTDL | 364.835 | 3,471.135 | 0.105105x |
| 5 | PyOptiX | 365.965 | 3,466.500 | 0.105572x |
| 6 | RTDL | 373.940 | 3,484.931 | 0.107302x |
| 7 | PyOptiX | 365.560 | 3,497.031 | 0.104534x |

Order does not explain the result. All RTDL-first and PyOptiX-first blocks are
within the narrow `0.104055x` to `0.107302x` interval.

## RTDL attribution

RTDL retained 512 samples for each internal layer:

| Layer | Pooled median |
|---|---:|
| Direct native v8 | 274.997 us |
| Prepared owner | 333.194 us |
| Protocol lifecycle | 347.750 us |
| Family bridge | 353.444 us |
| Ordinary public family path | 366.340 us |

The median block-level public/direct ratio is `1.329106x`, below the frozen
`1.75x` gate. Therefore the public checks remain measurable but no longer
dominate the operation.

The explicit full-diagnostic path had an eight-worker median of 9.259284 ms,
`25.28x` the ordinary public median. It is a non-primary attribution, not a
formal comparison arm. It confirms that forensic row/counter expansion belongs
behind an explicit diagnostic request rather than in every steady call.

## Why RTDL beats this PyOptiX arm

The result is not evidence that Python bindings make OptiX intrinsically slow.
Both arms execute two OptiX traversals and return the same canonical relation,
but their continuation strategies differ:

- RTDL performs generic semantic sort/unique compaction before the single
  32,768-byte canonical output transfer.
- The pinned PyOptiX compatible-API arm receives 8,192 raw hit events, transfers
  them to the host, converts them to Python rows, and performs `sorted(set(...))`
  to produce the 4,096-row public result.

That difference is the contribution under test: RTDL packages a reusable,
validated, device-assisted relation continuation so users do not have to build
it manually. A separately optimized PyOptiX application could add its own
device compaction and narrow the gap. Therefore the defensible statement is
that RTDL incurs no material steady penalty and outperforms this pinned public
PyOptiX implementation on the exact contract, not that RTDL is universally
9.53x faster than PyOptiX.

## Cold/setup cost remains

Goal5845 preregistered prepared steady execution, not cold start. Median RTDL
setup components were approximately 108.6 ms route declaration, 99.9 ms
generic admission, 579.8 ms materialization, and 1,078.1 ms native prepare.
One first materialization paid a 33.98 s cold compilation/cache-fill cost.
Median PyOptiX setup components were approximately 342.2 ms device compile,
147.0 ms pipeline creation, and 30.2 ms prepare.

Consequently this report does not claim cold-start parity. Persisted artifact
and prepared-target reuse across processes is the next performance target if
cold or low-reuse workloads are part of the paper claim. Hiding setup outside
the steady timer would be misleading; separating it is valid only because the
evaluated contract is explicitly prepared/reused execution.

## Verification and evidence

- Both one-sample preflight arms passed and were excluded from estimators.
- All 16 formal workers passed and share one exact output hash.
- All 2,048 registered public samples are retained.
- Every RTDL worker records two successful OptiX launches, 8,192 raygen
  invocations, no launch/status error, device semantic compaction, one output
  transfer, zero reused-source uploads/builds, and no ordinary role counters.
- Eight independent RTDL worker nonces were observed.
- Post-formal pod regression: 55/55 tests pass.
- Combined local Goal5845/adjacent lifecycle regression: 126 passes and three
  intentional skips (129 discovered tests).
- The dedicated downloaded-authority suite passes 11/11 tests, including six
  hostile substitution/overclaim cases.
- The clean source status and post-capture compute-process list are empty.
- The downloaded standard-library-only authority builder rechecks Git blobs,
  build/source identities, all worker and receipt seals, native stamp mixes,
  timing summaries, block ratios, gates, and claim boundaries.
- Mutation tests reject changed worker samples, native stamp mixes, fast-path
  overclaims, public-claim changes, source substitutions, and missing ABI
  symbol evidence.

The controlling authority is `GOAL5845_INTERNAL_AUTHORITY.json`. Its internal
seal is `49827211b3b721fd7c893c15386c32b9fe701362258e7b168e64072807466e6a`.
Rebuild it with:

```bash
python3 scripts/goal5845_build_relation_public_parity_authority.py --verify-stored
```

Generated DSOs are not committed. The retained build manifest binds the exact
DSO hash, toolchain, source commit, source-file blobs, and build command; the
post-formal symbol record binds the required v8 name. This is reproducible
source/build custody, not preservation of the binary itself.

## Claim boundary and next gate

This is internal exact-task evidence only. External review count is zero, and
no public/manuscript claim or consensus is authorized. The next gates are:

1. Independent external review when the travel constraint is lifted.
2. A separately preregistered second-GPU-generation replication if the paper
   needs a hardware-general statement.
3. A separately scoped cold/persisted-artifact evaluation if the paper claims
   low-reuse or first-call performance.

Goal5843 remains preserved adverse history. Goal5845 does not rewrite it; it
demonstrates that its relation overhead was an implementation defect that can
be removed while retaining the public validation boundary.
