# Goal 80 Plan: Long End-to-End Runtime-Cache Win

Date: 2026-04-04
Status: complete

## Problem

The project already established that:

- Embree and OptiX beat PostGIS on the long `county_zipcode`
  `prepared_execution` boundary
- RTDL still loses on the accepted `end_to_end` boundary

That means the next gap is the runtime path around backend execution, not the
backend execution itself.

## Initial Optimization Hypothesis

The current runtime-owned cache still scales poorly on long repeated raw-input
calls because cache-key construction walks and normalizes every raw record.

For RTDL's own canonical frozen geometry tuples, that work is unnecessary.

The first Goal 80 optimization therefore is:

- identity-based cache keys for canonical RTDL geometry tuples
- no double-normalization on the cold bind path for canonical tuples

## Measurement Target

Measure repeated raw-input calls on Linux for:

- OptiX
- Embree

Using the long `county_zipcode` source path and the same positive-hit `pip`
kernel family used in Goals 69-71.

## Acceptance Rule

Publish only if:

- parity is exact
- the boundary is stated clearly
- the result is honest about whether the win is first-call end-to-end or
  repeated raw-input end-to-end

## Closure

Goal 80 closed on the repeated raw-input end-to-end boundary for OptiX on the
real top4 county/zipcode package.

- first run remained slower than PostGIS
- repeated raw-input reruns beat PostGIS
- parity stayed exact
