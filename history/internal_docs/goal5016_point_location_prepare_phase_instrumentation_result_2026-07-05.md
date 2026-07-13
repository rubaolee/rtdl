# Goal5016 - Directed Point-Location Prepare Phase Instrumentation

Date: 2026-07-05

## Purpose

Goal5016 instruments the generic directed-segment / planar-map point-location
OptiX prepare path so the RayJoin binary operator no longer guesses why PIP
workspace construction is expensive.

This is measurement infrastructure only. It does not add a RayJoin-specific
kernel and does not change point-location semantics.

## Implementation

Changed files:

- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `tests/goal5016_point_location_prepare_timing_test.py`

Native additions:

- Added extended point-location prepare timing fields:
  - `prepare_total`
  - `prepare_pipeline_ensure`
  - `prepare_host_copy`
  - `prepare_segment_pack`
  - `prepare_duplicate_canonicalize`
  - `prepare_device_upload`
  - `prepare_range_build`
  - `prepare_range_upload`
  - `prepare_accel_build`
  - `prepare_segment_count`
  - `prepare_range_count`
- Added optional C ABI:
  - `rtdl_optix_rayjoin_cdb_point_location_get_last_extended_phase_timings`
  - `rtdl_optix_directed_segment_point_location_get_last_extended_phase_timings`

Python additions:

- `last_phase_timings()` now includes an `extended` prepare breakdown when the
  rebuilt native library exports the new optional symbol.
- The prepare breakdown is captured per prepared point-location handle at
  creation time. This is important because the native timing storage is
  thread-local; without per-handle capture, later prepare/run calls can make all
  locators report the same last prepare timing.

## Validation

Local:

```text
PYTHONPATH=src py -3 -m unittest \
  tests.goal5016_point_location_prepare_timing_test \
  tests.goal4913_planar_map_workspace_api_test

Ran 9 tests in 0.020s
OK
```

POD:

```text
python -m unittest tests.goal5016_point_location_prepare_timing_test

Ran 4 tests in 0.002s
OK
```

POD native build:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk-8.1
```

Important POD note: the default `/root/vendor/optix-dev/include` is OptiX 9.1
and produced `OPTIX_ERROR_UNSUPPORTED_ABI_VERSION` on this pod. Rebuilding with
`/root/vendor/optix-sdk-8.1` produced a runnable library. This is a POD
toolchain/header selection issue, not a point-location instrumentation result.

## POD Measurement

Artifact:

- `history/internal_docs/goal5016_prepare_timing_top4_fastpack_v2.json`
- `history/internal_docs/goal5016_prepare_timing_top4_fastpack_v2.log`

Command scope:

- top4 County x Zipcode representative input
- writer-free binary route
- fast-pack route, not the stopped device-resident-carrier track
- bounded exact LSI device columns
- point-location device face columns
- device-columnar reprojection/sort
- compiled CPU Numba carrier

Summary:

```text
writer_free_hot_sec: 3.6225s
LSI phase:           2.6806s
```

Point-location prepare/run phases:

| Phase | Total wrapper time | Native prepare_total | Segment count | Native traversal |
|---|---:|---:|---:|---:|
| map0 vertices in map1 | 3.3186s | 3.3180s | 9,982,960 | 0.0044s |
| map1 vertices in map0 | 0.4324s | 0.4321s | 1,705,027 | 0.0152s |
| midpoint map0 | 0.0041s run | reuses 3.3180s locator | 9,982,960 | 0.0010s |
| midpoint map1 | 0.0038s run | reuses 0.4321s locator | 1,705,027 | 0.0010s |

Large locator prepare breakdown, `map0_in_map1` / Zipcode base:

| Native prepare component | Seconds |
|---|---:|
| pipeline ensure | 0.5066 |
| host copy | 0.3370 |
| segment pack | 0.1092 |
| duplicate canonicalize | 1.2431 |
| device upload | 0.0571 |
| range build | 0.4980 |
| range upload | 0.0064 |
| accel build | 0.0616 |
| total | 3.3180 |

Small locator prepare breakdown, `map1_in_map0` / County base:

| Native prepare component | Seconds |
|---|---:|
| pipeline ensure | ~0.0000 |
| host copy | 0.0543 |
| segment pack | 0.0184 |
| duplicate canonicalize | 0.1762 |
| device upload | 0.0099 |
| range build | 0.0836 |
| range upload | 0.0011 |
| accel build | 0.0097 |
| total | 0.4321 |

## Interpretation

This proves the remaining point-location cost is not traversal. Traversal is
millisecond-level. The expensive part is preparing the directed-segment locator
workspace:

- duplicate half-edge canonicalization
- range/AABB construction
- host copy / segment packing
- one-time pipeline ensure on the first locator

The strongest actionable result is that the large base locator is reusable. In
a prepared-base + same-domain query-many regime, a fixed base should pay the
3.318s locator construction once, then reuse it across distinct query batches.
The query-specific locator still costs whatever its query map size demands.

## Claim Boundary

Authorized:

- The generic directed point-location native prepare path now exposes phase
  timings.
- The top4 run shows large base point-location prepare is dominated by
  workspace construction, not RT traversal.
- Reusing a prepared base locator is the correct next optimization target for a
  prepared-base query-many route.

Not authorized:

- No 10x claim yet.
- No author parity claim.
- No fresh one-shot speedup claim.
- No all-device-resident / true-zero-copy claim.
- No RayJoin-specific core primitive claim.

## Recommended Next Goal

Goal5017 should wire a prepared-base query-many measurement that explicitly
reuses the base point-location locator and reports:

- base locator prepare paid once
- per-query query-locator prepare cost
- per-query PIP traversal cost
- full binary operator cost per distinct same-domain query

Exit should be one of:

- `prepared_base_locator_reuse_moves_query_many_floor`
- `query_specific_locator_prepare_still_dominates`
- `prepared_locator_reuse_not_product_effective`
