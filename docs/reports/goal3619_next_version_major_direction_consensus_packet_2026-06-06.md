# Goal3619 - Next-Version Major Direction Consensus Packet

Date: 2026-06-06

Status: Codex proposal for external review. This packet authorizes nothing: not a release, not a release tag, not public speedup wording, not RTDL-beats-RayJoin, not broad RT-core speedup, not true zero-copy, not automatic partner selection, and not app-specific native engine logic.

## Purpose

The current v2.9 RayJoin repair and route work produced one large internal win: the repaired mixed public-CDB route reaches `188.997x` over the all-CuPy same-contract hot-path sum on the measured `start=256,count=4096` slice, with a second public-CDB slice at `163.650x`.

That is enough signal for this version. Unless a proposed tuning task has a clear chance of a large material improvement or fixes a correctness/contract hole, the project should stop spending time on more incremental performance rounds for the current version.

This packet proposes the major work direction for the next version and asks Claude and Gemini to review it before the team commits to that direction.

## Codex Recommendation

The next version should be **contract-and-residency first**, not another app-specific tuning sprint and not shader-injection first.

The core thesis:

1. RTDL should remain a generic, app-agnostic engine with high-performance primitive contracts.
2. Users may choose any supported partner for custom logic; RTDL should provide high-performance support and honest evidence for supported partners, not automatic partner selection.
3. Benchmark apps should keep serving as pressure tests that reveal missing generic primitives, contract gaps, and data-residency bottlenecks.
4. Small tuning rounds should stop unless they are likely to produce a large end-to-end gain, close a correctness mismatch, or unlock a reusable primitive/runtime capability.
5. The next durable performance lever is device-resident typed primitive output plus explicit primitive contracts and conformance, not ad hoc per-app native logic.

## What Current Evidence Says

### Current RayJoin Position

The current internal RayJoin route after Goal3613/Goal3616 is:

- PIP scalar count: CuPy dense CUDA-core count.
- LSI count: repaired RTDL/OptiX left-id dense count with strict segment predicate.
- Overlay active-count: RTDL/OptiX prepared shape-pair active count.

For `start=256,count=4096`, the internal mixed route gives:

| All-CuPy Sum Median Sec | Mixed Sum Median Sec | Speedup | Counts Match |
| ---: | ---: | ---: | --- |
| `1.436104300` | `0.007598563` | `188.997x` | true |

For `start=0,count=4096`, the diversity probe gives:

| All-CuPy Sum Median Sec | Mixed Sum Median Sec | Speedup | Counts Match |
| ---: | ---: | ---: | --- |
| `1.623656120` | `0.009923336` | `163.650x` | true |

These are internal same-contract benchmark numbers, not public claims.

### What This Does Not Yet Prove

The current evidence does not prove:

- RayJoin paper reproduction.
- RTDL beats the original RayJoin implementation.
- broad RT-core speedup across apps.
- true zero-copy.
- a published segment-pair count contract for all degeneracies.
- a default native route for every RayJoin row.

Goal3618 records the immediate contract gap: the segment-pair count primitive still needs adversarial conformance for endpoint, near-parallel, collinear, tiny-segment, and threshold-policy cases before public wording.

## Proposed Next-Version Pillars

### Pillar 1 - Formal Primitive Contracts

Turn benchmark-specific repairs into published, generic primitive contracts only after adversarial tests exist.

First target:

- `segment_pair_intersection_count`
- `segment_pair_left_id_dense_count`
- `segment_pair_intersection_rows`

Required before public contract wording:

- adversarial geometry fixtures;
- explicit collinear-overlap decision;
- endpoint and near-zero-length policy;
- absolute vs scale-aware threshold policy;
- cross-route conformance across CuPy, OptiX fast device count, and OptiX host-refined count;
- explicit ambiguity telemetry or fallback rule if fast float-side counting cannot cover all cases.

### Pillar 2 - Device-Resident Typed Primitive Outputs

The next durable runtime work is to keep primitive outputs resident on device when downstream work can consume them there.

This should focus on typed primitive outputs, status/ambiguity columns, and bounded continuation inputs that can be consumed by supported partners or by native fused reductions without unnecessary host materialization.

This is not a true-zero-copy claim until measured and reviewed. It is a design target: no data movement unless the contract requires it.

### Pillar 3 - Benchmark-Driven Runtime Extensions

Use benchmark apps to force generic runtime improvements, not app-shaped native logic.

Recommended next benchmark pressure points:

| Benchmark family | Why it belongs in the next version |
| --- | --- |
| RayJoin | Segment-pair and closed-shape contracts expose primitive semantics and degeneracy policies. |
| RayDB or RT-DBSCAN | Materialization and grouped continuation expose residency bottlenecks. |
| Hausdorff / RTNN | Nearest-neighbor summaries expose witness/tie-break/determinism contracts. |

Each benchmark task should state the generic primitive/runtime capability it is adding before implementation begins.

### Pillar 4 - Partner Freedom, Not Partner Defaulting

The user chooses the partner. RTDL provides:

- generic primitive outputs;
- partner-compatible handoff contracts;
- reference benchmark implementations;
- measured support matrices;
- honest claim boundaries.

RTDL should not auto-select Triton, CuPy, Numba, Torch, or any other partner as a public default. Benchmark reference implementations may recommend a partner for a measured route, but that is evidence, not a language restriction.

### Pillar 5 - Claim Governance

No public release or public speedup claim should be made from this packet.

Future public wording requires:

- exact contract names;
- exact backend/partner route;
- exact dataset or input family;
- same-contract baseline;
- phase-separated timing;
- correctness evidence;
- external review;
- the required 3-AI consensus for roadmap/release/public-claim decisions.

## Stop/Continue Rule For Performance Work

For the next version, performance work should continue only when at least one is true:

1. It fixes a correctness mismatch or ambiguous primitive contract.
2. It has a credible path to a large material end-to-end improvement, not only a small kernel-only win.
3. It creates a reusable generic primitive/runtime capability.
4. It produces missing same-contract evidence required for a release or claim boundary.

Otherwise, stop the tuning loop and move to contract, residency, documentation, or external review.

## Questions For External Review

1. Do you accept the Codex recommendation that the next version should be contract-and-residency first?
2. Do you agree that more current-version tuning should stop unless it satisfies the stop/continue rule above?
3. Do you agree that shader injection should remain parked behind device-resident typed outputs and primitive contracts?
4. Are the proposed first contract targets (`segment_pair_*`) the right starting point?
5. Is the partner policy correct: user-chosen partners, measured support, no automatic public default?
6. What must be added or changed before this can become a 3-AI consensus direction?

## Codex Verdict

Codex verdict: `accept-with-boundary`.

Boundary: the direction is accepted as an internal next-version plan candidate, but it is not complete consensus until independent Claude and Gemini reviews are saved, read, and reconciled into a separate 3-AI consensus report.
