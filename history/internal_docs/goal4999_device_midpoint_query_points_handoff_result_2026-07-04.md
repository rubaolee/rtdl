# Goal4999 Result: Device-Resident Midpoint Query-Point Handoff

Date: 2026-07-04

## Purpose

Goal4999 attacks the concrete host boundary that remained after Goal4998 in the
writer-free RayJoin Section 5.7 binary route:

```text
device LSI/sort columns
  -> midpoint query points generated through host packed scaled-point records
  -> native directed point-location / PIP
```

That boundary was wrong for the device-resident route. The midpoint query points
are numerical records derived from device columns, so they should be generated on
the GPU and handed directly to the generic directed point-location primitive.

## Implemented Change

### 1. Generic Native Directed Point-Location Device Query Input

Added a generic native query-point ABI:

```cpp
struct RtdlDirectedSegmentDeviceQueryPoint2D {
    float x;
    float y;
    uint32_t id;
    uint32_t has_scaled;
    int64_t sx;
    int64_t sy;
};
```

and exported:

```cpp
rtdl_optix_prepare_directed_segment_point_location_device_query_points_2d(...)
```

This is a directed point-location input API. It is not an overlay writer, not an
output-chain primitive, and not a RayJoin-specific native kernel.

### 2. Python Runtime Front Door

`PreparedOptixRayjoinCdbPointLocation2D` now has
`prepare_device_query_points(...)`, and the public
`PreparedOptixPlanarMapPointLocation2D` wrapper forwards the same method under
the planar-map point-location environment guard.

The prepared point wrapper keeps an owner reference so the device query-point
array remains alive while native point-location consumes it.

### 3. RayJoin App Device Midpoint Query Points

`section57_overlay_columnar_binary.py` now has a Numba CUDA midpoint query-point
kernel. In `--device-resident-carrier` mode, midpoint PIP no longer calls the
host packed scaled-point path. The route is now:

```text
device sorted LSI columns
  -> Numba CUDA generates midpoint query-point records on device
  -> generic directed point-location prepares those device records directly
  -> face-id device columns
  -> device scatter into midpoint face arrays
  -> device carrier and descriptor consumer
```

The app also has a dtype layout guard for the native ABI offsets and size.

## Generic-System Boundary

This change preserves the project boundary:

- The native addition is a generic directed point-location device-query input.
- The RayJoin app owns midpoint generation and overlay semantics.
- No `rayjoin_overlay` helper is imported.
- No RTDL core output-chain or RayJoin text writer primitive was added.
- The path is exercised through the existing public planar-map point-location
  wrapper.

## Verification

Local:

```text
py_compile section57_overlay_columnar_binary.py: passed
py_compile optix_runtime.py: passed
unittest tests.goal4999_device_query_point_location_handoff_test
         tests.goal4990_binary_repeat_protocol_test
         tests.goal4988_lsi_device_columns_direct_numba_handoff_test
result: 9 tests OK
```

POD:

```text
POD: root@157.157.221.29 -p 25248
repo: /root/rtdl_goal4988
native rebuild: make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk-8.1
exported symbol: rtdl_optix_prepare_directed_segment_point_location_device_query_points_2d
POD unittest result: 9 tests OK
```

The rebuild must pin `OPTIX_PREFIX=/root/vendor/optix-sdk-8.1`; the default
`/root/vendor/optix-dev` headers are OptiX 9.1 and fail this POD driver with
`Unsupported ABI version`.

## Top4 POD Result

Command:

```text
python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
  --left Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_county.cdb
  --right Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_zipcode.cdb
  --pair-name top4_county_zipcode
  --summary /root/rtdl_goal4999_device_query_midpoint_top4_repeat5.json
  --device-columnar
  --bounded-exact-lsi-device-columns
  --bounded-exact-lsi-capacity 1000000
  --point-location-device-face-columns
  --fast-scaled-point-pack
  --prepared-operator-session
  --device-resident-carrier
  --warmup-runs 1
  --repeat 5
```

Artifact copied to:

```text
history/internal_docs/goal4999_device_midpoint_query_points_artifacts_2026-07-04/device_query_midpoint_top4_repeat5.json
```

Result:

| Metric | Value |
|---|---:|
| LSI rows | 428,322 |
| Descriptor pairs | 15,014 |
| Best writer-free hot sec | 0.3266657907515764 |
| Median writer-free hot sec | 0.3295415733009577 |
| Worst writer-free hot sec | 0.3492758944630623 |
| Median downstream floor sec | 0.3297787792980671 |
| Median LSI phase sec | 0.0030824393033981323 |

Compared with Goal4998 `--device-resident-carrier`:

| Route | Best | Median |
|---|---:|---:|
| Goal4998 device carrier | 0.3312861304730177 | 0.338140819221735 |
| Goal4999 device midpoint query points | 0.3266657907515764 | 0.3295415733009577 |

Median improvement: `1.026x`.

## Boundary Removed

The measured route now records:

```text
midpoint_points_map0_device_query_points_sec ~= 0.0015s
midpoint_points_map1_device_query_points_sec ~= 0.0017s
midpoint_points_map0_prepare_device_query_points_sec ~= 0.00007s
midpoint_points_map1_prepare_device_query_points_sec ~= 0.00026s
```

This replaces the previous host packed scaled-point midpoint query route in
`--device-resident-carrier` mode. The midpoint query points are generated as
device records and consumed by native point-location directly.

## Remaining Performance Floor

After this fix, the top prepared/query-many writer-free floor is no longer
dominated by midpoint query-point packing. The visible remaining phases are:

```text
sort_map0_device_columnar_sec        ~0.033s
sort_map1_device_columnar_sec        ~0.124s
device_resident_carrier_construction ~0.087s
descriptor_pair_count_consumer       ~0.041s
vertex PIP total                     ~0.030s
```

Those are separate ordering/carrier/consumer costs. Goal4999 closes the midpoint
query-point host packing boundary; it does not claim author parity or a fresh
one-shot result.

## Exit Label

`completed_device_midpoint_query_point_handoff__host_scaled_point_pack_removed`
