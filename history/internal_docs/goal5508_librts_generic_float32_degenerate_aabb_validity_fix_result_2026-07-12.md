# Goal5508: Generic float32-degenerate AABB validity fix

## Status

`implemented__generic_native_validity_fix__two_official_prefixes_matched__review_pending`

## Problem

Goal5507 matched the audited author contract on bounded and 8,192-pair probes,
but two larger official-archive prefixes still disagreed:

```text
parks_Europe: author 34,240,217; pre-fix RTDL 34,240,244; delta +27
lakes_bz2:    author 34,581,812; pre-fix RTDL 34,586,817; delta +5,005
```

The author and RTDL parsers produced identical float32 MBR fingerprints for
the same four input files. Queue capacity, counter overflow, and repeated
author execution were also ruled out.

## Root cause

The author uses `coord_t=float` and `Envelope::IsValid()` with strict
`min < max`. Its backward range-intersection raygen skips invalid indexed
envelopes. Four geometry records in each official prefix become zero-width or
zero-height after the actual float32 conversion:

```text
parks_Europe: 4 invalid indexed AABBs
lakes_bz2:    4 invalid indexed AABBs
```

RTDL packed the same float32 values, but its generic OptiX GAS padding could
make those records traversable. The RTDL intersection kernel did not reject
the post-pack invalid indexed record. A four-record-only probe reproduced the
entire disagreement: RTDL returned `27` and `5,005`, while the author subset
returned `0` and `0`.

## Generic fix

`src/native/optix/rtdl_optix_workloads.cpp` now checks strict float32 indexed
AABB validity inside the generic OptiX intersection kernel:

```text
min_x < max_x && min_y < max_y
```

The indexed record is selected correctly for both passes: `prim` in the
forward pass and the payload indexed source `qidx` in the backward pass.
Invalid indexed records fail closed before the operation-specific predicate.
No LibRTS, RTSpatial, paper, or author identity was added to RTDL core.

## POD evidence

POD: `157.157.221.29:25039`, NVIDIA RTX 4000 Ada Generation, CUDA 12.8,
clean build directory `build5508degenerate2`.

```text
parks_Europe: author 34,240,217; fixed RTDL 34,240,217; delta 0
lakes_bz2:    author 34,581,812; fixed RTDL 34,581,812; delta 0
```

The isolated degenerate subsets also match:

```text
parks_Europe: author 0; fixed RTDL 0
lakes_bz2:    author 0; fixed RTDL 0
```

Binary and source hashes, input hashes, invalid record indices, and all claim
flags are recorded in:

`Paper-reproduction-apps/librts-paper/results/goal5508_generic_float32_degenerate_aabb_validity_fix_gate.json`

## What this proves

- The two previously disagreeing official prefixes now match the pinned author
  count under the same input files.
- The count differences were caused by a generic native float32 validity gap,
  not by WKT parsing, queue capacity, or an app-specific comparator.
- The fix is pass-correct and fail-closed for indexed records in the generic
  OptiX AABB intersection kernel.

## What this does not prove

- It does not complete the 42-pair official range-intersects archive matrix.
- It does not prove pair-row equality for the official prefixes.
- It does not reproduce a paper figure or establish a performance ratio.
- It does not authorize author-specific behavior, native performance parity, or
  Embree work.

## Verification

Focused Goal5508 tests pass locally. The previous Goal5503-5507 regression
suite remains the required neighboring regression set.
