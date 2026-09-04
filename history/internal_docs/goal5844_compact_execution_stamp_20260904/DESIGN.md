# Goal5844: compact execution stamp for the public steady path

Date: 2026-09-04

Status: `READY_FOR_GPU_BUILD_AND_ENGINEERING_COMPARISON__NO_PERFORMANCE_CLAIM`

## Current implementation status

The source-level implementation is complete and locally validated. The native
v8 entry point, compact receipt, lazy fast-operation receipt, prepared query
pointer reuse, fixed ctypes scratch storage, forensic expansion, and balanced
RTDL/PyOptiX engineering runner now exist. The Goal5838 frozen generic core and
`rtdl_optix_core.cpp` remain byte-identical.

This is not a performance-complete status. The current native source has not
yet been built or executed on a live NVIDIA host, and no Goal5844 timing result
exists.

## Purpose

Reduce the ordinary public RTDL triangle-scalar steady-execution overhead
relative to the pinned PyOptiX-compatible baseline without removing semantic
admission, fail-closed device status, exact prepared-input reuse, or physical
OptiX traversal evidence.

Goal5843 remains an immutable accepted baseline. Goal5844 is a successor
engineering transaction and must not rewrite or pool Goal5843 rows.

## Evidence-based hypothesis

The same-GPU Goal5842R1 layer diagnostic measured these nonformal medians:

| Layer | Median (ms) | Increment (ms) |
| --- | ---: | ---: |
| Native v7 reused-input scalar | 0.0663465 | baseline |
| Provider owner without audit | 0.1433230 | 0.0769765 |
| Provider owner with audit | 0.2355695 | 0.0922465 |
| Ordinary public API | 0.2763450 | 0.0407755 |

Goal5843 later measured 0.148260 ms for pinned PyOptiX and 0.436590 ms for
public RTDL under a fresh blocked formal schedule. The layer diagnostic and
Goal5843 are separate transactions and their absolute values may not be
subtracted as formal causal evidence. They nevertheless identify the first
engineering target: per-execution audit and Python envelope construction, not
the OptiX traversal kernel.

## Frozen boundary

The following Goal5838 files must remain byte-identical:

- `src/rtdsl/v4_family_schema.py`
- `src/rtdsl/v4_generic_family_lifecycle.py`
- `src/rtdsl/v4_family.py`

Goal5844 may extend non-frozen provider, protocol, provenance, and native ABI
surfaces. If a future generic lifecycle successor is required, it must be a
new versioned module rather than a mutation of the frozen V1 evidence.

## Three-stage proof architecture

### 1. Prepare-time certificate

Validate and freeze invariant facts once:

- family plan, provider projection, Callback IR, and ABI identities;
- generated PTX and exact native-library identities;
- route identity and expected physical program-bundle identity;
- prepared token, process/thread ownership, immutable batch identity, and
  packed-query digest.

### 2. Execute-time compact stamp

Every execution must still produce and validate fresh dynamic facts:

- nonzero session nonce plus strictly increasing execution sequence;
- exactly one attempted and successful OptiX launch and zero failed launches;
- one complete traversable context, no incomplete context, and no pending
  context at completion;
- expected app-neutral program-bundle id and one nonzero traversable handle;
- expected raygen invocation count;
- native compact status, checked-U64 overflow status, output value, output
  digest, and prepared-input generation;
- exact provider, route, and static semantic certificate bindings.

The native v8 entry point begins and finishes traversal observation inside the
same host ABI call that performs the existing v7 operation. Python must not
perform separate audit begin/finish crossings for this path.

### 3. Explicit forensic expansion

The ordinary execution result carries a small, immutable, rehashable compact
receipt. Full forensic snapshot expansion is available through an explicit
lifecycle/audit read after execution. Optional forensic serialization is not
allowed to delay publication of an already validated scalar, but the compact
stamp itself must be validated before that scalar becomes public.

## Redundant work to remove

- Remove the separate steady `_native_query_cache_digest()` round trip. The
  execute call already compares the expected digest inside the native owner;
  its returned generation must match the locally frozen generation.
- Cache query column pointers and exact metadata binding after the first
  successful publication.
- Reuse fixed ctypes output/status/receipt storage under the existing
  nonreentrant prepared-owner lock.
- Precompute static semantic and route digests during prepare.
- Avoid rebuilding the full native snapshot mapping and hashing its JSON on
  every ordinary execution.
- Keep frozen generic-envelope checks intact; optimize the non-frozen objects
  and mappings those checks consume.

## Fail-closed requirements

- A native status error returns no public scalar.
- A digest or generation mismatch clears local reuse identity and fails.
- A wrong launch count, program bundle, traversable, raygen count, nonce,
  sequence, provider identity, route identity, or output binding fails before
  public result construction.
- A failed integrated audit is aborted and cannot leave an active audit
  session or reusable successor identity.
- Diagnostic execution remains available and unchanged.
- Do not combine status and scalar transfers in this first repair. The existing
  status-before-output boundary stays intact until measurement proves it is the
  next dominant cost and a separately reviewed contract permits change.

## Required local tests

- Compact receipt exact-schema, seal, and full-expansion equivalence tests.
- Mutation rejection for every dynamic field class.
- Strictly increasing sequence and wrong/replayed nonce rejection.
- Native v8 success, native-call failure, status failure, and audit cleanup
  behavior through a fake ABI.
- Exact reused-query path without the separate digest accessor.
- Changed batch, changed metadata, failed A-to-B transition, use-after-close,
  cross-thread/process, and reentrancy regressions.
- Existing Goal5842R1 and Goal5843 successor suites remain green.
- Frozen Goal5838 hashes remain exact.

## GPU engineering gate

Use the same task, public output, prepared regime, and pinned PyOptiX baseline
as Goal5843. Measure instrumented subphases first. Then run fresh balanced
within-block RTDL/PyOptiX comparisons on one GPU.

The engineering target is a steady RTDL/PyOptiX median ratio of at most 1.25.
The desired endpoint is near 1.0. If the ratio remains above 1.25, Goal5844 is
not closed as a performance repair: retain the adverse rows, identify the next
largest measured subphase, and continue. This target does not authorize a
public or manuscript claim.

## Claim ceiling

Until fresh GPU evidence and deferred external review exist, Goal5844 supports
only source-level implementation and local correctness statements. It does not
authorize performance success, PyOptiX parity, general language overhead,
hardware independence, public wording, manuscript wording, or consensus.
