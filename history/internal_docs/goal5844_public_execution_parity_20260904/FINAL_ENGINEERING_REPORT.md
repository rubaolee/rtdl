# Goal5844 public execution parity engineering report

## Decision

Goal5844 is internally complete at
`PASS__GOAL5844_INTERNAL_ENGINEERING_TARGET_MET__EXTERNAL_REVIEW_PENDING`.
On one RTX 2000 Ada GPU, the exact clean successor commit reduced the steady
public triangle-scalar RTDL/PyOptiX median within-block ratio from 2.1714x to
1.0457x. The preregistered engineering threshold was at most 1.25x. All eight
successor blocks were below 1.25x; the worst was 1.1543x.

This is a scoped internal engineering result. It is not a formal paper
baseline, hardware-independent parity, a result for the row-returning relation
path, external review, or permission for public/manuscript wording.

## Question addressed

The Goal5843 public triangle scalar route was 2.910x slower than pinned PyOptiX
on RTX A6000. Goal5844 first moved physical audit collection into the same
native v8 execution call, but its first formal Ada transaction was still
2.1714x PyOptiX. The remaining question was whether RTDL's public safety and
provenance contract intrinsically required that cost, or whether the runtime
was redundantly reconstructing already validated facts.

## Experimental contract

Both arms execute the same triangle fixture, ray batch, expected checked-U64
scalar, prepared/reused lifecycle, OptiX API 9.0 headers, CUDA 12.8 toolkit, and
RTX 2000 Ada UUID. The pinned PyOptiX source is commit
`3144f224c0fd18733925faf3d8fb82c7376b8dcf`. Each transaction uses eight
alternating-order blocks. Every arm/block runs in a fresh process with 16
warmups and 128 retained public samples. RTDL additionally retains 64 samples
for every registered attribution layer. Setup, compilation, materialization,
prepare, close, and explicit full-forensic expansion are outside the public
steady timer and separately represented.

The successor was measured from a new create-only checkout of exact commit
`ee0237963bcd838d652a059f15ecc0d3f56dfd09`. It rebuilt the PyOptiX wheel and
RTDL native DSO inside a new isolated environment. Both untimed worker-zero
arms passed before the balanced run. The pod verifier and a downloaded Mac
verifier independently recomputed the result from hashed payloads.

## Results

| Metric | Attempt 1 adverse | Attempt 2 successor |
|---|---:|---:|
| RTDL public median | 273.457 us | 132.534 us |
| PyOptiX public median | 129.368 us | 131.744 us |
| Median within-block RTDL/PyOptiX | 2.1714x | 1.0457x |
| Minimum block ratio | 2.0406x | 0.9681x |
| Maximum block ratio | 2.3834x | 1.1543x |
| RTDL direct-native median | 82.757 us | 82.592 us |
| RTDL provider-owner median | 141.808 us | 109.543 us |
| Public samples per arm | 1,024 | 1,024 |

The successor public RTDL median improved by 2.0633x. PyOptiX changed by only
1.0184x, and direct-native RTDL changed by 0.9980x. The measured improvement is
therefore in RTDL's host protocol/envelope, not in a changed native traversal.

Order stratification does not explain the pass. Median RTDL/PyOptiX was
1.0456709697x in RTDL-first blocks and 1.0456883372x in PyOptiX-first blocks.
All samples are retained; no block or outlier was removed.

## Root cause

The native operation was already near the PyOptiX public time. RTDL then paid
for the same facts repeatedly across owner, protocol, bridge, and generic
public layers:

1. A fresh compact native stamp was expanded into a JSON-like dictionary.
2. Adjacent layers copied, canonicalized, sealed, decoded, and froze that same
   proof again.
3. Immutable executable and provider-projection dictionaries were serialized
   and hashed on every execution.
4. Stable program-bundle IDs, valid SHA strings, and repeated integer output
   digests were recomputed despite identical immutable inputs.

This was accidental repeated representation work. It was not required by the
language contract and did not provide an independent safety fact.

