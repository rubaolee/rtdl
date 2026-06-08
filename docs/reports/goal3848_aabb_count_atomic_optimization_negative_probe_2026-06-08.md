# Goal3848: AABB Count Atomic Optimization Negative Probe

Date: 2026-06-08

Status: reverted; negative probe preserved

## Purpose

Goal3846 identified the generic OptiX `AABB_INDEX_QUERY_2D` count path as a
real large-scale performance target for the LibRTS-style benchmark. At dense
scale the current count-only implementation uses one global
`atomicAdd(params.hit_count, 1ULL)` per accepted hit. That is correct, but the
131k stress probe shows it can become seconds-level hot work:

- baseline counts: `point_contains=743946470`,
  `range_contains=520904982`, `range_intersects=1133035386`;
- baseline `repeat_protocol.query_sec_median`: `0.6460927510634065`;
- baseline `repeat_protocol.query_sec_total`: `6.463141920976341`.

Goal3848 tested whether the global hot counter could be replaced by a cheaper
per-ray count path.

## What Was Tried

Two generic alternatives were implemented and tested on the A5000 pod:

1. Payload-local accumulation: use an OptiX payload register as a per-ray hit
   accumulator and aggregate once after traversal.
2. Distributed per-ray device counters: write accepted hits into
   `query_hit_counts[payload_idx]` either from any-hit or directly from the
   custom intersection program, then sum the compact per-ray array.

Both variants were fast but wrong. On the same 131k fixture they returned:

- `point_contains=107557`
- `range_contains=11870`
- `range_intersects=428116`

Those values are first-hit-like and do not match the known-correct Goal3846
baseline counts. The optimization was therefore rejected.

## Current State

The native source is restored to the known-correct count path:

- `__intersection__aabb_index_exact` reports exact intersections;
- `__anyhit__aabb_index_count` reserves count/row slots with
  `atomicAdd(params.hit_count, 1ULL)`;
- the AABB pipeline uses one payload register;
- row collection and count-only paths remain semantically aligned.

No public speedup, release, or RT-core broad-claim wording is authorized by
this negative probe.

## Lesson

For this custom AABB traversal, merely replacing the global count atomic with a
per-ray accumulator changes semantics. The engine needs a stronger generic
design before this row can be accelerated further, such as:

- a verified count-only traversal variant that enumerates all exact accepted
  primitive/query pairs without row-slot atomics;
- a bounded row-stream plus device-resident grouped continuation that can count
  rows after traversal without materializing host rows;
- or a new RTSpatial-style generic primitive for high-density AABB join/count
  workloads, with CPU parity and large-scale pod validation.

This is a major primitive/runtime design problem, not a LibRTS-specific native
customization request.

