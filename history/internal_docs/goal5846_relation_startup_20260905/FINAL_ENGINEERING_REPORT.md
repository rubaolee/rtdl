# Goal5846 bounded-relation startup performance report

## Decision

Goal5846 is internally complete at exactly
`PASS__GOAL5846_EXACT_WARM_CACHE_FRESH_PROCESS_STARTUP_TARGET_MET__EXTERNAL_REVIEW_PENDING`.
For the frozen 4,096-by-4,096 custom-AABB relation task returning 4,096
canonical `(source_id, item_id)` rows, the median of eight paired fresh-process
RTDL/PyOptiX setup-plus-first ratios is `0.990957x`. The median setup-plus-first
times are 577.153 ms for RTDL and 580.880 ms for the pinned PyOptiX
compatible-API arm. The worst paired block is `1.132343x`, all 2,048 registered
steady samples are retained, and both arms return the same output SHA-256.

This closes the exact warm-cache fresh-process setup debt against the inherited
source-compiling PyOptiX contract. It does not close first-ever compilation,
precompiled/AOT PyOptiX parity, arbitrary relation workloads, cross-hardware
generality, external review, or public/manuscript claims.

## Why this goal was necessary

Goal5845 closed the prepared steady relation deficit: its RTDL public path ran
in 366.340 us versus 3,486.126 us for the pinned PyOptiX arm. The same work also
showed that RTDL's setup path was not acceptable for low-reuse execution. A
first materialization could compile seven Numba leaves for tens of seconds,
and repeated processes reconstructed compiler state and initialized native
CUDA/OptiX state serially.

A language abstraction that is fast only after an unexplained setup cost is
not enough for the CGO argument. Goal5846 therefore treats setup as a measured
system path rather than dismissing it as Python or driver overhead.

## Root causes

Profiling separated the setup path into route declaration, generic admission,
materialization, native preparation, and first public execution. It found four
distinct costs:

1. Generated Numba leaves were reusable, but the complete verified executable
   was reconstructed in every process.
2. The family, ABI, contract, and compiler layers repeated validation after a
   trusted internal boundary had already established the same immutable facts.
3. CUDA primary-context retention and OptiX context creation were started only
   after CPU route/compiler work, serializing two independent setup paths.
4. Native preparation could query CUDA context state before the generic warm
   path had initialized it, exposing both latency and a real cold-order defect.

A native phase diagnostic attributed roughly 365 ms to CUDA/OptiX context
establishment on this pod, including about 209 ms for primary-context
retention/selection and 142 ms for OptiX device-context creation. Native
relation-specific preparation itself was about 36 ms in that diagnostic. These
numbers are unregistered attribution, not additional formal samples.

## Repair

The repair is generic and application-neutral.

- `v4_executable_cache.py` adds a content-addressed canonical-JSON cache for
  verified compiler executables. Cache identity binds the callback contract,
  ABI, proof, target, compiler and generated-source hashes, toolchain policy,
  compute capability, and native provider bytes. It never serializes a live
  handle, Python executable object, or capability.
- A manifest-bound cache policy is logical hit-only: missing or changed bytes
  fail closed and no cache write is allowed. Formal workers rehash complete
  cache snapshots before and after execution. This is not an OS file-permission
  claim; the retained pod files had mode `0666`.
- A factory-created one-shot verified executable handoff lets native prepare
  consume an already admitted immutable executable. It is process/thread bound,
  weak-reference tracked, mutation rechecked, atomically consumed, and cannot
  be replayed after use or revocation.
- Target-bound native initialization begins before CPU route declaration and
  generic admission. Native initialization uses a generic warm ABI and joins at
  prepare, so the actual dependency is preserved while independent CPU/GPU
  setup overlaps.
- The warm ABI calls `std::call_once(init_optix_context)` before querying the
  current CUDA context. This fixes the real cold-order failure rather than
  relying on an earlier incidental CUDA call.
- Duplicate validation was removed only across exact internal verified-token
  boundaries. Public mappings, external providers, mutated sources, cache
  misses, ABI mismatches, and untrusted inputs still take the strict path.
- Provider source hashes are re-read at each relevant use. An attempted global
  memoization was rejected during self-review because it could hide in-process
  file mutation.

No database, graph, collision, or benchmark-specific operation was added to
the engine. The native behavior remains a generic bounded canonical relation.

## Frozen experiment

The preregistration was committed before formal GPU execution. Both arms used:

- task `CUSTOM_AABB_CLOSED_RELATION_COUNT_V1`;
- input SHA-256
  `8606dd3c22d424a7ee2d64b61918f6185d39d8090d1a0a64001de65054d25e0e`;
- output SHA-256
  `2fb668490480cbb5d4d9bbf5a8d357435eff5fc6bb3532427ac2726cdaa88c77`;
- 4,096 indexed boxes, 4,096 source boxes, and 4,096 canonical rows;
- two real OptiX launches per execution;
- RTX 2000 Ada Generation, compute capability 8.9, driver 580.159.04;
- CUDA 12.8.93, OptiX 9.0.0, and Python 3.12.3;
- source commit `a6f395cc9411cbed3045c11145d92eda3bc2f502`, tree
  `19546ddeaee191de3e756cd1c14d979a8387fec7`;
- a fresh DSO of 7,191,992 bytes, SHA-256
  `c56343fad27b4084566febbafeddca19f89c04fc66a0b878ca94417b64d2163e`;
- pinned PyOptiX commit
  `3144f224c0fd18733925faf3d8fb82c7376b8dcf`, tree
  `0bf0ec24efb4a43f129aee25dd265aa8149374e3`;