## Repair

`ValidatedCompactTraversalReceipt` is a factory-created Mapping that copies and
validates all native launch facts eagerly. Its transport dictionary and
self-digest are generated only when a caller inspects the mapping. The normal
public steady timer therefore includes physical validation but not optional
forensic serialization.

The protocol fast path is admitted only for the exact internal receipt type and
the triangle-reduction family. It checks provider digest, route, output digest,
program bundle, ray count, and expected bundle ID. Dynamic nonce, sequence,
launch counts, context counts, raygen count, traversable identity, error state,
and native mix values are still checked on every execution.

The internal scalar family bridge avoids a second JSON round trip only after
the protocol has validated the exact scalar and receipt. External providers,
ordinary mapping receipts, non-scalar outputs, and other families retain the
original strict envelope path.

Bounded memoization is used only for pure functions over immutable inputs:
canonical integer output digests, canonical SHA validity, physical
program-bundle IDs, and immutable executable/projection digests. Cache misses
produce the same canonical values and malformed values still fail closed.

## Architecture boundary

No triangle, geometry, or application dispatch was added to the native engine.
The native v8 ABI remains an app-neutral execution-plus-audit operation over an
existing checked reduction. The optimization changes representation and
lifecycle work after physical execution, not callback semantics, traversable
construction, or the OptiX workload.

One changed file, `src/rtdsl/v4_generic_family_lifecycle.py`, belonged to the
completed Goal5838 prospective frozen core. This change occurred only after the
exam and is a generic identity-memoization successor optimization. Goal5838's
exact preselection commit and seal remain immutable historical evidence. The
current tree must not be described as byte-identical to that old seal, and its
old current-file replay test is expected to reject this successor.

## Verification

- Goal5844 compact/provenance/harness tests: 34/34 pass locally before the
  successor transaction.
- Goal5838 generic lifecycle and route behavior tests: 51/51 pass.
- Goal5842 causal/cache tests: 55/55 pass.
- Combined current focused set: 128/128 pass.
- Focused pod transaction tests: pass before preflight.
- Both untimed real-GPU arms: pass and match the scalar oracle.
- Pod complete-result verification: pass.
- Downloaded Mac recomputation: pass.
- Stored two-attempt authority tests and exact rebuild: 8/8 pass, including
  four resealed/dropped/archive mutation cases.
- Combined current focused set after evidence integration: 136/136 pass.

A broader 440-test historical/adjacent run produced 401 passes, four skips,
35 missing-historical-artifact/environment errors, and four failures. Two of
the four failures are the explicitly superseded Goal5838 current-file identity
checks. The remaining failures/errors are old missing archive, environment, or
interpreter-identity refusals; they are not counted as successor passes and
were not repaired by fabricating historical artifacts.

## Evidence

The controlling internal authority is `GOAL5844_INTERNAL_AUTHORITY.json` in
this directory. It revalidates both formal attempts from stored worker JSON,
including all timing summaries and block ratios. Its current internal seal is
`3c44e95000a6d55d2036651bcd465f0f3a00da8309b329e6d39a46a1f558a90b`.

Attempt 1 summary seal:
`4d6548238849c49e7aa89dcb663f08febb2815d83da924dd3a083db5549a94d3`.
Attempt 2 summary seal:
`6229aeba61fa681cbcda37e0ca253f725269fe08c2dd5e85f91502e5ad0a3b03`.
Full archive SHA-256 values are retained, while generated native binaries are
not committed to Git.

## Remaining threats and next gate

The result covers one task, one GPU generation, one OS/toolchain transaction,
and steady prepared execution. It does not establish cold-start parity,
row-heavy relation parity, all callbacks, or all GPUs. Bounded memoization may
have different hit rates for workloads whose outputs or identities change on
every call; that requires separate workloads rather than extrapolation.

The immediate next gate is independent external review when available. A
second GPU-generation replication would strengthen a paper statement. The
row-returning bounded-relation path remains a separate major performance debt
and must not inherit this scalar result.
