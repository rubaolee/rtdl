# RTDL V4.0 Section 8 Route D Protocol

Date: 2026-06-24
Status: focused ceiling-reference protocol; not a release claim

## Purpose

Section 8 already showed that RTDL's prepared `FIXED_RADIUS_COUNT_THRESHOLD_2D`
hot path can beat the separated row-materialization route on the measured
fixture. That does **not** prove "near hand-written OptiX" because the measured
route is still inside the RTDL runtime.

This protocol asks the missing Route D question:

> What is the independent hand-written OptiX ceiling for the same fixed-radius
> count-threshold contract, on the same fixture, same hardware, and comparable
> prepared hot-path boundary?

## Independence Contract

The Route D reference must satisfy all of these:

- no `import rtdsl`
- no link to `librtdl_optix.so`
- no call to any `rtdl_optix_*` symbol
- no RTDL Python app route in the measured path
- standalone CUDA Driver + OptiX host program
- own OptiX context, GAS, pipeline, SBT, launch params, and kernel source
- same generated outlier fixture as `make_outlier_case(copies=...)`

Copying the public contract and equivalent kernel logic is allowed. Calling the
RTDL runtime is not.

## Workload

The fixture is the current Section 8 outlier-density tiled point set:

- 8 base points per tile
- x tile offset: `7.0 * copy_index`
- id offset: `100 * copy_index`
- radius: `0.35`
- threshold: `3`

The expected threshold-reached count is `6 * copies`. The expected outlier count
is `2 * copies`.

## Routes

Route D must measure two output contracts:

### D1. Scalar threshold-count ceiling

The hand-written OptiX kernel returns only the scalar count of queries reaching
the threshold. This is the ceiling reference for the RTDL prepared scalar route.

### D2. Count-row ceiling

The hand-written OptiX kernel writes one `{query_id, neighbor_count,
threshold_reached}` row per query. This is the ceiling reference for compact
summary routes that still need per-query identity.

## Timing Boundary

Use prepared-session hot-path timing:

- included: host query packing/upload, launch params upload, OptiX launch,
  synchronization, and required result download
- excluded: fixture construction, OptiX context creation, module/pipeline build,
  search-point upload, and GAS build

This intentionally matches the current RTDL prepared hot-path boundary closely.

## Serious Sizes

- `copies=8192` -> 65,536 points
- `copies=32768` -> 262,144 points
- `copies=131072` -> 1,048,576 points

Smoke runs may use smaller sizes but cannot be used for claims.

## Repeats

For each serious size:

- warmup: 1 per measured mode
- measured repeats: 7
- report all raw timings, median, min, max

## Correctness Gate

Both D1 and D2 must pass:

- point count matches `copies * 8`
- scalar threshold-reached count equals `copies * 6`
- count-row threshold-reached count equals `copies * 6`
- count-row outlier count equals `copies * 2`

Any correctness mismatch kills Route D.

## Claim Boundary

Passing this protocol can authorize only a ceiling comparison for this exact
primitive, fixture, hardware, and timing boundary. It does not authorize:

- V4 release
- broad V4 speedup wording
- Tier-3 callback support claims
- app-specific native engine claims
- whole-call app-route claims

Near hand-written OptiX wording remains unauthorized until this Route D result is
externally reviewed and explicitly accepted.