- eight alternating-order blocks, a fresh process for every arm/block, 16
  steady warmups, 128 retained samples per worker, and zero discarded samples.

RTDL setup-plus-first includes starting native initialization, route
declaration, generic admission, loading/reconstructing the sealed executable,
native/static prepare including any join on initialization, and first public
execution. PyOptiX setup-plus-first includes source-to-PTX compilation,
pipeline construction, static prepare, and first execution. Post-hoc oracle and
expanded provenance checks are outside both timers; required public execution
checks remain in the RTDL path.

## Cache preparation

The first-ever empty-cache fill is preserved and excluded exactly as frozen:

| Phase | Time |
|---|---:|
| Route declaration | 79.507 ms |
| Generic admission | 23.160 ms |
| Materialize and compile | 36.880 s |
| Total | 36.982 s |
| Sealed hit-only replay | 127.639 ms |

The cache contains seven bound leaf artifacts and one complete executable
artifact. Every formal RTDL worker observed the same two manifest hashes and
the same before/after cache-byte snapshots.

## Formal results

| Metric | RTDL | Pinned PyOptiX | RTDL/PyOptiX |
|---|---:|---:|---:|
| Median setup plus first | 577.153 ms | 580.880 ms | descriptive 0.994x |
| Primary median of paired block ratios | - | - | 0.990957x |
| Worst paired block | 620.265 ms | 547.771 ms | 1.132343x |
| Pooled prepared steady median | 364.985 us | 3,487.496 us | 0.104655x |
| Registered steady samples | 1,024 | 1,024 | - |
| Canonical rows per call | 4,096 | 4,096 | exact match |

The reciprocal prepared-steady ratio is `9.555x` for this pinned arm. This is
consistent with Goal5845 and shows that the startup repair did not buy parity
by regressing the steady path.

| Block | First arm | RTDL ms | PyOptiX ms | RTDL/PyOptiX |
|---:|---|---:|---:|---:|
| 0 | RTDL | 578.416 | 573.168 | 1.009156x |
| 1 | PyOptiX | 620.265 | 547.771 | 1.132343x |
| 2 | RTDL | 617.955 | 572.666 | 1.079086x |
| 3 | PyOptiX | 565.669 | 581.511 | 0.972758x |
| 4 | RTDL | 613.787 | 580.249 | 1.057799x |
| 5 | PyOptiX | 575.890 | 602.044 | 0.956559x |
| 6 | RTDL | 574.182 | 606.503 | 0.946709x |
| 7 | PyOptiX | 555.890 | 616.761 | 0.901306x |

The RTDL-first stratum median is `1.033478x`; the PyOptiX-first stratum median
is `0.964658x`. This approximately seven-percent separation warns against a
claim that the observed 0.9-percent central advantage is meaningful. The
defensible result is parity within the preregistered bound, not an RTDL startup
speedup.

Median RTDL phase times across the eight workers were:

| Phase | Median |
|---|---:|
| Start native initialization | 11.295 ms |
| Route declaration | 59.439 ms |
| Generic admission | 19.692 ms |
| Materialize sealed executable | 144.662 ms |
| Native/static prepare and initialization join | 322.319 ms |
| First public execution | 24.883 ms |

Phase medians do not sum to the median total because they are independently
computed across workers.

## Adverse evidence and remaining debt

The strongest counterexample is intentionally retained. A diagnostic PyOptiX
arm loaded precompiled PTX and disabled debug validation; it observed about
236.415 ms setup-plus-first. Comparing that unregistered sensitivity with the
formal RTDL median gives approximately `2.44x`. It changes the deployment
contract and therefore is not pooled into the frozen primary estimator, but it
shows that generic whole-route AOT deployment remains a real performance goal.

Likewise, a first-ever cache fill of 36.982 s is unacceptable for one-shot
interactive use. Goal5846 amortizes that cost through content-addressed reuse;
it does not eliminate compilation itself. A deployable RTDL artifact should
eventually package the verified complete executable and compatible native
provider so a user does not perform this fill on first use.

Other residual limits are one sparse relation shape, one Ada GPU, no full
process-import timer, no best-possible custom PyOptiX device-compaction arm,
and no external review. The DSO bytes are not committed; Git retains its exact
hash, size, complete symbol listing, build manifest, toolchain identity, and
all source-blob hashes.

## Verification

- Formal controller: 16/16 workers passed, stderr empty.
- Exact public output: identical SHA-256 in all workers and both arms.
- Traversal: every RTDL worker has a valid compact receipt, two successful
  launches, 8,192 raygen invocations, expected program bundle, and a unique
  process nonce.
- Post-formal affected suite: 232/232 passed after fetching one historical
  commit absent from the pod's shallow clone.
- The first post-formal run is retained: 230 tests passed and two Goal5842
  history tests errored before assertions because the shallow clone lacked
  commit `04305fc...`; no source, DSO, or formal sample changed before rerun.
- Independent authority builder imports neither RTDL nor a GPU package and
  validates worker transport duplicates, source blobs, cache artifacts,
  manifests, native stamp arithmetic, statistics, gates, and claim ceilings.
- Mutation tests reject resealed worker substitution, traversal-stamp changes,
  cache-byte mutation, and missing native ABI records.

## Final boundary

The exact pinned warm-cache fresh-process startup penalty is removed without
an app-specific engine branch and without prepared-steady regression. This is
a meaningful performance-debt closure, not a universal result. The next
performance goal is generic deployable whole-route/AOT artifact loading against
the disclosed precompiled PyOptiX sensitivity. External review must occur
before any manuscript or public performance wording.
