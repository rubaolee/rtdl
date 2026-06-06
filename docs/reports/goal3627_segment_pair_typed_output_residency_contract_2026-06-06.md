# Goal3627 - Segment-Pair Typed Output Residency Contract

Date: 2026-06-06

Status: internal next-version residency-contract step. This does not authorize release, public speedup wording, RTDL-beats-RayJoin wording, RayJoin paper reproduction, broad RT-core speedup, true zero-copy, automatic partner selection, or app-specific native engine logic.

## Purpose

Goal3625 made the segment-pair predicate executable and discoverable. Goal3627 makes the next residency target concrete without adding a new memory system.

The new helper:

`segment_pair_left_id_dense_count_output_residency_contract(...)`

reuses the existing generic primitive payload descriptor and neutral-buffer seam machinery to describe three typed outputs for a dense left-id count path:

| Column | dtype | Role |
| --- | --- | --- |
| `segment_pair_left_id_counts` | `int64[group_capacity]` | dense grouped count output |
| `segment_pair_overflow_status` | `uint32[1]` | fail-closed capacity status |
| `segment_pair_ambiguous_count` | `uint64[1]` | ambiguity/fallback telemetry |

## Design Decision

Do not invent a second residency seam.

The segment-pair output plan delegates per-column ownership, transfer, stream ordering, and zero-copy claim checks to `RtdlPrimitivePayloadColumnDescriptor` and the neutral-buffer seam. That preserves the next-version direction from Goal3619/3622:

- typed primitive outputs first;
- user-chosen partners;
- no automatic partner default;
- no true-zero-copy claim without measured pointer/no-host-stage/stream-order evidence;
- no public speedup wording from metadata.

## Current Behaviors

When device pointers are supplied, the contract records:

- CUDA device-resident descriptors;
- native producer;
- producer-retained lifetime;
- borrowed device pointer, unmeasured transfer status;
- no fallback required;
- true-zero-copy still unauthorized.

When pointers are not supplied, the contract records:

- host reference descriptors;
- explicit fallback required;
- host materialization before handoff;
- true-zero-copy still unauthorized.

## Why Ambiguity Count Is First-Class

The segment-pair predicate has known excluded or ambiguous cases:

- parallel pairs;
- collinear overlap;
- near-parallel pairs below the denominator threshold;
- degenerate zero-length segments;
- non-finite coordinates.

A fast device-resident count path needs an ambiguity/status channel before it can become a public primitive. Without that channel, the runtime cannot fail closed or choose a host/double refinement fallback when the fast predicate is outside its contract.

## Validation

The focused Goal3627 test checks:

- the device-resident descriptor path with fake CUDA pointers;
- the host-reference fallback path;
- all three required columns;
- neutral-buffer seam metadata on each column;
- false release/public-speedup/true-zero-copy authorization flags;
- compatibility with the Goal3625 predicate contract.

## Boundary

This is a residency-contract target and machine-checkable metadata path. It does not prove a pod-executed device-resident implementation, does not prove true zero-copy, and does not authorize public claims.
