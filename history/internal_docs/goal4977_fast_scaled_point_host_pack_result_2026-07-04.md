# Goal4977 Result: Fast Scaled-Point Host Pack Route

Date: 2026-07-04

## Verdict Requested

`completed_fast_scaled_point_pack_moves_midpoint_floor`

## Summary

Goal4977 implemented a fast host-side pack route for `RtdlRayjoinCdbScaledPoint`.

This is a narrow but real performance fix. Goal4976 showed that midpoint query-point generation was not math-bound; it was dominated by per-row Python/ctypes packing into the existing scaled-point ABI. Goal4977 keeps the same ABI and replaces per-row object construction with a NumPy structured-array owner plus a ctypes view.

This is not a zero-copy or device-resident prepared-points route. It is a safer first fix for the host packing boundary exposed by Goal4976.

## Code Changes

Changed:

- `src/rtdsl/embree_runtime.py`
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal4977_fast_scaled_point_pack_test.py`

New public/internal helper:

```python
pack_rayjoin_cdb_scaled_points_fast_host(ids=..., x=..., y=..., sx=..., sy=...)
```

The helper:

- preserves the existing `RtdlRayjoinCdbScaledPoint` ctypes ABI
- uses a NumPy structured array as the owner
- exposes a ctypes view over that same buffer
- validates itemsize and every field offset against the ctypes structure
- rejects ids outside `uint32`

The paper-reproduction app now has:

```text
--fast-scaled-point-pack
```

Its claim boundary explicitly says:

- `fast_scaled_point_pack_scope = vectorized_host_pack_same_scaled_point_abi`
- `fast_scaled_point_pack_device_resident_claim_authorized = false`

## Local Validation

Commands:

```text
py -m py_compile src/rtdsl/embree_runtime.py Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
$env:PYTHONPATH='src'; py -m unittest tests.goal4977_fast_scaled_point_pack_test tests.goal4974_point_location_device_face_columns_route_test
```

Result:

```text
Ran 6 tests in 0.012s
OK
```

## POD Evidence

POD:

- `root@213.173.108.6 -p 10626`

Input:

- left: `Paper-reproduction-apps/rayjoin-paper/_data/goal4971_top4_arcgis/top4_county.cdb`
- right: `Paper-reproduction-apps/rayjoin-paper/_data/goal4971_top4_arcgis/top4_zipcode.cdb`

Route:

```text
--device-columnar
--compiled-group
--bounded-exact-lsi-device-columns --bounded-exact-lsi-capacity 600000
--point-location-device-face-columns
--fast-scaled-point-pack
```

Artifact:

- `history/internal_docs/goal4977_fast_scaled_point_host_pack_artifacts_2026-07-04/fast_pack_summary.json`

## Performance Delta vs Goal4976

| Metric | Goal4976 baseline | Goal4977 fast pack | Delta | Speedup |
|---|---:|---:|---:|---:|
| writer-free hot | 5.373426s | 4.219930s | -1.153496s | 1.273x |
| downstream floor | 2.671954s | 1.478150s | -1.193804s | 1.808x |
| midpoint map0 total | 0.698236s | 0.017627s | -0.680609s | 39.611x |
| midpoint map0 pack | 0.683992s | 0.003442s | -0.680550s | 198.717x |
| midpoint map1 total | 0.614120s | 0.011730s | -0.602391s | 52.357x |
| midpoint map1 pack | 0.606735s | 0.003427s | -0.603308s | 177.044x |

The pack boundary identified by Goal4976 was removed almost completely:

```text
pack_scaled_points map0: 0.683992s -> 0.003442s
pack_scaled_points map1: 0.606735s -> 0.003427s
```

This moved the writer-free hot route by about 1.15s and the downstream floor by about 1.19s.

## Correctness / Structural Consistency

Compared with the Goal4976 baseline, the following fields match exactly:

- `lsi_row_count`
- `xsect_sorted_counts`
- `vertex_positive_counts`
- `grouped_carrier`
- `downstream_consumer`
- `scale_bounds`

The route still reports:

- `lsi_row_count = 428322`
- `xsect_sorted_counts.side0 = 428322`
- `xsect_sorted_counts.side1 = 428322`
- `vertex_positive_counts.side0_in_side1 = 812721`
- `vertex_positive_counts.side1_in_side0 = 4527305`

The fast pack changes the host construction method for scaled query points. It does not change point-location semantics, LSI semantics, grouping semantics, or the app-level numeric route contract.

## Remaining Cost After Goal4977

After this fix, the largest measured downstream components are no longer midpoint pack:

| Remaining component | Time |
|---|---:|
| grouped compiled columnar carrier construction | 0.664343s |
| vertex PIP map1-in-map0 | 0.328811s |
| intersection reprojection device-columnar | 0.237396s |
| sort map1 device-columnar | 0.095491s |
| vertex PIP map0-in-map1 | 0.058887s |
| sort map0 device-columnar | 0.038731s |

The next bottleneck is therefore not midpoint math or scaled-point pack. The largest remaining downstream component is carrier construction / grouped output descriptor construction, followed by one vertex-PIP phase and reprojection/sort.

## Claim Boundary

Authorized:

- The fast host pack route materially reduces the midpoint query-point packing floor on the top4 representative binary route.
- The implementation preserves the existing scaled-point ABI and passes local ABI/parity tests.
- This is a useful host-boundary optimization for the current RayJoin paper-reproduction app route.

Not authorized:

- No zero-copy claim.
- No true device-resident prepared-point claim.
- No author-performance headline.
- No claim that Layer 1/2 is complete.
- No claim that this closes the remaining overlay compute gap.

## Interpretation

This was the correct low-risk first fix after Goal4976. The issue was not midpoint arithmetic; it was the per-row Python/ctypes pack boundary. A vectorized structured-array pack removes that cost without changing native semantics.

However, this is still a host pack. The deeper product direction remains a generic device/columnar prepared-points or point-location input path if we want true device-resident overlay execution.

## Exit Label

`completed_fast_scaled_point_pack_moves_midpoint_floor`
